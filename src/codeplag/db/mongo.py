"""MIT License.

Written 2025 by Stepan Pahomov, Daniil Lokosov, Artyom Semidolin.
"""

import atexit
from pathlib import Path
from typing import Final

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure
from typing_extensions import Self

from codeplag.consts import (
    DEFAULT_MONGO_HOST,
    DEFAULT_MONGO_PORT,
    DEFAULT_MONGO_USER,
    UTIL_NAME,
)
from codeplag.featurescache import (
    AbstractFeaturesCache,
    deserialize_features_from_dict,
    serialize_features_to_dict,
)
from codeplag.logger import codeplag_logger as logger
from codeplag.reporters import (
    AbstractReporter,
    deserialize_compare_result_from_dict,
    serialize_compare_result_to_dict,
)
from codeplag.types import ASTFeatures, FullCompareInfo, Settings


class MongoDBConnection:
    DB_NAME: Final = f"{UTIL_NAME}_cache"

    def __init__(
        self: Self,
        password: str,
        host: str = DEFAULT_MONGO_HOST,
        port: int = DEFAULT_MONGO_PORT,
        user: str = DEFAULT_MONGO_USER,
    ) -> None:
        """Initialize the connection to MongoDB.

        Args:
            host (str): MongoDB host address.
            port (int): MongoDB port number. Defaults to 27017.
            user (str): MongoDB username for authentication.
            password (str): MongoDB password for authentication.
        """
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.url: str = f"mongodb://{user}:{password}@{host}:{port}/"

        try:
            self.client = MongoClient(self.url, serverSelectionTimeoutMS=3000)
            self.client.admin.command("ping")
        except ConnectionFailure as err:
            logger.error("Failed to connect to MongoDB: %s", err)
            raise Exception(
                "Can't connect to MongoDB with selected 'mongo'. Check your settings. "
                "Please note if the application is running in Docker, the host may change."
            ) from err
        logger.debug("Successfully connected to the MongoDB.")
        self.db = self.client[self.DB_NAME]

        # Registering the disconnect method for execution upon program termination
        atexit.register(self.disconnect)

    @classmethod
    def from_settings(
        cls: type["MongoDBConnection"], settings_conf: Settings
    ) -> "MongoDBConnection":
        host = settings_conf.get("mongo_host", DEFAULT_MONGO_HOST)
        port = settings_conf.get("mongo_port", DEFAULT_MONGO_PORT)
        user = settings_conf.get("mongo_user", DEFAULT_MONGO_USER)
        password = settings_conf.get("mongo_pass")
        if password is None:
            raise ValueError("'mongo' reports_exception provided, but 'mongo-pass' is missing")

        return cls(host=host, port=port, user=user, password=password)

    def disconnect(self: Self) -> None:
        """Close the connection to MongoDB.

        Ensures that the MongoDB client is properly closed upon program termination.
        """
        if self.client:
            self.client.close()
            self.client = None
            logger.debug("MongoDB connection closed.")

    def get_collection(self: Self, collection_name: str) -> Collection | None:
        """Get a collection by name from the current database.

        Args:
            collection_name (str): The name of the collection to retrieve.

        Returns:
            Collection: The MongoDB collection object.
        """
        return self.db[collection_name] if self.db is not None else None

    def clear_db(self: Self) -> None:
        """Clears all collections."""
        for collection in self.db.list_collection_names():
            self.db[collection].delete_many({})


class ReportRepository:
    COLLECTION_NAME: Final = "compare_info"

    def __init__(self: Self, mongo_connection: MongoDBConnection) -> None:
        """Initialization of the repository for the compare_info collection."""
        collection = mongo_connection.get_collection(self.COLLECTION_NAME)
        if collection is None:
            logger.error('Mongo collection "%s" not found', self.COLLECTION_NAME)
            raise Exception('Mongo collection "%s" not found', self.COLLECTION_NAME)
        self.collection: Collection = collection

    def get_compare_info(
        self: Self, first_filepath: str | Path, second_filepath: str | Path
    ) -> FullCompareInfo | None:
        """Retrieve comparison result between two files from the compare_info collection.

        The document is identified by sorted file paths.

        Returns None if SHA-256 hashes of either file do not match stored values.

        Args:
            first_filepath (str | Path): First filepath.
            second_filepath (str | path): Second filepath.

        Returns:
            FullCompareInfo | None: Deserialized comparison result if found and valid.
        """
        # Sort works by filepath to form the unique key
        first_path, second_path = sorted([str(first_filepath), str(second_filepath)])
        document_id = {"first": first_path, "second": second_path}
        document = self.collection.find_one({"_id": document_id})
        if not document:
            logger.trace("No compare_info found for file path: (%s, %s)", first_path, second_path)  # type: ignore
            return None
        logger.trace("Compare_info found for file path: (%s, %s)", first_path, second_path)  # type: ignore

        return deserialize_compare_result_from_dict(document)

    def write_compare_info(self: Self, compare_info: FullCompareInfo) -> None:
        """Insert or update a document in the compare_info collection.

        The primary key (_id) is formed as a dictionary with sorted file paths.

        Args:
            compare_info (CompareInfo): Information about the comparison results.
        """
        document_id = {
            "first": str(compare_info.first_path),
            "second": str(compare_info.second_path),
        }
        document = {"_id": document_id, **serialize_compare_result_to_dict(compare_info)}

        self.collection.update_one({"_id": document_id}, {"$set": document}, upsert=True)
        logger.trace(  # type: ignore
            "Document for (%s, %s) successfully inserted/updated.",
            compare_info.first_path,
            compare_info.second_path,
        )


