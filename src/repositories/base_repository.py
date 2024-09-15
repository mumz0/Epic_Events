"""
This module defines the BaseRepository class which provides basic methods for interacting with the database.
"""


class BaseRepository:
    """
    This class provides basic methods for interacting with the database.

    :param model: The database model associated with this repository.
    :type model: object
    """

    def __init__(self, model):
        self.model = model

    def add(self, instance, session):
        """
        Adds a new instance to the database.

        :param instance: The instance to add.
        :type instance: object
        :param session: The database session.
        :type session: Session
        :return: The added instance.
        :rtype: object
        """
        session.add(instance)
        session.commit()
        return instance

    def add_all(self, instances, session):
        """
        Adds multiple instances to the database.

        :param instances: The instances to add.
        :type instances: list
        :param session: The database session.
        :type session: Session
        :return: The added instances.
        :rtype: list
        """
        session.add_all(instances)
        session.commit()
        return instances

    def get(self, instance_id, session):
        """
        Retrieves an instance by its ID.

        :param instance_id: The ID of the instance to retrieve.
        :type instance_id: int
        :param session: The database session.
        :type session: Session
        :return: The retrieved instance.
        :rtype: object
        """
        return session.query(self.model).get(instance_id)

    def get_all(self, session):
        """
        Retrieves all instances of the model.

        :param session: The database session.
        :type session: Session
        :return: A list of all instances of the model.
        :rtype: list
        """
        return session.query(self.model).all()

    def update(self, instance_id, data, session):
        """
        Updates an instance with the provided data.

        :param instance_id: The ID of the instance to update.
        :type instance_id: int
        :param data: The data to update the instance with.
        :type data: dict
        :param session: The database session.
        :type session: Session
        :return: The updated instance.
        :rtype: object
        """
        instance = session.query(self.model).get(instance_id)
        for key, value in data.items():
            setattr(instance, key, value)
        session.commit()
        return instance

    def delete(self, instance_id, session):
        """
        Deletes an instance by its ID.

        :param instance_id: The ID of the instance to delete.
        :type instance_id: int
        :param session: The database session.
        :type session: Session
        :return: The deleted instance.
        :rtype: object
        """
        instance = session.query(self.model).get(instance_id)
        session.delete(instance)
        session.commit()
        return instance
