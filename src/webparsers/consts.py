import argparse


LOG_PATH = "/tmp/webparsers.log"


def _get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--get_log_path',
        action='store_const',
        const=LOG_PATH
    )

    return parser


if __name__ == '__main__':
    parser = _get_parser()

    args = vars(parser.parse_args())
    if args.get('get_log_path'):
        print(args.get('get_log_path'))
        exit(0)
