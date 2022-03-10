import argparse


LOG_PATH = "/tmp/codeplag.log"
SUPPORTED_EXTENSIONS = {
    'py': [
        r'.py\b'
    ],
    'cpp': [
        r'.cpp\b',
        r'.c\b',
        r'.h\b'
    ]
}
COMPILE_ARGS = '-x c++ --std=c++11'.split()

try:
    import ccsyspath
    SYSPATH = ccsyspath.system_include_paths('clang++')
    INCARGS = [b'-I' + inc for inc in SYSPATH]
    COMPILE_ARGS = COMPILE_ARGS + INCARGS
except ModuleNotFoundError:
    pass


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
