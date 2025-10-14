import uuid
from neo4j import GraphDatabase


class TNode:
    def __init__(self, id, uri, description, title, arcs=None):
        self.id = id
        self.uri = uri
        self.description = description
        self.title = title
        self.arcs = arcs or []

    def to_dict(self):
        return {
            'id': self.id,
            'uri': self.uri,
            'description': self.description,
            'title': self.title,
            'arcs': [arc.to_dict() for arc in self.arcs] if self.arcs else []
        }
    

class TArc:
    def __init__(self, id, uri, node_uri_from, node_uri_to):
        self.id = id
        self.uri = uri
        self.node_uri_from = node_uri_from
        self.node_uri_to = node_uri_to
    
    def to_dict(self):
        return {
            'id': self.id,
            'uri': self.uri,
            'node_uri_from': self.node_uri_from,
            'node_uri_to': self.node_uri_to
        }
    

class neo4jHandler:    
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_all_nodes(self):
        query = '''
        MATCH (n)
        RETURN n
        '''
        with self.driver.session() as session:
            result = session.run(query)
            nodes = [self.collect_node(record['n']) for record in result]
            return [node.to_dict() for node in nodes]

    def get_all_nodes_and_arcs(self):
        query = '''
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        '''
        with self.driver.session() as session:
            result = session.run(query)
            nodes = {}
            for record in result:
                node_from = self.collect_node(record['n'])
                node_to = self.collect_node(record['m'])
                arc = self.collect_arc(record['r'])

                if node_from.uri not in nodes:
                    nodes[node_from.uri] = node_from
                if node_to.uri not in nodes:
                    nodes[node_to.uri] = node_to

                nodes[node_from.uri].arcs.append(arc)
            
            return [node.to_dict() for node in nodes.values()]
    
    def get_nodes_by_labels(self, labels):
        if not labels:
            return []
        
        labels_str = ':'.join(labels)
        query = f'''
        MATCH (n:{labels_str})
        RETURN n
        '''
        with self.driver.session() as session:
            result = session.run(query)
            nodes = [self.collect_node(record['n']) for record in result]
            return [node.to_dict() for node in nodes]
    
    def get_node_by_uri(self, uri):
        query = '''
        MATCH (n {uri: $uri})
        RETURN n
        '''
        with self.driver.session() as session:
            result = session.run(query, uri=uri)
            record = result.single()
            if record:
                return self.collect_node(record['n']).to_dict()
            return None
    
    def create_node(self, params):
        if 'uri' not in params:
            params['uri'] = self.generate_random_string()

        query = 'CREATE (n) SET n = $props RETURN n'
        with self.driver.session() as session:
            result = session.run(query, props=params)
            record = result.single()            
            if record:
                node = record['n']
                return self.collect_node(node).to_dict()
            return None
    
    def create_arc(self, node1_uri, node2_uri, arc_type='RELATED'):
        arc_uri = self.generate_random_string()
        query = f'''
        MATCH (a {{uri: $uri1}}), (b {{uri: $uri2}})
        CREATE (a)-[r:{arc_type} ]->(b)
        SET r.uri = $arc_uri
        RETURN r
        '''        
        with self.driver.session() as session:
            result = session.run(query, uri1=node1_uri, uri2=node2_uri, arc_uri=arc_uri)
            record = result.single()
            if record:
                return self.collect_arc(record['r']).to_dict()
            return None

    
    def delete_node_by_uri(self, uri):
        query = '''
        MATCH (n {uri: $uri})
        WITH n, elementId(n) AS nid, properties(n) AS props
        DETACH DELETE n
        RETURN nid, props
        '''
        with self.driver.session() as session:
            record = session.run(query, uri=uri).single()
            if record:
                data = dict(record['props'])
                data['id'] = record['nid']
                return data
            return None

    
    def delete_arc_by_id(self, arc_id):
        query = '''
        MATCH ()-[r]->()
        WHERE elementId(r) = $arc_id
        WITH r, elementId(r) AS rid, properties(r) AS props
        DELETE r
        RETURN rid, props
        '''
        with self.driver.session() as session:
            record = session.run(query, arc_id=arc_id).single()
            if record:
                data = dict(record['props'])
                data['id'] = record['rid']
                return data
            return None
    
    def update_node(self, uri, params):
        if not params:
            return None
        
        query = '''
        MATCH (n {uri: $uri})
        SET n += $props
        RETURN n
        '''
        with self.driver.session() as session:
            result = session.run(query, uri=uri, props=params)
            record = result.single()
            if record:
                return self.collect_node(record['n']).to_dict()
            return None
    
    def run_custom_query(self, query, params=None):
        with self.driver.session() as session:
            result = session.run(query, **(params or {}))
            return [dict(record) for record in result]
    
    def collect_node(self, node):
        properties = dict(node)
        return TNode(
            id=node.element_id,
            uri=properties.get('uri', ''),
            description=properties.get('description', ''),
            title=properties.get('title', '')
        )

    def collect_arc(self, arc):
        properties = dict(arc)
        start_node = arc.start_node
        end_node = arc.end_node
        return TArc(
            id=arc.element_id,
            uri=properties.get('uri', ''),
            node_uri_from=start_node.get('uri', ''),
            node_uri_to=end_node.get('uri', '')
        )
    
    def generate_random_string(self):
        return str(uuid.uuid4())