from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import sys
import atexit
from typing import Dict


HOST = "localhost"
USER = "username"
PASSWORD = ""


class MongoDBConnection:
    def __init__(self, host=HOST, user=USER, password=PASSWORD, db_name="new_database"):
        """
        Инициализация подключения к MongoDB.

        :param host: Хост MongoDB.
        :param user: Имя пользователя MongoDB.
        :param password: Пароль пользователя MongoDB.
        :param db_name: Имя базы данных.
        """
        # future url: url = self.url = f"mongodb://{user}:{password}@{host}:27017/"
        self.url = "mongodb://localhost:27017/"
        self.db_name = db_name
        self.client = None
        self.db = None

        # Подключение к MongoDB
        self.connect()

        # Регистрация метода disconnect для выполнения при завершении программы
        atexit.register(self.disconnect)

    def connect(self):
        """
        Подключение к MongoDB.
        """
        try:
            self.client = MongoClient(self.url, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')  # Проверка подключения
            print("Подключение к MongoDB успешно!")
            self.db = self.client[self.db_name]
        except ConnectionFailure as e:
            print(f"Не удалось подключиться к MongoDB: {e}")
            raise

    def disconnect(self):
        """
        Отключение от MongoDB.
        """
        if self.client:
            self.client.close()
            print("Подключение к MongoDB закрыто.")

    def get_collection(self, collection_name):
        """
        Получение коллекции по имени из текущей базы данных.

        :param collection_name: Имя коллекции.
        :return: Объект коллекции текущей базы данных.
        """
        pass


class ReportRepository:
    def __init__(self):
        """
        Инициализация репозитория для коллекции compare_info.
        """
        self.compare_info = None

    def write_compare_info(self, first_path: str, second_path: str, compare_info: Dict):
        """
        Вставка или обновление документа в коллекции compare_info.
        Первичный ключ: (first_path, second_path).
        """
        document = {
            "first_path": first_path,
            "second_path": second_path,
            "compare_info": compare_info
        }

        # other instructions  with self.compare_info


class FeatureRepository:
    def __init__(self):
        """
        Инициализация репозитория для коллекции features.
        """
        self.collection = None

    def write_feature(self, path: str, modify_date: str, sha256: str, features: Dict):
        """
        Вставка или обновление документа в коллекции features.
        Первичный ключ: path.
        """
        document = {
            "path": path,
            "modify_date": modify_date,
            "sha256": sha256,
            "features": features
        }

        # other instructions
