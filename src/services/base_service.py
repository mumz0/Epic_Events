"""
This module defines the BaseService class which provides basic services for interacting with database models.
"""

from src.repositories.base_repository import BaseRepository
from src.repositories.permission_repository import PermissionRepository
from src.repositories.role_repository import RoleRepository


class BaseService:
    """
    This class provides basic services for interacting with database models.

    :param model: The database model associated with this service.
    :type model: object
    :param repository: The repository associated with this service.
    :type repository: BaseRepository
    """

    def __init__(self, model=None, repository=None):
        self.model = model
        self.repository = repository or BaseRepository(model)

    def create_instance(self, data):
        """
        Creates an instance of the model without persisting it to the database.

        :param data: The data to initialize the model instance.
        :type data: dict
        :return: The instance of the model.
        :rtype: object
        """
        return self.model(**data)

    def create(self, data, session):
        """
        Creates and persists an instance of the model with the given data.

        :param data: The data to initialize the model instance.
        :type data: dict
        :param session: The database session.
        :type session: Session
        :return: The persisted instance of the model.
        :rtype: object
        """
        instance = self.model(**data)
        return self.repository.add(instance, session)

    def create_all(self, data_list, session):
        """
        Creates and persists multiple instances of the model with the given data list.

        :param data_list: A list of data dictionaries to initialize the model instances.
        :type data_list: list
        :param session: The database session.
        :type session: Session
        :return: A list of persisted instances of the model.
        :rtype: list
        """
        instances = [self.model(**data) for data in data_list]
        return self.repository.add_all(instances, session)

    def get(self, instance_id, session):
        """
        Retrieves an instance of the model by its ID.

        :param instance_id: The ID of the model instance.
        :type instance_id: int
        :param session: The database session.
        :type session: Session
        :return: The instance of the model if found, otherwise None.
        :rtype: object or None
        """
        return self.repository.get(instance_id, session)

    def get_id(self, instance_name, session):
        """
        Retrieves an instance of the model by its name.

        :param instance_name: The name of the model instance.
        :type instance_name: str
        :param session: The database session.
        :type session: Session
        :return: The instance of the model if found, otherwise None.
        :rtype: object or None
        """
        return self.repository.get_id(instance_name, session)

    def get_all(self, session):
        """
        Retrieves all instances of the model.

        :param session: The database session.
        :type session: Session
        :return: A list of all instances of the model.
        :rtype: list
        """
        if isinstance(self.repository, (RoleRepository, PermissionRepository)):
            raise PermissionError("Access to this method is not allowed.")
        return self.repository.get_all(session)

    def update(self, instance_id, data, session):
        """
        Updates an instance of the model with the given data.

        :param instance_id: The ID of the model instance to update.
        :type instance_id: int
        :param data: The data to update the model instance with.
        :type data: dict
        :param session: The database session.
        :type session: Session
        :return: The updated instance of the model.
        :rtype: object
        """
        return self.repository.update_obj(instance_id, data, session)

    def delete(self, instance_id, session):
        """
        Deletes an instance of the model by its ID.

        :param instance_id: The ID of the model instance to delete.
        :type instance_id: int
        :param session: The database session.
        :type session: Session
        :return: The deleted instance of the model.
        :rtype: object
        """
        return self.repository.delete(instance_id, session)

    def remove_attributes_from_object(self, object_template, attributes_to_remove):
        """
        Removes specified attributes from the object template.

        :param object_template: The template object from which attributes will be removed.
        :type object_template: dict
        :param attributes_to_remove: A list of attribute names to be removed.
        :type attributes_to_remove: list
        :return: The modified object template.
        :rtype: dict
        """
        for attr in attributes_to_remove:
            object_template.pop(attr, None)
        return object_template

    @staticmethod
    def datetime_to_string(date_obj):
        """
        Convert a datetime object to a date string.

        :param date_obj: Datetime object.
        :type date_obj: datetime
        :return: Corresponding date string in the format 'YYYY/MM/DD'.
        :rtype: str
        """
        return date_obj.strftime("%Y/%m/%d")
