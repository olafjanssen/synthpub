import os
import yaml
import json
from neo4j import GraphDatabase
from pathlib import Path
from datetime import datetime

SETTINGS_FILE = "settings.yaml"

# Load database settings
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

# Get the database path dynamically
settings = load_settings()
DATABASE_PATH = settings.get("db_path", "/Users/arsl/Documents/db").strip()

# Neo4j Connection
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "securepassword123"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Function to handle datetime serialization
def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def load_yaml_files(folder_name, label):
    """Reads YAML files from the selected database folder."""
    if not os.path.exists(DATABASE_PATH):
        print(f"⚠️ Database path does not exist: {DATABASE_PATH}")
        return
    
    print(f"📂 Scanning for files in: {DATABASE_PATH}")

    files_found = False
    for subdir, dirs, files in os.walk(DATABASE_PATH):
        for filename in files:
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                files_found = True
                file_path = os.path.join(subdir, filename)
                print(f"📂 Found YAML file: {file_path}")  # Debugging output
                
                # Read YAML file
                with open(file_path, "r") as file:
                    try:
                        data = yaml.safe_load(file)
                        
                        # Convert datetime objects to string before printing
                        print(f"📜 Contents of {filename}: {json.dumps(data, indent=2, default=serialize_datetime)}")  
                        
                        # Determine label type (Topic or Project)
                        label = "Project" if "title" in data and "id" in data else "Topic"
                        
                        # ✅ Ensure `filename` is passed when calling `create_graph_nodes()`
                        create_graph_nodes(data, label, filename)

                    except yaml.YAMLError as e:
                        print(f"❌ Error reading {filename}: {e}")

    if not files_found:
        print("❌ No YAML files found in the directory.")


def create_graph_nodes(data, label, filename):
    """Creates nodes in Neo4j and dynamically assigns previous and next versions."""
    node_id = data.get("id")
    created_at = data.get("created_at", datetime.utcnow().isoformat())  # Ensure created_at exists
    
    # Assign a default version if missing
    version = str(data.get("version", "1"))  # Default to "1" if missing
    
    previous_version = None
    next_version = None

    with driver.session() as session:
        # Find the previous version (earlier created_at)
        previous_record = session.run(
            """
            MATCH (t:Topic)
            WHERE t.id = $id AND datetime(t.created_at) < datetime($created_at)
            RETURN t.id ORDER BY datetime(t.created_at) DESC LIMIT 1;
            """,
            id=node_id, created_at=created_at
        ).single()
        
        if previous_record:
            previous_version = previous_record["t.id"]

        # Find the next version (later created_at)
        next_record = session.run(
            """
            MATCH (t:Topic)
            WHERE t.id = $id AND datetime(t.created_at) > datetime($created_at)
            RETURN t.id ORDER BY datetime(t.created_at) ASC LIMIT 1;
            """,
            id=node_id, created_at=created_at
        ).single()
        
        if next_record:
            next_version = next_record["t.id"]

    print(f"🛠️ Processing {label}: {node_id} (Version: {version}, Prev: {previous_version}, Next: {next_version})")

    with driver.session() as session:
        if label == "Topic":
            print(f"📂 Creating Topic Node: {node_id} (Version: {version}, Previous: {previous_version}, Next: {next_version})")
            session.run(
                """
                MERGE (t:Topic {id: $id})
                ON CREATE SET t.name = $name, 
                              t.description = $description, 
                              t.version = $version, 
                              t.created_at = $created_at, 
                              t.previous_version = $previous_version,
                              t.next_version = $next_version
                """,
                id=node_id, version=version,
                name=data.get("name", "Untitled Topic"),
                description=data.get("description", "No Description"),
                created_at=created_at,
                previous_version=previous_version,
                next_version=next_version
            )


def load_markdown_files():
    """Reads Markdown files from the articles folder."""
    articles_path = os.path.join(DATABASE_PATH, "articles")
    if not os.path.exists(articles_path):
        print(f"⚠️ Folder 'articles' not found at {DATABASE_PATH}")
        return

    print(f"📂 Loading Markdown articles from: {articles_path}")

    for filename in os.listdir(articles_path):
        if filename.endswith(".md"):
            file_path = os.path.join(articles_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                create_article_node(filename, content)

def create_article_node(filename, content):
    """Creates an Article node in Neo4j."""
    article_id = filename.replace(".md", "")

    with driver.session() as session:
        session.run(
            """
            MERGE (a:Article {id: $id})
            ON CREATE SET a.content = $content, a.created_at = timestamp()
            """,
            id=article_id, content=content
        )

def link_versions():
    """Links different versions of Topics and Projects using `previous_version` and `next_version`."""
    with driver.session() as session:
        print("🔗 Linking previous and next versions...")

        # 🔹 Link previous versions of Topics
        result = session.run(
            """
            MATCH (old:Topic), (new:Topic)
            WHERE new.previous_version = old.id
            MERGE (old)-[:PREVIOUS_VERSION]->(new)
            RETURN old.id AS old_id, new.id AS new_id, old.version AS old_version, new.version AS new_version
            """
        )
        for record in result:
            print(f"✅ Linked Topic Versions: {record['old_id']} → {record['new_id']} (v{record['old_version']} → v{record['new_version']})")

        # 🔹 Link next versions of Topics
        result = session.run(
            """
            MATCH (old:Topic), (new:Topic)
            WHERE old.next_version = new.id
            MERGE (old)-[:NEXT_VERSION]->(new)
            RETURN old.id AS old_id, new.id AS new_id, old.version AS old_version, new.version AS new_version
            """
        )
        for record in result:
            print(f"✅ Linked Topic Next Versions: {record['old_id']} → {record['new_id']} (v{record['old_version']} → v{record['new_version']})")

        # 🔹 Link previous versions of Projects
        result = session.run(
            """
            MATCH (old:Project), (new:Project)
            WHERE new.previous_version = old.id
            MERGE (old)-[:PREVIOUS_VERSION]->(new)
            RETURN old.id AS old_id, new.id AS new_id, old.version AS old_version, new.version AS new_version
            """
        )
        for record in result:
            print(f"✅ Linked Project Versions: {record['old_id']} → {record['new_id']} (v{record['old_version']} → v{record['new_version']})")

        # 🔹 Link next versions of Projects
        result = session.run(
            """
            MATCH (old:Project), (new:Project)
            WHERE old.next_version = new.id
            MERGE (old)-[:NEXT_VERSION]->(new)
            RETURN old.id AS old_id, new.id AS new_id, old.version AS old_version, new.version AS new_version
            """
        )
        for record in result:
            print(f"✅ Linked Project Next Versions: {record['old_id']} → {record['new_id']} (v{record['old_version']} → v{record['new_version']})")

    print("✅ Version linking complete.")


if __name__ == "__main__":
    print(f"🔍 Using Database Path: {DATABASE_PATH}")
    
    # Load topics and projects
    load_yaml_files("topics", "Topic")
    load_yaml_files("projects", "Project")

    # Load articles
    load_markdown_files()

    # Link different versions using `previous_version` and `next_version`
    link_versions()

    print("✅ Import complete.")
