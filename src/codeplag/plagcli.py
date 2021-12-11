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


parser = argparse.ArgumentParser(
             prog="CODEPLAG",
             description="Program help to find similar parts of source "
                         "codes for the different languages.",
         )
parser.add_argument(
    '-v', '--version',
    help="Print current version number and exit",
    action="version",
    version="codeplag 0.0.2"
)

parser.add_argument(
    "-ext", "--extension",
    help="Extension responsible for the analyzed programming language",
    type=str,
    choices=["py", "cpp"],
    default="py",
    required=True
)
parser.add_argument(
    "-f", "--files",
    type=file_path,
    help="Full path to files on a computer",
    nargs="+"
)
parser.add_argument(
    "-gf", "--git_files",
    type=str,
    help="URL to file in a GIT repository"
)
parser.add_argument(
    "-g", "--git",
    type=str,
    help="GitHub organisation/user name"
)
parser.add_argument(
    "-d", "--directory",
    type=dir_path,
    help="Path to a local directory with python project/files",
)
parser.add_argument(
    "-gp", "--git_project",
    type=str,
    help="Path to a GIT project"
)
parser.add_argument(
    "-E", "--reg_exp",
    type=str,
    help="A regular expression to filter searching repositories on GitHub"
)
parser.add_argument(
    "-ab", "--all_branches",
    help="Searching in all branches",
    action="store_true"
)
parser.add_argument(
    "-t", "--threshold",
    help="Threshold of analyzer",
    type=int,
    default=65,
    choices=range(50, 100),
    metavar="{50, 51, ..., 99}"
)

parser.parse_args()
