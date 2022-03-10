import argparse


UTIL_VERSION = "0.0.5"
UTIL_NAME = "codeplag"


def _get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version',
        action="version",
        version="{}".format(UTIL_VERSION)
    )
    parser.add_argument(
        '--util_name',
        action='store_const',
        const=UTIL_NAME
    )

    return parser


if __name__ == '__main__':
    parser = _get_parser()

    args = vars(parser.parse_args())
    if args.get('util_name'):
        print(args.get('util_name'))
        exit(0)
