from pymongo import MongoClient


class MongoDBConnection:
    def __init__(self, url="mongodb://localhost:27017/", db_name="new_database"):
        """
        Класс инициализации подключения к MongoDB.

        :param url:
        :param db_name:
        """
        self.url = url
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        """
        Подключение к MongoDB.
        """

        pass

    def disconnect(self):
        """
        Отключение от MongoDB.
        """

        pass

    def get_collection(self, collection_name):
        """
        Получение коллекции по имени из текущей базы данных.

        :param collection_name: Имя коллекции.
        :return: Объект коллекции текущей базы данных.
        """

        pass
