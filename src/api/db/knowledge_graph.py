from neo4j import GraphDatabase
import os

# Get environment variables for security
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class KnowledgeGraph:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def create_document(self, doc_id, title, topic_id):
        """Add a document and link it to a topic."""
        query = """
        MERGE (d:Document {id: $doc_id})
        SET d.title = $title
        MERGE (t:Topic {id: $topic_id})
        MERGE (d)-[:HAS_TOPIC]->(t)
        """
        with self.driver.session() as session:
            session.run(query, doc_id=doc_id, title=title, topic_id=topic_id)

    def get_documents_by_topic(self, topic_id):
        """Retrieve all documents related to a topic."""
        query = """
        MATCH (d:Document)-[:HAS_TOPIC]->(t:Topic {id: $topic_id})
        RETURN d.id AS doc_id, d.title AS title
        """
        with self.driver.session() as session:
            results = session.run(query, topic_id=topic_id)
            return [{"id": record["doc_id"], "title": record["title"]} for record in results]

# Singleton instance of the knowledge graph
knowledge_graph = KnowledgeGraph()
