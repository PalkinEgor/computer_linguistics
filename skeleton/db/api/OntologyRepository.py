from db.api.DriverRepository import DriverRepository
from db.api.external.ontology_service import OntologyService


class OntologyRepository:
    def __init__(self, uri=None, user=None, password=None):
        self.driver_repo = DriverRepository(uri=uri, user=user, password=password)
        self.service = OntologyService(self.driver_repo.handler)

    def close(self):
        self.driver_repo.close()

    def get_ontology(self):
        return self.service.get_ontology()

    def get_class(self, uri):
        return self.service.get_class(uri)

    def create_class(self, title, description="", parent_uri=None):
        return self.service.create_class(title, description, parent_uri)

    def update_class(self, uri, title=None, description=None):
        return self.service.update_class(uri, title, description)

    def delete_class(self, uri):
        return self.service.delete_class(uri)

    def get_class_parents(self, uri):
        return self.service.get_class_parents(uri)

    def get_class_children(self, uri):
        return self.service.get_class_children(uri)

    def get_class_objects(self, uri):
        return self.service.get_class_objects(uri)

    def add_class_attribute(self, class_uri, title):
        return self.service.add_class_attribute(class_uri, title)

    def delete_class_attribute(self, property_uri):
        return self.service.delete_class_attribute(property_uri)