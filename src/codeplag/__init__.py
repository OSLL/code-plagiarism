import sys

try:
    import pandas as pd

    from codeplag.consts import LOG_PATH
    from codeplag.logger import get_logger
    from codeplag.utils import CodeplagEngine
except ModuleNotFoundError:
    pass
else:
    def main():
        pd.options.display.float_format = '{:,.2%}'.format
        codeplag_util = CodeplagEngine()
        logger = get_logger(__name__, LOG_PATH)
        try:
            codeplag_util.run()
        except Exception:
            logger.error(
                "An unexpected error occurred while running the utility. "
                f"For getting more information, check file '{LOG_PATH}'."
            )
            logger.debug("Trace:", exc_info=True)
            sys.exit(1)
