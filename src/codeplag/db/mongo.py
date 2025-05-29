"""MIT License.

Written 2025 by Stepan Pahomov, Daniil Lokosov
"""

import atexit
from datetime import datetime
from typing import Final, NamedTuple

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
from codeplag.types import ASTFeatures, FullCompareInfo


class MongoDBConnection:
    DB_NAME: Final[str] = f"{UTIL_NAME}_cache"

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

        # Connecting to MongoDB
        try:
            self.client = MongoClient(self.url, serverSelectionTimeoutMS=3000)
            self.client.admin.command("ping")  # Checking the connection
        except ConnectionFailure as err:
            logger.error("Failed to connect to MongoDB: %s", err)
            raise err
        logger.debug("Successfully connected to MongoDB!")
        self.db = self.client[self.DB_NAME]

        # Registering the disconnect method for execution upon program termination
        atexit.register(self.disconnect)

    def disconnect(self: Self) -> None:
        """Close the connection to MongoDB.

        Ensures that the MongoDB client is properly closed upon program termination.
        """
        if self.client:
            self.client.close()
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
    class CompareInfoDocument(NamedTuple):
        """Compare Info Document structure."""

        first_sha256: str
        second_sha256: str
        first_modify_date: datetime
        second_modify_date: datetime
        compare_info: FullCompareInfo

    COLLECTION_NAME: str = "compare_info"

    def __init__(self: Self, mongo_connection: MongoDBConnection) -> None:
        """Initialization of the repository for the compare_info collection."""
        collection = mongo_connection.get_collection(self.COLLECTION_NAME)
        if collection is None:
            logger.error('Mongo collection "%s" not found', self.COLLECTION_NAME)
            raise Exception('Mongo collection "%s" not found', self.COLLECTION_NAME)
        self.collection: Collection = collection

    def get_compare_info(
        self: Self, work1: ASTFeatures, work2: ASTFeatures
    ) -> CompareInfoDocument | None:
        """Retrieve comparison result between two files from the compare_info collection.

        The document is identified by sorted file paths:
        _id = {"first": min(filepath), "second": max(filepath)}.
        Returns None if SHA-256 hashes of either file do not match stored values.

        Args:
            work1 (ASTFeatures): First file metadata.
            work2 (ASTFeatures): Second file metadata.

        Returns:
            ReportType | None: Deserialized comparison result if found and valid.
        """
        # Sort works by filepath to form the unique key
        work1, work2 = sorted([work1, work2])
        first_path, second_path = [str(work1.filepath), str(work2.filepath)]
        document_id = {"first": first_path, "second": second_path}

        # Find document in collection
        document = self.collection.find_one({"_id": document_id})
        if not document:
            logger.trace("No compare_info found for file path: (%s, %s)", first_path, second_path)  # type: ignore
            return None
        logger.trace("Compare_info found for file path: (%s, %s)", first_path, second_path)  # type: ignore

        # Deserialize and return compare_info
        compare_info = deserialize_compare_result_from_dict(document["compare_info"])
        return self.CompareInfoDocument(
            first_sha256=document["first_sha256"],
            second_sha256=document["second_sha256"],
            first_modify_date=document["first_modify_date"],
            second_modify_date=document["second_modify_date"],
            compare_info=compare_info,
        )

    def write_compare_info(
        self: Self, work1: ASTFeatures, work2: ASTFeatures, compare_info: FullCompareInfo
    ) -> None:
        """Insert or update a document in the compare_info collection.

        The primary key (_id) is formed as a dictionary with sorted file paths.

        Args:
            work1 (ASTFeatures): The first file for comparison.
            work2 (ASTFeatures): The second file for comparison.
            compare_info (CompareInfo): Information about the comparison results.
        """
        # Sorting paths to create a unique primary key
        work1, work2 = sorted([work1, work2])
        first_path, second_path = [str(work1.filepath), str(work2.filepath)]

        # Forming _id as a string of sorted paths
        document_id = {"first": first_path, "second": second_path}

        # Using the serialize_compare_result_to_dict function to convert data
        serialized_compare_info = serialize_compare_result_to_dict(compare_info)

        document = {
            "_id": document_id,
            "first_sha256": work1.sha256,
            "second_sha256": work2.sha256,
            "first_modify_date": work1.modify_date,
            "second_modify_date": work2.modify_date,
            "compare_info": serialized_compare_info,
        }

        # Insert or update the document
        self.collection.update_one({"_id": document_id}, {"$set": document}, upsert=True)
        logger.trace(  # type: ignore
            "Document for (%s, %s) successfully inserted/updated.", first_path, second_path
        )


class FeaturesRepository:
    COLLECTION_NAME: str = "features"

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
        # Forming _id as the file path
        document_id = str(work.filepath)

        # Using function serialize_features_to_dict to convert data
        serialized_work = serialize_features_to_dict(work)

        document = {
            "_id": document_id,
            "modify_date": work.modify_date,
            "sha256": work.sha256,
            "features": serialized_work,
        }

        # Insert or update the document
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

        # Find document in collection
        document = self.collection.find_one({"_id": document_id})
        if not document:
            logger.trace("No features found for file path: %s", document_id)  # type: ignore
            return None
        logger.trace("Features found for file path: %s", document_id)  # type: ignore

        # Deserialize and return features
        features = deserialize_features_from_dict(document["features"])
        return features


class MongoReporter(AbstractReporter):
    def __init__(self: Self, repository: ReportRepository) -> None:
        self.repository = repository

    def save_result(
        self: Self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        compare_info: FullCompareInfo,
    ) -> None:
        """Updates the cache with new comparisons and writes it to the MongoDB.

        Args:
            first_work (ASTFeatures): Contains the first work metadata.
            second_work (ASTFeatures): Contains the second work metadata.
            compare_info (CompareInfo): Contains information about comparisons
              between the first and second works.
        """
        self.repository.write_compare_info(first_work, second_work, compare_info)

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
        cache_val = self.repository.get_compare_info(work1, work2)

        if (
            cache_val
            and cache_val.first_sha256 == work1.sha256
            and cache_val.second_sha256 == work2.sha256
        ):
            return cache_val.compare_info
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
