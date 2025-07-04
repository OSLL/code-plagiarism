from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from codeplag.config import read_settings_conf, write_settings_conf
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
    settings_config = read_settings_conf()
    for key in Settings.__annotations__:
        new_value = parsed_args.get(key)
        if new_value is None:
            continue
        if isinstance(new_value, Path):
            settings_config[key] = new_value.resolve()
        else:
            settings_config[key] = new_value

        write_settings_conf(settings_config)
