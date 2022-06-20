import argcomplete
import argparse
import os

from webparsers.github_parser import GitHubParser
from codeplag.logger import get_logger
from codeplag.consts import (
    LOG_PATH, UTIL_NAME, UTIL_VERSION
)

logger = get_logger(__name__, LOG_PATH)


def dir_path(path_to_directory: str) -> str:
    if not os.path.isdir(path_to_directory):
        raise argparse.ArgumentTypeError(
            f"Directory '{path_to_directory}' not found or not a directory."
        )

    return path_to_directory


def file_path(path_to_file: str) -> str:
    if not os.path.isfile(path_to_file):
        raise argparse.ArgumentTypeError(
            f"File '{path_to_file}' not found or not a file."
        )

    return path_to_file


def env_path(path_to_env: str) -> str:
    if not os.path.isfile(path_to_env):
        logger.warning(f"Env file '{path_to_env}' not found or not a file.")
        return ""

    return path_to_env


def github_url(url: str) -> str:
    try:
        GitHubParser.parse_content_url(url)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"'{url}' is incorrect link to GitHub."
        )

    return url


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"{UTIL_NAME.upper()}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Program help to find similar parts of source "
                    "codes for the different languages.",
    )
    parser.add_argument(
        "-env", "--environment",
        help="Path to the environment file with GitHub access token.",
        type=env_path,
        default=".env",
    )
    parser.add_argument(
        "--mode",
        help="Choose one of the following modes of searching plagiarism. "
             "The 'many_to_many' mode may require more free memory.",
        type=str,
        choices=["many_to_many"],
        default="many_to_many"
    )
    parser.add_argument(
        "-sp", "--show_progress",
        help="Show current progress of searching plagiarism.",
        action="store_true"
    )
    parser.add_argument(
        "-t", "--threshold",
        help="Threshold of analyzer which classifies two work as same. "
             "If this number is too large, such as 99, "
             "then completely matching jobs will be found. "
             "Otherwise, if this number is small, such as 50, "
             "then all work with minimal similarity will be found.",
        type=int,
        default=65,
        choices=range(50, 100),
        metavar="{50, 51, ..., 99}"
    )
    parser.add_argument(
        '-v', '--version',
        help="Print current version number and exit.",
        action="version",
        version=f"{UTIL_NAME} {UTIL_VERSION}"
    )

    parser_required = parser.add_argument_group("required options")
    parser_required.add_argument(
        "-ext", "--extension",
        help="Extension responsible for the analyzed programming language.",
        type=str,
        choices=["py", "cpp"],
        required=True
    )

    parser_github = parser.add_argument_group("GitHub options")
    parser_github.add_argument(
        "-ab", "--all-branches",
        help="Searching in all branches",
        action="store_true"
    )
    parser_github.add_argument(
        "-e", "--regexp",
        type=str,
        help="A regular expression to filter searching repositories on GitHub."
    )
    parser_github.add_argument(
        "-gf", "--github-files",
        metavar="GITHUB_FILE",
        type=github_url,
        help="URL to file in a GitHub repository.",
        nargs="+",
        default=[]
    )
    parser_github.add_argument(
        "-gu", "--github-user",
        type=str,
        help="GitHub organisation/user name."
    )
    parser_github.add_argument(
        "-gp", "--github-project-folders",
        metavar="GITHUB_PROJECT_FOLDER",
        type=github_url,
        help="Path to a GitHub project folder.",
        nargs="+",
        default=[]
    )

    parser.add_argument(
        "-f", "--files",
        metavar="FILE",
        type=file_path,
        help="Full path to files on a computer.",
        nargs="+",
        default=[]
    )
    parser.add_argument(
        "-d", "--directories",
        metavar="DIRECTORY",
        type=dir_path,
        help="Full path to a local directories with project/files.",
        nargs="+",
        default=[]
    )

    argcomplete.autocomplete(parser)

    return parser
