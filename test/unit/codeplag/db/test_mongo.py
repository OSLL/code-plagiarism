"""MIT License.

Written 2025 by Konstantin Rogozhin, Nikolai Myshkin
"""

import dataclasses
import time

import pytest
from testcontainers.mongodb import MongoDbContainer
from typing_extensions import Self

from codeplag.consts import DEFAULT_MONGO_USER
from codeplag.db.mongo import (
    FeaturesRepository,
    MongoDBConnection,
    MongoFeaturesCache,
    MongoReporter,
    ReportRepository,
)
from codeplag.types import ASTFeatures, FullCompareInfo
from unit.codeplag.db.testkit import FeaturesRepositoryStub, ReportRepositoryStub


@pytest.fixture(scope="module")
def mongo_container() -> MongoDbContainer:
    with MongoDbContainer("mongo:8.0", username=DEFAULT_MONGO_USER) as mongo:
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
    @pytest.fixture(scope="class")
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
    @pytest.fixture(scope="class")
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


class TestMongoReporter:
    @pytest.fixture
    def mongo_reporter(self: Self) -> MongoReporter:
        repository = ReportRepositoryStub()
        return MongoReporter(repository)

    def test_write_read_report(
        self: Self,
        mongo_reporter: MongoReporter,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: FullCompareInfo,
    ):
        mongo_reporter.save_result(first_features, second_features, first_compare_result)

        result = mongo_reporter.get_result(first_features, second_features)

        assert result is not None
        assert result.fast.jakkar == first_compare_result.fast.jakkar
        assert result.fast.operators == first_compare_result.fast.operators
        assert result.fast.keywords == first_compare_result.fast.keywords
        assert result.fast.literals == first_compare_result.fast.literals
        assert result.fast.weighted_average == first_compare_result.fast.weighted_average

    def test_read_nonexistent_report(
        self: Self,
        mongo_reporter: MongoReporter,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
    ):
        result = mongo_reporter.get_result(first_features, second_features)

        assert result is None

    def test_read_after_first_modify(
        self: Self,
        mongo_reporter: MongoReporter,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: FullCompareInfo,
    ):
        mongo_reporter.save_result(first_features, second_features, first_compare_result)

        work1 = dataclasses.replace(first_features)
        work1.sha256 = "new_sha256"

        result = mongo_reporter.get_result(work1, second_features)

        assert result is None

    def test_read_after_second_modify(
        self: Self,
        mongo_reporter: MongoReporter,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: FullCompareInfo,
    ):
        mongo_reporter.save_result(first_features, second_features, first_compare_result)

        work2 = dataclasses.replace(second_features)
        work2.sha256 = "new_sha256"

        result = mongo_reporter.get_result(first_features, work2)

        assert result is None


class TestMongoFeaturesCache:
    @pytest.fixture
    def mongo_features_cache(self: Self) -> MongoFeaturesCache:
        repository = FeaturesRepositoryStub()
        return MongoFeaturesCache(repository)

    def test_write_read_features(
        self: Self,
        mongo_features_cache: MongoFeaturesCache,
        first_features: ASTFeatures,
    ):
        mongo_features_cache.save_features(first_features)

        result = mongo_features_cache.get_features(first_features)

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

    def test_read_nonexistent_features(
        self: Self,
        mongo_features_cache: MongoFeaturesCache,
        first_features: ASTFeatures,
    ):
        result = mongo_features_cache.get_features(first_features)

        assert result is None

    def test_read_after_modify(
        self: Self,
        mongo_features_cache: MongoFeaturesCache,
        first_features: ASTFeatures,
    ):
        mongo_features_cache.save_features(first_features)

        modified_features = dataclasses.replace(first_features)
        modified_features.modify_date = "new_sha256"

        result = mongo_features_cache.get_features(modified_features)

        assert result is None
