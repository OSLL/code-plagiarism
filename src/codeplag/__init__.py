from typing import Literal


def main() -> Literal[0, 1]:
    import pandas as pd

    from codeplag.consts import LOG_PATH
    from codeplag.logger import get_logger
    from codeplag.utils import CodeplagEngine

    pd.options.display.float_format = '{:,.2%}'.format
    logger = get_logger(__name__, LOG_PATH)
    codeplag_util = CodeplagEngine(logger)
    try:
        codeplag_util.run()
    except Exception:
        logger.error(
            "An unexpected error occurred while running the utility. "
            f"For getting more information, check file '{LOG_PATH}'."
        )
        logger.debug("Trace:", exc_info=True)
        return 1

    return 0
