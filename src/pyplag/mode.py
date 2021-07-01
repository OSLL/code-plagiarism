import os
import sys
import argparse

# 0 mode works with GitHub repositoryes
# 1 mode works with directory in user computer

def get_mode():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', "--file", type=str, 
                        help = "Path to file on a computer")
    parser.add_argument("-F", "--git_file", type=str, 
                        help = "URL to file in a GIT repository")
    parser.add_argument("-g", "--git", type=str, 
                        help = "GitHub organisation URL")                    
    parser.add_argument("-d", "--dir", type=str, 
                        help = "Path to a local directory")
    parser.add_argument("-p", "--project", type=str, 
                        help = "Path to a local project")
    parser.add_argument("-P", "--git_project", type=str, 
                        help = "Path to a GIT project")
    parser.add_argument("-e", "--reg_exp", type=str, 
                        help = "Regular expresion (in GitHub mode)")

    args = parser.parse_args()
    
    file_path = args.file
    git_file = args.git_file
    git = args.git
    directory = args.dir
    project = args.project
    git_project = args.git_project
    reg_exp = args.reg_exp

    if not directory:
        directory = '/py'
    else:
        if not os.path.exists(directory):
            print('Directory {directory} isn\'t exist')
            exit()


    if len(sys.argv) == 1:
        exit()
    elif args.file and args.git and not (args.git_file or args.dir or args.project or args.git_project):
        print("Local file comapres with files in git repositories")
        mode = 0
    elif args.git_file and args.git and not (args.file or args.dir or args.project or args.git_project):
        print("Github file comapres with files in git repositories")
        mode = 1
    elif args.file and args.dir and not (args.git_file or args.git or args.project or args.git_project):
        print("Local file comapres with files in a local directory")
        mode = 2
    elif args.git_file and args.dir and not (args.file or args.git or args.project or args.git_project):
        print("Git file comapres with files in a local directory")
        mode = 3
    elif args.project and args.dir and not (args.file or args.git or args.git_file or args.git_project):
        print("Local project comapres with a local directory")
        mode = 4
    elif args.project and args.git and not (args.file or args.dir or args.git_file or args.git_project):
        print("Local project comapres with git repositories")
        mode = 5
    elif args.git_project and args.dir and not (args.file or args.git or args.git_file or args.project):
        print("Git project comapres with a local directory")
        mode = 6
    elif args.git_project and args.git and not (args.file or args.dir or args.git_file or args.project):
        print("Git project comapres with git repositories")
        mode = 7
    else: 
        print('\n  Invalid arguments. Please use one of the following agrument combination:\n')    
        print('  --file PATH --git URL [--reg_exp EXPR]         Local file comapres with files in git repositories')    
        print('  --file PATH --dir PATH                         Local file comapres with files in a local directory')    
        print('  --git_file URL --git URL [--reg_exp EXPR]      Git file comapres with files in git repositories')    
        print('  --git_file URL --dir PATH                      Git file comapres with files in a local directory')    
        print('  --project PATH --git URL [--reg_exp EXPR]      Files in local project comapre with git repositories')    
        print('  --project PATH --dir PATH                      Files in local project comapre with files in a local directory')    
        print('  --git_project URL --git URL [--reg_exp EXPR]   Files in git project comapre with git repositories')   
        print('  --git_project URL --dir PATH                   Files in git project comapre with files in a local directory')   
        print()
        exit()

    return (mode, file_path, git_file, git, directory, project, git_project, reg_exp)
