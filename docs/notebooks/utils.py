import re
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from datetime import datetime
from time import perf_counter
from codeplag.pyplag.utils import get_ast_from_content, get_features_from_ast
from codeplag.algorithms.tokenbased import value_jakkar_coef
from codeplag.algorithms.stringbased import gst
from codeplag.algorithms.featurebased import counter_metric, struct_compare

from webparsers.github_parser import GitHubParser
from decouple import Config, RepositoryEnv


def square_func(x, a, b, c):
    return a * x**2 + b * x + c


def cube_func(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d


def quart_func(x, a, b, c, d, e):
    return a * x**4 + b * x**3 + c * x**2 + d * x + e


def remove_unnecessary_blank_lines(source_code):
    pattern = r"\n+"
    return re.sub(pattern, "\n", source_code)


def get_data_from_dir(path='./data', max_count_lines=None):
    df = pd.DataFrame()
    for filename in os.listdir(path):
        if not re.search(r'.csv$', filename):
            continue

        tmp_df = pd.read_csv(os.path.join(path, filename), sep=';', index_col=0)
        df = df.append(tmp_df, ignore_index=True)

    if max_count_lines:
        return df[df.count_lines_without_blank_lines < max_count_lines]

    return df


def save_works_from_repo_url(url, check_policy=1):
    current_repo_name = url.split('/')[-1]
    env_config = Config(RepositoryEnv('../../.env'))
    gh = GitHubParser(file_extensions=[r'.py$'], check_policy=check_policy, access_token=env_config.get('ACCESS_TOKEN'))
    files = list(gh.get_files_generator_from_repo_url(url))
    files = [(remove_unnecessary_blank_lines(file[0]), file[1]) for file in files]

    df = pd.DataFrame(
        {
            'content': [file_[0] for file_ in files[:-1]],
            'link': [file_[1] for file_ in files[:-1]],
            'extension': ['py'] * (len(files) - 1),
            'repo_name': [current_repo_name] * (len(files) - 1),
            'content_len': [len(file_[0]) for file_ in files[:-1]],
            'content_len_without_blank': [len(file_[0].replace(' ', '').replace('\n', '').replace('\t', '')) for file_ in files[:-1]],
            'count_lines_without_blank_lines': [len(file_[0].splitlines()) for file_ in files[:-1]]
        }
    )
    df = df[df['count_lines_without_blank_lines'] > 5]
    df.to_csv(os.path.join('./data/', current_repo_name + '.csv'), sep=';')


def get_time_to_meta(df, iterations=10):
    count_lines = []
    to_meta_time = []
    for (index, content) in df[['content', 'link', 'count_lines_without_blank_lines']].iterrows():
        print(index, " " * 20, end='\r')
        for i in range(iterations):
            tree = get_ast_from_content(content[0], content[1])
            try:
                start = perf_counter()
                features1 = get_features_from_ast(tree)
                end = perf_counter() - start
                to_meta_time.append(end)
                count_lines.append(content[2])
            except:
                break

    output = pd.DataFrame(
        {
            'count_lines': count_lines,
            'times': to_meta_time
        }
    )

    return output


def plot_and_save_result(df, xlabel, ylabel, title, what,
                         trend='linear'):
    # Simple Moving average
    unique_count_lines = np.unique(df.count_lines)
    mean_times = []
    for i in range(unique_count_lines.shape[0]):
        summ = 0
        count = 0
        for count_line, time in zip(df.count_lines, df.times):
            if unique_count_lines[i] == count_line:
                summ += time
                count += 1
        mean_times.append(summ / count)

    plt.figure(figsize=(12, 12), dpi=80)
    # plt.plot(unique_count_lines, mean_times, label='Среднее')

    if trend == 'linear':
        z = np.polyfit(unique_count_lines, mean_times, 1)
        p = np.poly1d(z)
        plt.plot(unique_count_lines, p(unique_count_lines),"r--", label='Линейный тренд.')
    elif trend == 'n^2':
        popt_cons, _ = curve_fit(square_func, unique_count_lines, mean_times, bounds=([-np.inf, 0., 0.], [np.inf, 0.1 ** 100, 0.1 ** 100]))
        p = np.poly1d(popt_cons)
        plt.plot(unique_count_lines, p(unique_count_lines),"r--", label='Квадратичный тренд.')
    elif trend == 'n^3':
        popt_cons, _ = curve_fit(cube_func, unique_count_lines, mean_times, bounds=([-np.inf, 0., 0., 0.], [np.inf, 0.1 ** 100, 0.1 ** 100, 0.1 ** 100]))
        p = np.poly1d(popt_cons)
        plt.plot(unique_count_lines, p(unique_count_lines),"r--", label='Кубический тренд.')
    elif trend == 'n^4':
        popt_cons, _ = curve_fit(quart_func, unique_count_lines, mean_times, bounds=([-np.inf, 0., 0., 0., 0.], [np.inf, 0.1 ** 100, 0.1 ** 100, 0.1 ** 100, 0.1 ** 100]))
        p = np.poly1d(popt_cons)
        plt.plot(unique_count_lines, p(unique_count_lines),"r--", label='n^4.')

    rolling = pd.DataFrame(
        {
            'unique_count_lines': unique_count_lines,
            'mean_times': mean_times
        }
    )
    num_window = 20
    plt.plot(rolling.unique_count_lines, rolling.mean_times.rolling(window=num_window).mean(), label=f'Скользящее среднее по {num_window}ти замерам.')

    plt.ylabel(ylabel, fontsize=15)
    plt.xlabel(xlabel, fontsize=15)
    plt.title(title, fontsize=17)
    plt.legend(loc='upper left')
    plt.savefig('./graphics/need_time_{}_{}.png'.format(what, datetime.now().strftime("%d%m%Y_%H%M%S")))


def get_time_algorithms(df, work, iterations=5, metric='fast'):
    count_lines = []
    times = []
    tree1 = get_ast_from_content(work.content, work.link)
    features1 = get_features_from_ast(tree1)
    for (index, content) in df[['content', 'link', 'count_lines_without_blank_lines']].iterrows():
        for iteration in range(iterations):
            print(index, " " * 20, end='\r')
            tree2 = get_ast_from_content(content[0], content[1])
            try:
                features2 = get_features_from_ast(tree2)
            except:
                continue

            if metric == 'fast':
                start = perf_counter()
                jakkar_coef = value_jakkar_coef(features1.tokens, features2.tokens)
                ops_res = counter_metric(features1.operators, features2.operators)
                kw_res = counter_metric(features1.keywords, features2.keywords)
                lits_res = counter_metric(features1.literals, features2.literals)
                end = perf_counter() - start 
                times.append(end)
            elif metric == 'gst':
                start = perf_counter()
                gst(features1.tokens, features2.tokens, 6)
                end = perf_counter() - start 
                times.append(end)
            elif metric == 'structure':
                start = perf_counter()
                struct_compare(features1.structure, features2.structure)
                end = perf_counter() - start
                times.append(end)
            else:
                print('Incorrect metric!')
                return 1

            count_lines.append(content[2])

    output = pd.DataFrame(
        {
            'count_lines': count_lines,
            'times': times
        }
    )

    return output
