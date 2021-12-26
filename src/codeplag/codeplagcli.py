import os
import argparse


def dir_path(path_to_directory):
    if not os.path.isdir(path_to_directory):
        print("Directory not found or not a directory")
        exit(1)

    return path_to_directory

def file_path(path_to_file):
    if not os.path.isfile(path_to_file):
        print("File not found or not a file")
        exit(1)

    return path_to_file


def get_parser():
    parser = argparse.ArgumentParser(
                 prog="CODEPLAG",
                 description="Program help to find similar parts of source "
                             "codes for the different languages.",
             )
    parser.add_argument(
        "-t", "--threshold",
        help="Threshold of analyzer which classifies two work as same. "
             "If this number is too large, such as 99, then completely matching jobs will be found. "
             "Otherwise, if this number is small, such as 50, then all work with minimal similarity will be found. ",
        type=int,
        default=65,
        choices=range(50, 100),
        metavar="{50, 51, ..., 99}"
    )
    parser.add_argument(
        '-v', '--version',
        help="Print current version number and exit",
        action="version",
        version="codeplag 0.0.2"
    )

    parser_required = parser.add_argument_group("required options")
    parser_required.add_argument(
        "-ext", "--extension",
        help="Extension responsible for the analyzed programming language",
        type=str,
        choices=["py", "cpp"],
        required=True
    )
    parser_required.add_argument(
        "mode",
        help="Choose one of the following modes of searching plagiarism. "
             "The 'many_to_many' mode may require a lot of free memory.",
        type=str,
        choices=["many_to_many"]
    )

    parser_git = parser.add_argument_group("GitHub options")
    parser_git.add_argument(
        "-ab", "--all_branches",
        help="Searching in all branches",
        action="store_true"
    )
    parser_git.add_argument(
        "-E", "--reg_exp",
        type=str,
        help="A regular expression to filter searching repositories on GitHub"
    )
    # TODO: Checks for correct input
    parser_git.add_argument(
        "-gf", "--git_files",
        metavar="GIT_FILE",
        type=str,
        help="URL to file in a GIT repository",
        nargs="+"
    )
    # TODO: Checks for correct input
    parser_git.add_argument(
        "-g", "--git_user",
        type=str,
        help="GitHub organisation/user name"
    )
    parser_git.add_argument(
        "-gp", "--git_project",
        type=str,
        help="Path to a GIT project"
    )


    parser.add_argument(
        "-f", "--files",
        metavar="FILE",
        type=file_path,
        help="Full path to files on a computer",
        nargs="+"
    )
    parser.add_argument(
        "-d", "--directories",
        metavar="DIRECTORY",
        type=dir_path,
        help="Full path to a local directories with project/files",
        nargs="+"
    )

    return parser
