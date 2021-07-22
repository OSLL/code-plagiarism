import context
import ast
import os
import sys
import numpy as np
import pandas as pd

from time import perf_counter
from src.pyplag.tfeatures import ASTFeatures
from src.pyplag.utils import get_ast_from_content, run_compare
from src.pyplag.utils import get_ast_from_filename, print_compare_res
from src.webparsers.github_parser import GitHubParser
from termcolor import colored
from mode import get_mode

pd.options.display.float_format = '{:,.2%}'.format


def compare_file_pair(filename, filename2, threshold):
    '''
        Function compares 2 files
        filename - path to the first file (dir/file1.py)
        filename2 - path the second file (dir/file2.py)
    '''
    tree1 = get_ast_from_filename(filename)
    tree2 = get_ast_from_filename(filename2)

    if tree1 is None:
        return
    if tree2 is None:
        return

    features1 = ASTFeatures()
    features2 = ASTFeatures()
    features1.visit(tree1)
    features2.visit(tree2)

    metrics = run_compare(features1, features2)
    total_similarity = np.sum(metrics * weights) / weights.sum()

    if (total_similarity * 100) > threshold:
        print_compare_res(metrics, total_similarity,
                          features1.structure,
                          features2.structure,
                          features1.from_num,
                          features2.from_num,
                          features1.seq_ops,
                          features2.seq_ops,
                          features1.tokens,
                          features2.tokens,
                          filename.split('/')[-1],
                          filename2.split('/')[-1])

    return (metrics, total_similarity)


#(mode, file_path, git_file, git, directory, project, git_project, reg_exp,
# check_policy, threshold) = get_mode()

mode, args = get_mode()

tree1 = None
start_eval = perf_counter()
weights = np.array([1, 0.4, 0.4, 0.4], dtype=np.float32)

if mode == 0:
    # Local file comapres with files in git repositories
    # Use variablse 'file_path' and 'git'
    # Когда отсутствует подключение к интернету, программа падает

    tree1 = get_ast_from_filename(args.file)
    if tree1 is None:
        exit()

    features1 = ASTFeatures()
    features1.visit(tree1)

    gh = GitHubParser(file_extensions=['py'], check_policy=args.check_policy)
    repos = gh.get_list_of_repos(owner=args.git, reg_exp=args.reg_exp)
    count_iter = len(repos)
    iteration = 0
    for repo, repo_url in repos.items():
        print(repo_url)
        files = gh.get_files_generator_from_repo_url(repo_url)
        for file, url_file in files:
            tree2 = get_ast_from_content(file, url_file)
            if tree2 is None:
                continue

            features2 = ASTFeatures()
            features2.visit(tree2)
            metrics = run_compare(features1, features2)
            total_similarity = np.sum(metrics * weights) / weights.sum()

            if (total_similarity * 100) > args.threshold:
                print_compare_res(metrics, total_similarity,
                                  features1.structure,
                                  features2.structure,
                                  features1.from_num,
                                  features2.from_num,
                                  features1.seq_ops,
                                  features2.seq_ops,
                                  features1.tokens,
                                  features2.tokens,
                                  args.file.split('\\')[-1],
                                  url_file)

        iteration += 1
        print(repo_url, " ... OK")
        print(" " * 40, end="\r")
        print('In repos {:.2%}'.format(iteration / count_iter), end="\r")

