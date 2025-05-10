import time

import pytest
from testcontainers.mongodb import MongoDbContainer
from typing_extensions import Self

from codeplag.db.mongo import (
    DEFAULT_MONGO_PASS,
    DEFAULT_MONGO_USER,
    FeaturesRepository,
    MongoDBConnection,
    ReportRepository,
)
from codeplag.types import ASTFeatures, FullCompareInfo


@pytest.fixture(scope="module")
def mongo_container() -> MongoDbContainer:
    with MongoDbContainer(
        "mongo:6.0", username=DEFAULT_MONGO_USER, password=DEFAULT_MONGO_PASS
    ) as mongo:
        mongo.start()
        time.sleep(7)
        yield mongo


@pytest.fixture(scope="module")
def mongo_connection(mongo_container: MongoDbContainer) -> MongoDBConnection:
    host = mongo_container.get_container_host_ip()
    port = int(mongo_container.get_exposed_port(27017))
    user = mongo_container.username
    password = mongo_container.password

    conn = MongoDBConnection(
        host=host,
        port=port,
        user=user,
        password=password,
    )
    yield conn


@pytest.fixture(autouse=True)
def clear_db(mongo_connection: MongoDBConnection) -> None:
    mongo_connection.clear_db()

    yield


class TestMongoDBInfrastructure:
    def test_mongodb_connection(self: Self, mongo_connection: MongoDBConnection):
        assert mongo_connection.client is not None
        assert mongo_connection.db is not None
        assert mongo_connection.get_collection("test").insert_one({"0": 1}).inserted_id is not None


class TestReportRepository:
    @pytest.fixture
    def report_repository(self: Self, mongo_connection: MongoDBConnection):
        return ReportRepository(mongo_connection)

    def test_report_repository_write_and_get(
        self: Self,
        report_repository: ReportRepository,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: FullCompareInfo,
    ):
        # Write compare info
        report_repository.write_compare_info(first_features, second_features, first_compare_result)

        # Read compare info
        result = report_repository.get_compare_info(first_features, second_features)

        # Compare metadata
        assert result is not None
        assert result.first_sha256 == first_features.sha256
        assert result.second_sha256 == second_features.sha256
        assert result.first_modify_date == first_features.modify_date
        assert result.second_modify_date == second_features.modify_date

        compare_info = result.compare_info

        # Compare result with compare info
        assert compare_info is not None
        assert compare_info.fast.jakkar == first_compare_result.fast.jakkar
        assert compare_info.fast.operators == first_compare_result.fast.operators
        assert compare_info.fast.keywords == first_compare_result.fast.keywords
        assert compare_info.fast.literals == first_compare_result.fast.literals
        assert compare_info.fast.weighted_average == first_compare_result.fast.weighted_average

    def test_report_repository_nonexistent_comparison(
        self: Self,
        report_repository: ReportRepository,
        first_features: ASTFeatures,
        third_features: ASTFeatures,
    ):
        result = report_repository.get_compare_info(first_features, third_features)
        assert result is None


class TestFeaturesRepository:
    @pytest.fixture
    def features_repository(self: Self, mongo_connection: MongoDBConnection):
        return FeaturesRepository(mongo_connection)

    def test_features_repository_write_and_get(
        self: Self, features_repository: FeaturesRepository, first_features: ASTFeatures
    ):
        # Write features
        features_repository.write_features(first_features)

        # Read features
        result = features_repository.get_features(first_features)

        # Compare result with features
        assert result is not None
        assert result == first_features
        assert result.sha256 == first_features.sha256
        assert result.modify_date == first_features.modify_date
        assert result.count_of_nodes == first_features.count_of_nodes
        assert result.head_nodes == first_features.head_nodes
        assert result.operators == first_features.operators
        assert result.keywords == first_features.keywords
        assert result.literals == first_features.literals
        assert result.unodes == first_features.unodes
        assert result.from_num == first_features.from_num
        assert result.count_unodes == first_features.count_unodes
        assert result.structure == first_features.structure
        assert result.tokens == first_features.tokens
        assert result.tokens_pos == first_features.tokens_pos

    def test_features_repository_nonexistent_file(
        self: Self, features_repository: FeaturesRepository, third_features: ASTFeatures
    ):
        result = features_repository.get_features(third_features)
        assert result is None
