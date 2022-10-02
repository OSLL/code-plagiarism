"""
This module consist the CLI of the codeplag util and
necessary internal classes for it.
"""
import argparse
from pathlib import Path
from typing import List, Optional

from codeplag.consts import MODE_CHOICE, UTIL_NAME, UTIL_VERSION
from webparsers.types import GitHubContentUrl


class CheckUniqueStore(argparse.Action):
    """Checks that the list of arguments contains no duplicates, then stores"""

    def __call__(
        self,
        _parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: List[str],
        _option_string: Optional[str] = None
    ):
        if len(values) > len(set(values)):
            raise argparse.ArgumentError(
                self,
                "You cannot specify the same value multiple times. "
                f"You provided {values}",
            )
        setattr(namespace, self.dest, values)


class DirPath(Path):
    """Path that raising argparse.ArgumentTypeError when parsing CLI
    arguments if directory is not exists.
    """

    def __new__(cls, *args, **kwargs):
        path = Path(*args, **kwargs)
        if not path.is_dir():
            raise argparse.ArgumentTypeError(
                f"Directory '{path}' not found or not a directory."
            )

        return Path.__new__(Path, *args, **kwargs)


class FilePath(Path):
    """Path that raising argparse.ArgumentTypeError when parsing CLI
    arguments if file is not exists.
    """

    def __new__(cls, *args, **kwargs):
        path = Path(*args, **kwargs)
        if not path.is_file():
            raise argparse.ArgumentTypeError(
                f"File '{path}' not found or not a file."
            )

        return Path.__new__(Path, *args, **kwargs)


class EnvPath(Path):
    """Path that returns None when parsing CLI
    arguments if file is not exists.
    """

    def __new__(cls, *args, **kwargs):
        path = Path(*args, **kwargs)
        if not path.is_file():
            return None

        return Path.__new__(Path, *args, **kwargs)


class CodeplagCLI(argparse.ArgumentParser):
    """The argument parser of the codeplag util."""

    def __init__(self):
        super(CodeplagCLI, self).__init__(
            prog=UTIL_NAME,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Program help to find similar parts of source "
                        "codes for the different languages.",
        )
        self.add_argument(
            "-env", "--environment",
            help="Path to the environment file with GitHub access token.",
            type=EnvPath,
            default=".env",
        )
        self.add_argument(
            "--mode",
            help="Choose one of the following modes of searching plagiarism. "
                 "The 'many_to_many' mode may require more free memory.",
            type=str,
            choices=MODE_CHOICE,
            default="many_to_many"
        )
        self.add_argument(
            '-rd', '--reports_directory',
            help="If defined, then saves reports about suspect works "
                 "into provided path.",
            type=DirPath
        )
        self.add_argument(
            "-sp", "--show_progress",
            help="Show current progress of searching plagiarism.",
            action="store_true"
        )
        self.add_argument(
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
        self.add_argument(
            '-v', '--version',
            help="Print current version number and exit.",
            action="version",
            version=f"{UTIL_NAME} {UTIL_VERSION}"
        )

        parser_required = self.add_argument_group("required options")
        parser_required.add_argument(
            "-ext", "--extension",
            help="Extension responsible for the analyzed "
                 "programming language.",
            type=str,
            choices=["py", "cpp"],
            required=True
        )

        parser_github = self.add_argument_group("GitHub options")
        parser_github.add_argument(
            "-ab", "--all-branches",
            help="Searching in all branches",
            action="store_true"
        )
        parser_github.add_argument(
            "-e", "--regexp",
            type=str,
            help="A regular expression to filter "
                 "searching repositories on GitHub."
        )
        parser_github.add_argument(
            "-gf", "--github-files",
            metavar="GITHUB_FILE",
            type=GitHubContentUrl,
            help="URL to file in a GitHub repository.",
            nargs="+",
            action=CheckUniqueStore,
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
            type=GitHubContentUrl,
            help="Path to a GitHub project folder.",
            nargs="+",
            action=CheckUniqueStore,
            default=[]
        )

        self.add_argument(
            "-f", "--files",
            metavar="FILE",
            type=FilePath,
            help="Full path to files on a computer.",
            nargs="+",
            action=CheckUniqueStore,
            default=[]
        )
        self.add_argument(
            "-d", "--directories",
            metavar="DIRECTORY",
            type=DirPath,
            help="Full path to a local directories with project/files.",
            nargs="+",
            action=CheckUniqueStore,
            default=[]
        )
