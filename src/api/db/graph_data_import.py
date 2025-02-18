import os
import yaml
import json
from neo4j import GraphDatabase
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

def load_yaml_files(folder_name, label):
    """Reads and updates YAML files before inserting into Neo4j."""
    folder_path = os.path.join(DATABASE_PATH, folder_name)

    if not os.path.exists(folder_path):
        print(f"⚠️ Folder {folder_path} does not exist!")
        return
    
    print(f"📂 Scanning for YAML files in: {folder_path}")

    for filename in os.listdir(folder_path):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "r") as file:
                try:
                    data = yaml.safe_load(file)
                    update_yaml_versions(data, file_path, label)
                except yaml.YAMLError as e:
                    print(f"❌ Error reading {filename}: {e}")

def update_yaml_versions(data, file_path, label):
    """Assigns version, previous_version, and next_version before inserting into Neo4j."""
    node_id = data.get("id")
    created_at = data.get("created_at", datetime.utcnow().isoformat())

    with driver.session() as session:
        # 🔹 Get the latest version for this ID
        latest_version_record = session.run(
            f"""
            MATCH (n:{label})
            WHERE n.id = $id
            RETURN MAX(toInteger(n.version)) AS latest_version;
            """,
            id=node_id
        ).single()

        latest_version = latest_version_record["latest_version"] if latest_version_record and latest_version_record["latest_version"] else 0
        version = str(latest_version + 1)  # Increment version properly

        # 🔹 Find previous version
        previous_record = session.run(
            f"""
            MATCH (n:{label})
            WHERE n.id = $id AND datetime(n.created_at) < datetime($created_at)
            RETURN n.id ORDER BY datetime(n.created_at) DESC LIMIT 1;
            """,
            id=node_id, created_at=created_at
        ).single()
        previous_version = previous_record["n.id"] if previous_record else None

        # 🔹 Find next version
        next_record = session.run(
            f"""
            MATCH (n:{label})
            WHERE n.id = $id AND datetime(n.created_at) > datetime($created_at)
            RETURN n.id ORDER BY datetime(n.created_at) ASC LIMIT 1;
            """,
            id=node_id, created_at=created_at
        ).single()
        next_version = next_record["n.id"] if next_record else None

    # 🔹 Update the YAML file with the new version info
    data["version"] = version
    data["previous_version"] = previous_version
    data["next_version"] = next_version

    with open(file_path, "w") as file:
        yaml.dump(data, file)

    print(f"✅ Updated {label} in YAML: {file_path} (Version {version})")

    # Insert into Neo4j
    insert_into_neo4j(data, label)

def insert_into_neo4j(data, label):
    """Inserts or updates nodes in Neo4j with versioning."""
    with driver.session() as session:
        session.run(
            f"""
            MERGE (n:{label} {{id: $id}})
            SET n.name = $name, 
                n.description = $description, 
                n.version = $version, 
                n.created_at = $created_at, 
                n.previous_version = $previous_version,
                n.next_version = $next_version
            """,
            id=data["id"],
            name=data.get("name", "Untitled"),
            description=data.get("description", "No Description"),
            version=data["version"],
            created_at=data["created_at"],
            previous_version=data["previous_version"],
            next_version=data["next_version"]
        )

def link_versions():
    """Links different versions using `previous_version` and `next_version` in Neo4j."""
    with driver.session() as session:
        print("🔗 Linking previous and next versions...")

        # 🔹 Link previous versions
        result = session.run(
            """
            MATCH (old:Topic), (new:Topic)
            WHERE new.previous_version = old.id
            MERGE (old)-[:PREVIOUS_VERSION]->(new)
            RETURN COUNT(*);
            """
        ).single()
        prev_links = result[0] if result and result[0] else 0
        print(f"✅ {prev_links} Previous Version links created.")

        # 🔹 Link next versions
        result = session.run(
            """
            MATCH (old:Topic), (new:Topic)
            WHERE old.next_version = new.id
            MERGE (old)-[:NEXT_VERSION]->(new)
            RETURN COUNT(*);
            """
        ).single()
        next_links = result[0] if result and result[0] else 0
        print(f"✅ {next_links} Next Version links created.")

    print("✅ Version linking complete.")

if __name__ == "__main__":
    print(f"🔍 Using Database Path: {DATABASE_PATH}")
    
    # Load and process topics and projects
    load_yaml_files("topics", "Topic")
    load_yaml_files("projects", "Project")

    # Link different versions using `previous_version` and `next_version`
    link_versions()

    print("✅ Import complete.")
