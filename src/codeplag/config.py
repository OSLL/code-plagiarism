import json
from pathlib import Path
from typing import Any, Dict, Literal, Mapping, Optional, overload

from typing_extensions import NotRequired

from codeplag.consts import (
    CONFIG_PATH,
    DEFAULT_LANGUAGE,
    DEFAULT_REPORT_EXTENSION,
    DEFAULT_THRESHOLD,
    DEFAULT_WORKERS,
)
from codeplag.logger import codeplag_logger as logger
from codeplag.types import Settings

Config = Dict[str, Any]


@overload
def read_config(file: Path, safe: Literal[False] = False) -> Config:
    ...


@overload
def read_config(file: Path, safe: bool = False) -> Optional[Config]:
    ...


def read_config(file: Path, safe: bool = False) -> Optional[Config]:
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

    for key, key_type in Settings.__annotations__.items():
        if key not in loaded_settings_config:
            if key in DefaultSettingsConfig:
                loaded_settings_config[key] = DefaultSettingsConfig[key]
            continue

        if key_type == Path or key_type == NotRequired[Path]:  # type: ignore
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
    show_progress=0,
    reports_extension=DEFAULT_REPORT_EXTENSION,
    language=DEFAULT_LANGUAGE,
    workers=DEFAULT_WORKERS,
)
