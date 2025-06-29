"""MIT License.

Written 2025 by Konstantin Rogozhin, Nikolai Myshkin, Artyom Semidolin.
"""

import dataclasses
import os
from typing import Generator

import pytest
from typing_extensions import Self

from codeplag.consts import DEFAULT_MONGO_PORT, DEFAULT_MONGO_USER
from codeplag.db.mongo import (
    FeaturesRepository,
    MongoDBConnection,
    MongoFeaturesCache,
    MongoReporter,
    ReportRepository,
)
from codeplag.types import ASTFeatures, FullCompareInfo


@pytest.fixture(scope="module")
def mongo_host() -> str:
    host = os.environ.get("MONGO_HOST")
    assert host, f"Invalid MONGO_HOST environment '{host}'."
    return host


@pytest.fixture(scope="module")
def mongo_connection(mongo_host: str) -> Generator[MongoDBConnection, None, None]:
    conn = MongoDBConnection(
        host=mongo_host,
        port=DEFAULT_MONGO_PORT,
        user=DEFAULT_MONGO_USER,
        password=DEFAULT_MONGO_USER,
    )
    yield conn


@pytest.fixture(autouse=True)
def clear_db(mongo_connection: MongoDBConnection) -> Generator[None, None, None]:
    yield

    mongo_connection.clear_db()


class TestMongoDBInfrastructure:
    def test_mongodb_connection(self: Self, mongo_connection: MongoDBConnection):
        assert mongo_connection.client is not None
        assert mongo_connection.db is not None
        assert mongo_connection.get_collection("test").insert_one({"0": 1}).inserted_id is not None


class TestReportRepository:
    @pytest.fixture(scope="class")
    def report_repository(self: Self, mongo_connection: MongoDBConnection) -> ReportRepository:
        return ReportRepository(mongo_connection)

    def test_report_repository_write_and_get(
        self: Self,
        report_repository: ReportRepository,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: FullCompareInfo,
    ):
        report_repository.write_compare_info(first_compare_result)
        compare_info = report_repository.get_compare_info(
            first_features.filepath, second_features.filepath
        )

        # Compare metadata
        assert compare_info is not None
        assert compare_info.date
        assert compare_info.first_sha256 == first_compare_result.first_sha256
        assert compare_info.second_sha256 == first_compare_result.second_sha256
        assert compare_info.first_modify_date == first_compare_result.first_modify_date
        assert compare_info.second_modify_date == first_compare_result.second_modify_date
        assert compare_info.first_path == first_compare_result.first_path
        assert compare_info.second_path == first_compare_result.second_path
        assert compare_info.first_heads == first_compare_result.first_heads
        assert compare_info.second_heads == first_compare_result.second_heads

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
        result = report_repository.get_compare_info(
            first_features.filepath, third_features.filepath
        )
        assert result is None


class TestFeaturesRepository:
    @pytest.fixture(scope="class")
    def features_repository(self: Self, mongo_connection: MongoDBConnection) -> FeaturesRepository:
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
    def mongo_reporter(self: Self, mongo_connection: MongoDBConnection) -> MongoReporter:
        repository = ReportRepository(mongo_connection)
        return MongoReporter(repository)

    def test_write_read_report(
        self: Self,
        mongo_reporter: MongoReporter,
        first_features: ASTFeatures,
        second_features: ASTFeatures,
        first_compare_result: FullCompareInfo,
    ):
        mongo_reporter.save_result(first_compare_result)
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
        mongo_reporter.save_result(first_compare_result)

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
        mongo_reporter.save_result(first_compare_result)

        work2 = dataclasses.replace(second_features)
        work2.sha256 = "new_sha256"

        result = mongo_reporter.get_result(first_features, work2)

        assert result is None


class TestMongoFeaturesCache:
    @pytest.fixture
    def mongo_features_cache(
        self: Self, mongo_connection: MongoDBConnection
    ) -> MongoFeaturesCache:
        repository = FeaturesRepository(mongo_connection)
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
