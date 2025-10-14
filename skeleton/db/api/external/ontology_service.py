from skeleton.db.api.external.neo4jHandler import neo4jHandler

class OntologyService:
    def __init__(self, handler):
        self.db = handler

    def get_ontology(self):
        return self.db.get_all_nodes_and_arcs()
    
    def get_ontology_parent_classes(self):
        query = '''
        MATCH (c:Class)
        WHERE NOT (c)-[:subClassOf]->(:Class)
        RETURN c
        '''
        return [self.db.collect_node(r['c']).to_dict() for r in self.db.run_custom_query(query)]

    def get_class(self, uri):
        return self.db.get_node_by_uri(uri)
    
    def get_class_parents(self, uri: str):
        query = '''
        MATCH (c:Class {uri: $uri})-[:subClassOf]->(p:Class)
        RETURN p
        '''
        return [self.db.collect_node(r['p']).to_dict() for r in self.db.run_custom_query(query, {'uri': uri})]
    
    def get_class_children(self, uri):
        query = '''
        MATCH (p:Class {uri: $uri})<-[:subClassOf]-(c:Class)
        RETURN c
        '''
        return [self.db.collect_node(r['c']).to_dict() for r in self.db.run_custom_query(query, {'uri': uri})]
    
    def get_class_objects(self, uri):
        query = '''
        MATCH (o:Object)-[:`rdf:type`]->(c:Class {uri: $uri})
        RETURN o
        '''
        return [self.db.collect_node(r['o']).to_dict() for r in self.db.run_custom_query(query, {'uri': uri})]
    
    def update_class(self, uri, title=None, description=None):
        params = {}
        if title:
            params['title'] = title
        if description:
            params['description'] = description
        return self.db.update_node(uri, params)

    def create_class(self, title, description="", parent_uri=None):
        node = self.db.create_node({
            "title": title,
            "description": description,
            "uri": self.db.generate_random_string(),
        })

        query = '''
        MATCH (n {uri: $uri})
        SET n:Class
        RETURN n
        '''
        self.db.run_custom_query(query, {"uri": node['uri']})

        if parent_uri:
            self.db.create_arc(node['uri'], parent_uri, 'subClassOf')

        return node
    
    def delete_class(self, uri):
        query = '''
        MATCH (c:Class {uri: $uri})
        OPTIONAL MATCH (child:Class)-[:subClassOf*]->(c)
        WITH collect(child) + collect(c) AS toDelete
        UNWIND toDelete AS x
        OPTIONAL MATCH (x)<-[:`rdf:type`]-(o:Object)
        DETACH DELETE x, o
        '''
        self.db.run_custom_query(query, {"uri": uri})

    def add_class_attribute(self, class_uri, title):
        prop = self.db.create_node({
            "uri": self.db.generate_random_string(),
            "title": title
        })
        query = '''
        MATCH (p {uri: $uri_p}), (c:Class {uri: $uri_c})
        SET p:DatatypeProperty
        CREATE (p)-[:domain]->(c)
        '''
        self.db.run_custom_query(query, {"uri_p": prop['uri'], "uri_c": class_uri})
        return prop

    def delete_class_attribute(self, property_uri):
        query = '''
        MATCH (p:DatatypeProperty {uri: $uri})
        DETACH DELETE p
        '''
        self.db.run_custom_query(query, {"uri": property_uri})

    def add_class_object_attribute(self, class_uri, attr_name, range_class_uri):
        prop = self.db.create_node({
            "uri": self.db.generate_random_string(),
            "title": attr_name
        })
        query = '''
        MATCH (p {uri: $uri_p}), (domain:Class {uri: $uri_c}), (range:Class {uri: $uri_r})
        SET p:ObjectProperty
        CREATE (p)-[:domain]->(domain)
        CREATE (p)-[:range]->(range)
        '''
        self.db.run_custom_query(query, {
            "uri_p": prop['uri'],
            "uri_c": class_uri,
            "uri_r": range_class_uri
        })
        return prop
    
    def delete_class_object_attribute(self, object_property_uri):
        query = '''
        MATCH (p:ObjectProperty {uri: $uri})
        DETACH DELETE p
        '''
        self.db.run_custom_query(query, {"uri": object_property_uri})
    
    def add_class_parent(self, parent_uri, target_uri):
        self.db.create_arc(target_uri, parent_uri, "subClassOf")
    
    def get_object(self, uri):
        return self.db.get_node_by_uri(uri)

    def delete_object(self, uri):
        return self.db.delete_node_by_uri(uri)
    
    def collect_signature(self, class_uri):
        query = '''
        MATCH (c:Class {uri: $uri})
        OPTIONAL MATCH (p:DatatypeProperty)-[:domain]->(c)
        OPTIONAL MATCH (o:ObjectProperty)-[:domain]->(c)
        RETURN collect(DISTINCT p) AS datatype_props,
               collect(DISTINCT o) AS object_props
        '''
        record = self.db.run_custom_query(query, {"uri": class_uri})[0]
        datatype_props = [self.db.collect_node(p).to_dict() for p in record['datatype_props'] if p]
        object_props = [self.db.collect_node(o).to_dict() for o in record['object_props'] if o]
        return {"datatype": datatype_props, "object": object_props}
    
    def create_object(self, class_uri, title, description):
        obj = self.db.create_node({
            "uri": self.db.generate_random_string(),
            "title": title,
            "description": description
        })
        query = '''
        MATCH (o {uri: $obj_uri}), (c:Class {uri: $class_uri})
        SET o:Object
        CREATE (o)-[:`rdf:type`]->(c)
        '''
        self.db.run_custom_query(query, {"obj_uri": obj['uri'], "class_uri": class_uri})

    def update_object(self, uri, title=None, description=None):
        params = {}
        if title:
            params['title'] = title
        if description:
            params['description'] = description
        return self.db.update_node(uri, params)