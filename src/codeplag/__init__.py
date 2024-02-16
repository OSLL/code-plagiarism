from typing import Literal


def main() -> Literal[0, 1, 2]:
    import argcomplete
    import pandas as pd

    from codeplag.codeplagcli import CodeplagCLI
    from codeplag.consts import LOG_PATH
    from codeplag.logger import codeplag_logger as logger
    from codeplag.logger import set_handlers
    from codeplag.utils import CodeplagEngine

    pd.set_option("display.float_format", "{:,.2%}".format)
    pd.set_option("display.max_colwidth", None)

    cli = CodeplagCLI()
    argcomplete.autocomplete(cli)
    parsed_args = vars(cli.parse_args())
    verbose = bool(parsed_args["verbose"])

    set_handlers(logger, LOG_PATH, verbose)
    codeplag_util = CodeplagEngine(logger, parsed_args)
    try:
        code = codeplag_util.run()
    except KeyboardInterrupt:
        logger.warning("The util stopped by keyboard interrupt.")
        return 1
    except Exception:
        logger.error(
            "An unexpected error occurred while running the utility. "
            "For getting more information, check file '%s'.",
            LOG_PATH,
        )
        logger.debug("Trace:", exc_info=True)
        return 2

    return code
