import os
import argparse


FILE_DOWNLOAD_PATH = '/tmp/codeplag/download.out'
TMP_FILES_PATH = '/tmp/codeplag'
LOG_PATH = os.path.join(TMP_FILES_PATH, 'codeplag.log')
SUPPORTED_EXTENSIONS = {
    'py': [
        r'.py$'
    ],
    'cpp': [
        r'.cpp$',
        r'.c$',
        r'.h$'
    ]
}


def _get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--get_log_path',
        action='store_const',
        const=LOG_PATH
    )
    parser.add_argument(
        '--get_tpm_files_path',
        action='store_const',
        const=TMP_FILES_PATH
    )

    return parser


if __name__ == '__main__':
    parser = _get_parser()

    args = vars(parser.parse_args())
    if args.get('get_log_path'):
        print(args.get('get_log_path'))
        exit(0)
    if args.get('get_tpm_files_path'):
        print(args.get('get_tpm_files_path'))
        exit(0)
