"""
This module defines the BaseRepository class which provides basic methods for interacting with the database.
"""

import sentry_sdk


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
        try:
            instance = session.query(self.model).get(instance_id)
            if not instance:
                error_message = f"Instance with ID {instance_id} not found."
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)
            return instance
        except Exception as e:
            error_message = f"Error retrieving instance by ID: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)

    def get_id(self, instance_name, session):
        """
        Retrieves an instance by its name.

        :param instance_name: The name of the instance to retrieve.
        :type instance_name: str
        :param session: The database session.
        :type session: Session
        :return: The retrieved instance.
        :rtype: object
        """
        try:
            instance = session.query(self.model).filter_by(name=instance_name).first()
            if not instance:
                error_message = f"Instance with name {instance_name} not found."
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)
            return instance
        except Exception as e:
            error_message = f"Error retrieving instance by name: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)

    def get_all(self, session):
        """
        Retrieves all instances of the model.

        :param session: The database session.
        :type session: Session
        :return: A list of all instances of the model.
        :rtype: list
        """
        try:
            instances = session.query(self.model).all()
            return instances
        except Exception as e:
            error_message = f"Error retrieving all instances: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)

    def update_obj(self, instance_id, data, session):
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
        try:
            instance = session.query(self.model).get(instance_id)
            if not instance:
                error_message = f"Instance with ID {instance_id} not found."
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)

            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            session.commit()
            return instance
        except Exception as e:
            error_message = f"Error updating instance: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)

    def update_attr(self, instance_id, attribute_name, value, session):
        """
        Updates a single attribute of an instance with the provided value.

        :param instance_id: The ID of the instance to update.
        :type instance_id: int
        :param attribute_name: The name of the attribute to update.
        :type attribute_name: str
        :param value: The value to set for the attribute.
        :type value: any
        :param session: The database session.
        :type session: Session
        :return: The updated instance.
        :rtype: object
        """
        try:
            instance = session.query(self.model).filter_by(id=instance_id).first()
            if not instance:
                error_message = f"Instance with ID {instance_id} not found."
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)

            setattr(instance, attribute_name, value)
            session.commit()
            return instance
        except Exception as e:
            error_message = f"Error updating attribute: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)

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
        try:
            instance = session.query(self.model).filter_by(id=instance_id).first()
            if not instance:
                error_message = f"Instance with ID {instance_id} not found."
                sentry_sdk.capture_message(error_message)
                raise ValueError(error_message)

            session.delete(instance)
            session.commit()
            return instance
        except Exception as e:
            error_message = f"Error deleting instance: {str(e)}"
            sentry_sdk.capture_exception(e)
            raise ValueError(error_message) from (e)
