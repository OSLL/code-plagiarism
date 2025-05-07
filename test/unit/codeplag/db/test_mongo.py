import pytest
from testcontainers.mongodb import MongoDbContainer

from codeplag.algorithms.compare import compare_works
from codeplag.db.mongo import (
    DEFAULT_MONGO_PASS,
    DEFAULT_MONGO_USER,
    FeaturesRepository,
    MongoDBConnection,
    ReportRepository,
)
from codeplag.types import ASTFeatures, FullCompareInfo


@pytest.fixture(scope="module")
def mongo_container():
    """Фикстура создает временный контейнер MongoDB для тестов.

    Контейнер живет в течение всего модуля тестов (scope='module')
    """
    with MongoDbContainer(
        "mongo:6.0", username=DEFAULT_MONGO_USER, password=DEFAULT_MONGO_PASS
    ) as mongo:
        mongo.start()
        yield mongo


@pytest.fixture
def mongo_connection(mongo_container: MongoDbContainer) -> MongoDBConnection:
    """Фикстура создает подключение к тестовой MongoDB.

    Подключение автоматически закрывается после каждого теста.
    """
    host = mongo_container.get_container_host_ip()
    port = int(mongo_container.get_exposed_port(27017))

    conn = MongoDBConnection(host=host, port=port)
    yield conn
    conn.disconnect()


@pytest.fixture
def report_repository(mongo_connection: MongoDbContainer):
    """Фикстура создает репозиторий для работы с отчетами сравнений."""
    return ReportRepository(mongo_connection)


@pytest.fixture
def features_repository(mongo_connection: MongoDbContainer):
    """Фикстура создает репозиторий для работы с фичами AST."""
    return FeaturesRepository(mongo_connection)


def test_mongodb_connection(mongo_connection: MongoDbContainer):
    """Тест проверяет успешное подключение к MongoDB.

    Проверяет, что клиент и база данных инициализированы.
    """
    assert mongo_connection.client is not None
    assert mongo_connection.db is not None


def test_report_repository_write_and_get(
    report_repository: ReportRepository,
    first_features: ASTFeatures,
    second_features: ASTFeatures,
    first_compare_result: FullCompareInfo,
):
    """Тест проверяет базовые операции ReportRepository.

    1. Запись результатов сравнения в БД.
    2. Чтение ранее сохраненных результатов.
    3. Корректность сохраненных данных (хеши, структура).
    """
    # Записываем данные сравнения
    report_repository.write_compare_info(first_features, second_features, first_compare_result)

    # Читаем данные сравнения
    result = report_repository.get_compare_info(first_features, second_features)

    # Проверяем результаты
    assert result is not None, "Результат сравнения не должен быть None"
    assert result.first_sha256 == first_features.sha256, "Хеш первого файла не совпадает"
    assert result.second_sha256 == second_features.sha256, "Хеш второго файла не совпадает"

    # Дополнительная проверка структуры сравнения
    compare_info = compare_works(features1=first_features, features2=second_features)
    assert isinstance(compare_info, FullCompareInfo), (
        "Результат сравнения должен быть FullCompareInfo"
    )


def test_report_repository_nonexistent_comparison(
    report_repository: ReportRepository, first_features: ASTFeatures, third_features: ASTFeatures
):
    """Тест проверяет поведение при запросе несуществующего сравнения.

    Ожидается возврат None.
    """
    result = report_repository.get_compare_info(first_features, third_features)
    assert result is None, "Для несуществующего сравнения должен возвращаться None"


def test_features_repository_write_and_get(
    features_repository: FeaturesRepository, first_features: ASTFeatures
):
    """Тест проверяет базовые операции FeaturesRepository.

    1. Запись фич в БД.
    2. Чтение ранее сохраненных фич.
    3. Корректность сохраненных данных (хеш, путь к файлу).
    """
    # Записываем фичи
    features_repository.write_features(first_features)

    # Читаем фичи
    result = features_repository.get_features(first_features)

    # Проверяем результаты
    assert result is not None, "Результат не должен быть None"
    assert result.sha256 == first_features.sha256, "Хеш файла не совпадает"
    assert str(result.filepath) == str(first_features.filepath), "Путь к файлу не совпадает"


def test_features_repository_nonexistent_file(
    features_repository: FeaturesRepository, third_features: ASTFeatures
):
    """Тест проверяет поведение при запросе несуществующих фич.

    Ожидается возврат None.
    """
    result = features_repository.get_features(third_features)
    assert result is None, "Для несуществующего файла должен возвращаться None"
