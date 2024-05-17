"""Provides functionality for translating application messages into different languages."""

import gettext

from codeplag.config import read_settings_conf
from codeplag.consts import TRANSLATIONS_PATH, UTIL_NAME


def get_translations() -> gettext.GNUTranslations:
    return gettext.translation(
        UTIL_NAME,
        TRANSLATIONS_PATH,
        fallback=False,
        languages=[read_settings_conf()["language"]],
    )
