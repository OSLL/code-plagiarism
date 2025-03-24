import sys
import os
import atexit
import numpy as np
from pathlib import Path
from collections import defaultdict
from typing import Dict
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from codeplag.types import ASTFeatures, CompareInfo, FastMetrics, StructuresInfo
from codeplag.logger import codeplag_logger as logger
# from ..reporters import serialize_compare_result_to_dict, deserialize_compare_result_from_dict


HOST = "localhost"
USER = "root"
PASSWORD = "example"


class MongoDBConnection:
    def __init__(self, host=HOST, user=USER, password=PASSWORD, db_name="new_database"):
        """
        Инициализация подключения к MongoDB.

        :param host: Хост MongoDB.
        :param user: Имя пользователя MongoDB.
        :param password: Пароль пользователя MongoDB.
        :param db_name: Имя базы данных.
        """
        self.url = self.url = f"mongodb://{user}:{password}@{host}:27017/"
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
            logger.debug("Подключение к MongoDB успешно!")
            self.db = self.client[self.db_name]
        except ConnectionFailure as e:
            logger.error(f"Не удалось подключиться к MongoDB: {e}")
            raise

    def disconnect(self):
        """
        Отключение от MongoDB.
        """
        if self.client:
            self.client.close()
            logger.debug("Подключение к MongoDB закрыто.")

    def get_collection(self, collection_name):
        """
        Получение коллекции по имени из текущей базы данных.

        :param collection_name: Имя коллекции.
        :return: Объект коллекции текущей базы данных.
        """

        return self.db[collection_name]


class ReportRepository:
    def __init__(self, mongo_connection: MongoDBConnection):
        """
        Инициализация репозитория для коллекции compare_info.
        """
        self.collection = mongo_connection.get_collection("compare_info")

    def write_compare_info(
        self,
        work1: ASTFeatures,
        work2: ASTFeatures,
        compare_info: CompareInfo
    ):
        """
        Вставка или обновление документа в коллекции compare_info.
        Первичный ключ: _id (отсортированные пути).

        Args:
            work1 (ASTFeatures): Первый файл для сравнения.
            work2 (ASTFeatures): Второй файл для сравнения.
            compare_info (CompareInfo): Информация о сравнении.
        """
        # Сортируем пути для создания уникального первичного ключа
        first_path, second_path = sorted([str(work1.filepath), str(work2.filepath)])

        # Формируем _id как строку из отсортированных путей
        document_id = {"first": first_path, "second": second_path}

        # Используем функцию serialize_compare_result_to_dict для преобразования данных
        serialized_compare_info = None  # serialize_compare_result_to_dict(compare_info)

        document = {
            "_id": document_id,
            "first_path": first_path,
            "second_path": second_path,
            "first_sha256": work1.sha256,
            "second_sha256": work2.sha256,
            "first_modify_date": work1.modify_date,
            "second_modify_date": work2.modify_date,
            "compare_info": serialized_compare_info,
        }

        # Вставка или обновление документа
        self.collection.update_one(
            {"_id": document_id},
            {"$set": document},
            upsert=True
        )
        print(f"Документ для ({first_path}, {second_path}) успешно вставлен/обновлен.")


class FeatureRepository:
    def __init__(self, mongo_connection: MongoDBConnection):
        """
        Инициализация репозитория для коллекции features.
        """
        self.collection = mongo_connection.get_collection("features")

    def write_feature(self, work: ASTFeatures, cmp_for_feature: CompareInfo):
        """
        Вставка или обновление документа в коллекции features.
        Первичный ключ: path.

        Args:
            work (ASTFeatures): Файл для сохранения признаков.
            cmp_for_feature (CompareInfo): объект с нужными данными о структуре
        """
        # Формируем _id как путь файла
        document_id = {"first": str(work.filepath)}

        document = {
            "_id": document_id,
            "path": document_id,
            "modify_date": work.modify_date,
            "sha256": work.sha256,
            "features": {
                "head_nodes": work.head_nodes,
                "structure": {
                    "similarity": cmp_for_feature.structure.similarity,
                    "compliance_matrix": cmp_for_feature.structure.compliance_matrix.tolist(),
                }
            }
        }

        # Вставка или обновление документа
        self.collection.update_one(
            {"_id": document_id},
            {"$set": document},
            upsert=True
        )
        print(f"Документ для пути {document_id} успешно вставлен/обновлен.")