elif mode == 1:
    # Github file comapres with files in git repositories
    # Use variablse 'git_file' and 'git'
    gh = GitHubParser(file_extensions=['py'], check_policy=args.check_policy)
    tree1 = get_ast_from_content(gh.get_file_from_url(args.git_file)[0],
                                 args.git_file)
    if tree1 is None:
        exit()

    features1 = ASTFeatures()
    features1.visit(tree1)

    repos = gh.get_list_of_repos(owner=args.git, reg_exp=args.reg_exp)
    count_iter = len(repos)
    iteration = 0
    for repo, repo_url in repos.items():
        print(repo_url)
        files = gh.get_files_generator_from_repo_url(repo_url)
        for file, url_file in files:
            tree2 = get_ast_from_content(file, url_file)
            if tree2 is None:
                continue

            features2 = ASTFeatures()
            features2.visit(tree2)
            metrics = run_compare(features1, features2)
            total_similarity = np.sum(metrics * weights) / weights.sum()

            if (total_similarity * 100) > args.threshold:
                print_compare_res(metrics, total_similarity,
                                  features1.structure,
                                  features2.structure,
                                  features1.from_num,
                                  features2.from_num,
                                  features1.seq_ops,
                                  features2.seq_ops,
                                  features1.tokens,
                                  features2.tokens,
                                  args.git_file,
                                  url_file)

        iteration += 1
        print(repo_url, " ... OK")
        print(" " * 40, end="\r")
        print('In repos {:.2%}'.format(iteration / count_iter), end="\r")

elif mode == 2:
    # Local file comapres with files in a local directory
    # Use variablse 'file_path' and 'directory'

    files = os.listdir(args.dir)
    files = list(filter(lambda x: (x.endswith('.py')), files))

    count_files = len(files)
    if count_files == 0:
        print("Folder is empty")
        exit()

    iterrations = (count_files)
    iterration = 0

    for row in np.arange(0, count_files, 1):
        if args.dir[-1] != '/':
            args.dir += '/'

        filename = args.dir + files[row]
        compare_file_pair(args.file, filename, args.threshold)

        iterration += 1
        print('  {:.2%}'.format(iterration / iterrations), end="\r")

elif mode == 3:
    # GitHub file comapres with files in a local directory
    # Use variablse 'git_file' and 'directory'
    gh = GitHubParser(file_extensions=['py'], check_policy=args.check_policy)
    tree1 = get_ast_from_content(gh.get_file_from_url(args.git_file)[0],
                                 args.git_file)
    if tree1 is None:
        exit()

    features1 = ASTFeatures()
    features1.visit(tree1)

    files = os.listdir(args.dir)
    files = list(filter(lambda x: (x.endswith('.py')), files))

    count_files = len(files)
    if count_files == 0:
        print("Folder is empty")
        exit()

    iterrations = (count_files)
    iterration = 0

    for row in np.arange(0, count_files, 1):
        if args.dir[-1] != '/':
            args.dir += '/'

        filename = args.dir + files[row]
        tree2 = get_ast_from_filename(filename)
        if tree2 is None:
            continue

        features2 = ASTFeatures()
        features2.visit(tree2)

        metrics = run_compare(features1, features2)
        total_similarity = np.sum(metrics * weights) / weights.sum()

        if (total_similarity * 100) > args.threshold:
            print_compare_res(metrics, total_similarity,
                              features1.structure,
                              features2.structure,
                              features1.from_num,
                              features2.from_num,
                              features1.seq_ops,
                              features2.seq_ops,
                              features1.tokens,
                              features2.tokens,
                              args.git_file,
                              filename.split('/')[-1])

        iterration += 1
        print('  {:.2%}'.format(iterration / iterrations), end="\r")

elif mode == 4:
    # Local project comapres with a local directory
    # Use variablse 'project' and 'directory'
    print('This mode is not ready yet')
    #TODO

elif mode == 5:
    # Local project comapres with git repositories
    # Use variables 'project' and 'git'
    print('This mode is not ready yet')
    #TODO

elif mode == 6:
    # Git project comapres with a local directory
    # Use variables 'git_project' and 'direcrory'
    print('This mode is not ready yet')
    #TODO

elif mode == 7:
    #Git project comapres with git repositories
    # Use variables 'git_project' and 'git'
    print('This mode is not ready yet')
    #TODO

else:
    print("Check the arguments (use --help)")
    exit()

print("Analysis complete")
print('Time for all {:.2f}'.format(perf_counter() - start_eval))
