from codeplag.types import ExitCode


def main() -> ExitCode:
    import argcomplete
    import pandas as pd

    from codeplag.codeplagcli import CodeplagCLI
    from codeplag.config import read_settings_conf
    from codeplag.consts import LOG_PATH
    from codeplag.logger import codeplag_logger as logger
    from codeplag.logger import set_handlers
    from codeplag.translate import get_translations
    from codeplag.utils import CodeplagEngine

    pd.set_option("display.float_format", "{:,.2%}".format)
    pd.set_option("display.max_colwidth", None)

    translations = get_translations()
    translations.install()

    cli = CodeplagCLI()
    argcomplete.autocomplete(cli)
    parsed_args = vars(cli.parse_args())
    settings_conf = read_settings_conf()
    set_handlers(logger, LOG_PATH, settings_conf["log_level"])
    try:
        codeplag_util = CodeplagEngine(parsed_args)
        code = codeplag_util.run()
    except KeyboardInterrupt:
        logger.warning("The util stopped by keyboard interrupt.")
        return ExitCode.EXIT_KEYBOARD
    except Exception:
        logger.error(
            "An unexpected error occurred while running the utility. "
            "For getting more information, check file '%s'.",
            LOG_PATH,
        )
        logger.debug("Trace:", exc_info=True)
        return ExitCode.EXIT_UNKNOWN

    return code