class FeaturesRepository:
    COLLECTION_NAME: Final = "features"

    def __init__(self: Self, mongo_connection: MongoDBConnection) -> None:
        """Initialization of the repository for the features collection."""
        collection = mongo_connection.get_collection(self.COLLECTION_NAME)
        if collection is None:
            logger.error('Mongo collection "%s" not found', self.COLLECTION_NAME)
            raise Exception('Mongo collection "%s" not found', self.COLLECTION_NAME)
        self.collection: Collection = collection

    def write_features(self: Self, work: ASTFeatures) -> None:
        """Insert or update a document in the features collection.

        The primary key (_id) is formed using the file path.

        Args:
            work (ASTFeatures): The file for which features are being saved.
        """
        document_id = str(work.filepath)
        serialized_work = serialize_features_to_dict(work)

        document = {
            "_id": document_id,
            "modify_date": work.modify_date,
            "sha256": work.sha256,
            "features": serialized_work,
        }

        self.collection.update_one({"_id": document_id}, {"$set": document}, upsert=True)
        logger.trace("Document for path %s successfully inserted/updated.", document_id)  # type: ignore

    def get_features(self: Self, work: ASTFeatures) -> ASTFeatures | None:
        """Retrieve AST features for a file from the features collection.

        The document is identified by its file path (_id = filepath).
        Returns None if the file's SHA-256 hash does not match the stored value.

        Args:
            work (ASTFeatures): File metadata used to search and validate the data.

        Returns:
            ASTFeatures | None: Deserialized AST features if found and valid.
        """
        document_id = str(work.filepath)
        document = self.collection.find_one({"_id": document_id})
        if not document:
            logger.trace("No features found for file path: %s", document_id)  # type: ignore
            return None
        logger.trace("Features found for file path: %s", document_id)  # type: ignore

        return deserialize_features_from_dict(document["features"])


class MongoReporter(AbstractReporter):
    def __init__(self: Self, repository: ReportRepository) -> None:
        self.repository = repository

    def save_result(self: Self, compare_info: FullCompareInfo) -> None:
        """Updates the cache with new comparisons and writes it to the MongoDB.

        Args:
            compare_info (CompareInfo): Contains information about comparisons
              between the first and second works.
        """
        self.repository.write_compare_info(compare_info)

    def get_result(
        self: Self,
        work1: ASTFeatures,
        work2: ASTFeatures,
    ) -> FullCompareInfo | None:
        """Get compare info from MongoDB cache if relevant.

        Args:
            work1 (ASTFeatures): Contains the first work metadata.
            work2 (ASTFeatures): Contains the second work metadata.
        """
        work1, work2 = sorted([work1, work2])
        cache_val = self.repository.get_compare_info(work1.filepath, work2.filepath)

        if (
            cache_val
            and cache_val.first_sha256 == work1.sha256
            and cache_val.second_sha256 == work2.sha256
        ):
            return cache_val
        else:
            return None


class MongoFeaturesCache(AbstractFeaturesCache):
    def __init__(self: Self, repository: FeaturesRepository) -> None:
        self.repository = repository

    def save_features(self: Self, features: ASTFeatures) -> None:
        """Updates the cache with new work metadata and writes it to the MongoDB.

        Args:
            features (ASTFeatures): Contains work metadata.
        """
        self.repository.write_features(features)

    def get_features(self: Self, work: ASTFeatures) -> ASTFeatures | None:
        """Get work metadata from MongoDB cache if relevant.

        Args:
            work (ASTFeatures): Contains work metadata.
        """
        features = self.repository.get_features(work)

        if features and features.modify_date == work.modify_date:
            return features
        else:
            return None
