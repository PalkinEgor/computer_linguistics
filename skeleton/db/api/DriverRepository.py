from django.conf import settings
from db.api.external.neo4jHandler import neo4jHandler

class DriverRepository:

    def __init__(self, uri=None, user=None, password=None):
        uri = uri or getattr(settings, "NEO4J_URI", "bolt://localhost:7687")
        user = user or getattr(settings, "NEO4J_USER", "neo4j")
        password = password or getattr(settings, "NEO4J_PASSWORD", "password")
        self.handler = neo4jHandler(uri, user, password)

    def close(self):
        self.handler.close()

    def get_all_nodes(self):
        return self.handler.get_all_nodes()

    def get_all_nodes_and_arcs(self):
        return self.handler.get_all_nodes_and_arcs()

    def get_nodes_by_labels(self, labels):
        return self.handler.get_nodes_by_labels(labels)

    def get_node_by_uri(self, uri):
        return self.handler.get_node_by_uri(uri)

    def create_node(self, params):
        return self.handler.create_node(params)

    def create_arc(self, n1, n2, arc_type='RELATED'):
        return self.handler.create_arc(n1, n2, arc_type)

    def delete_node_by_uri(self, uri):
        return self.handler.delete_node_by_uri(uri)

    def delete_arc_by_id(self, arc_id):
        return self.handler.delete_arc_by_id(arc_id)

    def update_node(self, uri, params):
        return self.handler.update_node(uri, params)

    def run_custom_query(self, query, params=None):
        return self.handler.run_custom_query(query, params)

    def generate_random_string(self):
        return self.handler.generate_random_string()