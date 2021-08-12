import os
import sys
import argparse


def get_mode():
    parser = argparse.ArgumentParser()
    # Добавить bracnh policy
    # Добавить threshold
    parser.add_argument('-f', "--file", type=str,
                        help="Path to file on a computer")
    parser.add_argument("-F", "--git_file", type=str,
                        help="URL to file in a GIT repository")
    parser.add_argument("-g", "--git", type=str,
                        help="GitHub organisation/user name")
    parser.add_argument("-d", "--dir", type=str,
                        help="Path to a local directory")
    parser.add_argument("-p", "--project", type=str,
                        help="Path to a local project")
    parser.add_argument("-P", "--git_project", type=str,
                        help="Path to a GIT project")
    parser.add_argument("-e", "--reg_exp", type=str,
                        help="Regular expresion (in GitHub mode)")
    parser.add_argument("-cp", "--check_policy", type=int,
                        help="Branches check policy, 0 - only main, 1 - All",
                        choices=[0, 1], default=0)
    parser.add_argument("-t", "--threshold",
                        help="Threshold of analyzer", type=int,
                        default=65, choices=range(50, 100))

    args = parser.parse_args()

    file_path = args.file
    directory = args.dir

    if not directory:
        directory = '/py'
    else:
        if not os.path.exists(directory):
            print('Directory ' + directory + ' doesn\'t exist')
            exit()

    if file_path:
        if not os.path.exists(file_path):
            print('File ' + file_path + ' doesn\'t exist')
            exit()

    if len(sys.argv) == 1:
        mode = -1
    elif args.file and args.git and not (args.git_file or args.dir or
                                         args.project or args.git_project):
        print("Local file compares with files in git repositories")
        mode = 0
    elif args.git_file and args.git and not (args.file or args.dir or
                                             args.project or
                                             args.git_project):
        print("Github file compares with files in git repositories")
        mode = 1
    elif args.file and args.dir and not (args.git_file or args.git or
                                         args.project or args.git_project):
        print("Local file compares with files in a local directory")
        mode = 2
    elif args.git_file and args.dir and not (args.file or args.git or
                                             args.project or
                                             args.git_project):
        print("Git file compares with files in a local directory")
        mode = 3
    elif args.project and args.dir and not (args.file or args.git or
                                            args.git_file or
                                            args.git_project):
        print("Local project compares with a local directory")
        mode = 4
    elif args.project and args.git and not (args.file or args.dir or
                                            args.git_file or
                                            args.git_project):
        print("Local project compares with git repositories")
        mode = 5
    elif args.git_project and args.dir and not (args.file or args.git or
                                                args.git_file or
                                                args.project):
        print("Git project compares with a local directory")
        mode = 6
    elif args.git_project and args.git and not (args.file or args.dir or
                                                args.git_file or
                                                args.project):
        print("Git project compares with git repositories")
        mode = 7
    else:
        print('\n  Invalid arguments. Please use one of the following agrument combination:\n')
        print('  --file PATH --git URL [--reg_exp EXPR] [--check_policy CHECK_POLICY] [--threshold THRESHOLD]           Local file compares with files in git repositories')
        print('  --file PATH --dir PATH [--threshold THRESHOLD]                                                         Local file compares with files in a local directory')
        print('  --git_file URL --git URL [--reg_exp EXPR] [--check_policy CHECK_POLICY] [--threshold THRESHOLD]        Git file compares with files in git repositories')
        print('  --git_file URL --dir PATH [--threshold THRESHOLD]                                                      Git file compares with files in a local directory')
        print('  --project PATH --git URL [--reg_exp EXPR]  [--check_policy CHECK_POLICY] [--threshold THRESHOLD]       Files in local project compares with git repositories')
        print('  --project PATH --dir PATH [--threshold THRESHOLD]                                                      Files in local project compares with files in a local directory')
        print('  --git_project URL --git URL [--reg_exp EXPR]  [--check_policy CHECK_POLICY] [--threshold THRESHOLD]    Files in git project compares with git repositories')
        print('  --git_project URL --dir PATH [--threshold THRESHOLD]                                                   Files in git project compares with files in a local directory')
        print()
        exit()

    return mode, args
