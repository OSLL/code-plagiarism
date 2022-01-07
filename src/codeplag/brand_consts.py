import argparse


UTIL_VERSION = "0.0.4"


def _get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version',
        action="version",
        version="{}".format(UTIL_VERSION)
    )

    return parser


if __name__ == '__main__':
    parser = _get_parser()
    parser.parse_args()
