# api/db/version_graph.py

import networkx as nx
from datetime import datetime
from typing import Optional, List, Dict

class ArticleVersionGraph:
    def __init__(self):
        # Initialize a directed graph to represent version history
        self.graph = nx.DiGraph()

    def add_version(
        self,
        article_id: str,
        version_id: str,
        content: str,
        timestamp: datetime,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        metadata = metadata or {}
        metadata.update({
            "article_id": article_id,
            "version_id": version_id,
            "content": content,
            "timestamp": timestamp.isoformat()
        })
        self.graph.add_node(version_id, **metadata)

    def link_version(self, new_version_id: str, previous_version_id: str) -> None:
        self.graph.add_edge(new_version_id, previous_version_id, relation="UPDATED_FROM")

    def get_latest_version(self, article_id: str) -> Optional[Dict]:
        nodes = [
            n for n, attr in self.graph.nodes(data=True)
            if attr.get("article_id") == article_id
        ]
        if not nodes:
            return None
        latest_node = max(nodes, key=lambda n: datetime.fromisoformat(self.graph.nodes[n]["timestamp"]))
        return self.graph.nodes[latest_node]

    def get_version_chain(self, article_id: str) -> List[Dict]:
        nodes = [
            n for n, attr in self.graph.nodes(data=True)
            if attr.get("article_id") == article_id
        ]
        sorted_nodes = sorted(nodes, key=lambda n: datetime.fromisoformat(self.graph.nodes[n]["timestamp"]))
        return [self.graph.nodes[n] for n in sorted_nodes]
