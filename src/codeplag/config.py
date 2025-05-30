import json
from pathlib import Path
from typing import Any, Literal, Mapping, overload

from codeplag.consts import (
    CONFIG_PATH,
    DEFAULT_LANGUAGE,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_DEPTH,
    DEFAULT_MONGO_HOST,
    DEFAULT_MONGO_PORT,
    DEFAULT_MONGO_USER,
    DEFAULT_NGRAMS_LENGTH,
    DEFAULT_REPORT_EXTENSION,
    DEFAULT_THRESHOLD,
    DEFAULT_WORKERS,
)
from codeplag.logger import codeplag_logger as logger
from codeplag.types import Settings, ShortOutput

Config = dict[str, Any]


@overload
def read_config(file: Path, safe: Literal[False] = False) -> Config: ...


@overload
def read_config(file: Path, safe: bool = False) -> Config | None: ...


def read_config(file: Path, safe: bool = False) -> Config | None:
    config = None
    try:
        with file.open(mode="r") as f:
            config = json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError, PermissionError):
        if not safe:
            raise

    return config


# TODO: Handle permission denied
def write_config(file: Path, config: Mapping[str, Any]) -> None:
    config_for_dump = dict(config)
    for key in config_for_dump:
        if isinstance(config_for_dump[key], Path):
            config_for_dump[key] = str(config_for_dump[key])

    with file.open(mode="w", encoding="utf-8") as f:
        json.dump(config_for_dump, f, indent=4)


def read_settings_conf() -> Settings:
    loaded_settings_config = read_config(CONFIG_PATH, safe=True)
    if loaded_settings_config is None:
        logger.warning(
            "Unsuccessful attempt to read config '%s'. Returning default config.",
            CONFIG_PATH,
        )
        return DefaultSettingsConfig

    for key in Settings.__annotations__:
        if key not in loaded_settings_config:
            if key in DefaultSettingsConfig:
                loaded_settings_config[key] = DefaultSettingsConfig[key]
            continue

        if key in ["environment", "reports"]:
            loaded_settings_config[key] = Path(loaded_settings_config[key])

    return Settings(
        **{
            key: loaded_settings_config[key]
            for key in Settings.__annotations__
            if key in loaded_settings_config
        }
    )


def write_settings_conf(settings: Settings) -> None:
    write_config(CONFIG_PATH, settings)


DefaultSettingsConfig = Settings(
    threshold=DEFAULT_THRESHOLD,
    max_depth=DEFAULT_MAX_DEPTH,
    ngrams_length=DEFAULT_NGRAMS_LENGTH,
    show_progress=0,
    short_output=ShortOutput.SHOW_ALL,
    reports_extension=DEFAULT_REPORT_EXTENSION,
    language=DEFAULT_LANGUAGE,
    log_level=DEFAULT_LOG_LEVEL,
    workers=DEFAULT_WORKERS,
    mongo_host=DEFAULT_MONGO_HOST,
    mongo_port=DEFAULT_MONGO_PORT,
    mongo_user=DEFAULT_MONGO_USER,
)
