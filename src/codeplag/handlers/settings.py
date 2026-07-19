from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from codeplag.config import read_settings_conf, write_settings_conf
from codeplag.logger import codeplag_logger as logger
from codeplag.types import Settings


def settings_show() -> None:
    settings_config = read_settings_conf()
    if "mongo_pass" in settings_config:
        del settings_config["mongo_pass"]
    table = pd.DataFrame(
        list(settings_config.values()),
        index=np.array(settings_config),
        columns=pd.Index(["Value"], name="Key"),
    )
    print(table)


def settings_modify(parsed_args: dict[str, Any]) -> None:
    if not parsed_args:
        logger.info("No arguments provided to change settings.")
        return

    settings_config = read_settings_conf()

    # Because in the argument parser 'reports' parsed as a string
    if parsed_args.get("reports"):
        parsed_args["reports"] = Path(parsed_args["reports"])

    for key in Settings.__annotations__:
        new_value = parsed_args.get(key)
        if new_value is None:
            continue
        if new_value == "" and key in settings_config:
            logger.info("Empty value provided for setting '%s', deleting it.", key)
            del settings_config[key]
            continue
        if isinstance(new_value, Path):
            settings_config[key] = new_value.resolve()
        else:
            settings_config[key] = new_value
    write_settings_conf(settings_config)
