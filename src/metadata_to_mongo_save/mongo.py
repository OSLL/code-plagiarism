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

    def get_database(self):
        """
        Получение объекта базы данных.
        """

        pass

    def list_collections(self):
        """
        Вывод списка коллекций в текущей базе данных.
        """

        pass

    def get_collection(self, collection_name):
        """
        Получение коллекции по имени из текущей базы данных.

        :param collection_name: Имя коллекции.
        :return: Объект коллекции текущей базы данных.
        """

        pass

    def insert_document(self, collection_name, document):
        """
        Вставка документа в коллекцию текущего объекта базы данных.

        :param collection_name: Имя коллекции.
        :param document: Документ для вставки (обычно словарь).
        :return: ID вставленного документа.
        """

        pass

    def find_document(self, collection_name, query=None):
        """
        Поиск документа по заданному условию в коллекцию текущего объекта базы данных.

        :param collection_name: Имя коллекции.
        :param query: Условие поиска - словарь (опциональный параметр).
        :return: Список найденных документов.
        """

        pass

    def delete_document(self, collection_name, query):
        """
        Удаление документа из коллекции текущего объекта базы данных.
        (возможно создание метода множественного удаления).

        :param collection_name: Имя коллекции.
        :param query: Обязательное условие (словарь).
        :return: Количество удалённых элементов.
        """

        pass
