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
from src.pyplag.utils import compare_file_pair, get_files_path_from_directory
from src.webparsers.github_parser import GitHubParser
from termcolor import colored
from mode import get_mode
from src.logger import get_logger
from src.pyplag.const import LOG_PATH

logger = get_logger(__name__, LOG_PATH)

logger.info("Pyplag starting...")

pd.options.display.float_format = '{:,.2%}'.format

mode, args = get_mode()

logger.info("Working mode = " + str(mode))

tree1 = None
start_eval = perf_counter()
weights = np.array([1, 0.4, 0.4, 0.4], dtype=np.float32)

if mode == 0:
    # Local file compares with files in git repositories
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
    # Github file compares with files in git repositories
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
    # Local file compares with files in a local directory
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
        compare_file_pair(args.file, filename, args.threshold, weights)

        iterration += 1
        print('  {:.2%}'.format(iterration / iterrations), end="\r")

elif mode == 3:
    # GitHub file compares with files in a local directory
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
    # Local project compares with a local directory
    # Use variablse 'project' and 'directory'
    dir_files = os.listdir(args.dir)
    dir_files = list(filter(lambda x: (x.endswith('.py')), dir_files))
    project_files = get_files_path_from_directory(args.project)

    count_files = len(dir_files) * len(project_files)
    if count_files == 0:
        print("One of the folder is empty")
        exit()

    iterrations = (count_files)
    iterration = 0

    for row in np.arange(0, len(dir_files), 1):
        if args.dir[-1] != '/':
            args.dir += '/'

        filename = args.dir + dir_files[row]
        for file in project_files:
            compare_file_pair(file, filename, args.threshold, weights)

            iterration += 1
            print('  {:.2%}'.format(iterration / iterrations), end="\r")

elif mode == 5:
    # Local project compares with git repositories
    # Use variables 'project' and 'git'
    gh = GitHubParser(file_extensions=['py'], check_policy=args.check_policy)

    project_files = get_files_path_from_directory(args.project)
    if len(project_files) == 0:
        print("Folder with project not consist py files.")
        exit()

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

            for filepath in project_files:
                tree1 = get_ast_from_filename(filepath)
                if tree1 is None:
                    continue

                features1 = ASTFeatures()
                features1.visit(tree1)

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
                                      filepath,
                                      url_file)

        iteration += 1
        print(repo_url, " ... OK")
        print(" " * 40, end="\r")
        print('In repos {:.2%}'.format(iteration / count_iter), end="\r")

elif mode == 6:
    # Git project compares with a local directory
    # Use variables 'git_project' and 'direcrory'
    gh = GitHubParser(file_extensions=['py'], check_policy=args.check_policy)
    project_files = list(gh.get_files_generator_from_dir_url(args.git_project))
    count_files_in_project = len(project_files)
    if count_files_in_project == 0:
        print("Project not consist py files.")
        exit()

    dir_files = os.listdir(args.dir)
    dir_files = list(filter(lambda x: (x.endswith('.py')), dir_files))

    count_files = len(dir_files) * count_files_in_project
    if count_files == 0:
        print("One of the folder is empty")
        exit()

    iterrations = (count_files)
    iterration = 0

    for row in np.arange(0, len(dir_files), 1):
        if args.dir[-1] != '/':
            args.dir += '/'

        filename = args.dir + dir_files[row]
        for file, url_file in project_files:
            tree1 = get_ast_from_content(file, url_file)
            tree2 = get_ast_from_filename(filename)
            if tree1 is None:
                continue
            if tree2 is None:
                continue

            features1 = ASTFeatures()
            features1.visit(tree1)
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
                                  url_file,
                                  filename)

            iterration += 1
            print('  {:.2%}'.format(iterration / iterrations), end="\r")

elif mode == 7:
    # Git project compares with git repositories
    # Use variables 'git_project' and 'git'
    gh = GitHubParser(file_extensions=['py'], check_policy=args.check_policy)
    project_files = list(gh.get_files_generator_from_dir_url(args.git_project))
    if len(project_files) == 0:
        print("Project not consist py files.")
        exit()

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

            for file2, url_file2 in project_files:
                tree1 = get_ast_from_content(file2, url_file2)
                if tree1 is None:
                    continue

                features1 = ASTFeatures()
                features1.visit(tree1)

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
                                      url_file2,
                                      url_file)

        iteration += 1
        print(repo_url, " ... OK")
        print(" " * 40, end="\r")
        print('In repos {:.2%}'.format(iteration / count_iter), end="\r")

else:
    logger.warning("Incorrect arguments!")
    print("Check the arguments (use --help)")
    logger.info("Pyplag stopping...")
    exit()

print("Analysis complete")
print('Time for all {:.2f}'.format(perf_counter() - start_eval))
