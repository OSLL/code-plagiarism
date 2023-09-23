import os
import re
from datetime import datetime
from time import perf_counter
from typing import Literal, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from codeplag.algorithms.featurebased import counter_metric, struct_compare
from codeplag.algorithms.stringbased import gst
from codeplag.algorithms.tokenbased import value_jakkar_coef
from codeplag.pyplag.utils import get_ast_from_content, get_features_from_ast
from decouple import Config, RepositoryEnv
from scipy.optimize import curve_fit
from webparsers.github_parser import GitHubParser


def square_func(x: float, a: float, b: float, c: float) -> float:
    return a * x**2 + b * x + c


def cube_func(x: float, a: float, b: float, c: float, d: float) -> float:
    return a * x**3 + b * x**2 + c * x + d


def quart_func(x: float, a: float, b: float, c: float, d: float, e: float) -> float:
    return a * x**4 + b * x**3 + c * x**2 + d * x + e


def remove_unnecessary_blank_lines(source_code: str) -> str:
    pattern = r"\n+"
    return re.sub(pattern, "\n", source_code)


def get_data_from_dir(
    path: str = "./data", max_count_lines: Optional[int] = None
) -> pd.DataFrame:
    df = pd.DataFrame()
    for filename in os.listdir(path):
        if not re.search(r".csv$", filename):
            continue

        tmp_df = pd.read_csv(os.path.join(path, filename), sep=";", index_col=0)
        df = df.append(tmp_df, ignore_index=True)

    if max_count_lines:
        return df[df.count_lines_without_blank_lines < max_count_lines]

    return df


def save_works_from_repo_url(url: str, check_policy: bool = True) -> None:
    current_repo_name = url.split("/")[-1]
    env_config = Config(RepositoryEnv("../../.env"))
    gh = GitHubParser(
        file_extensions=(re.compile(r".py$"),),
        check_all=check_policy,
        access_token=env_config.get("ACCESS_TOKEN"),
    )
    files = list(gh.get_files_generator_from_repo_url(url))
    files = [(remove_unnecessary_blank_lines(file.code), file.link) for file in files]

    df = pd.DataFrame(
        {
            "content": [file_[0] for file_ in files[:-1]],
            "link": [file_[1] for file_ in files[:-1]],
            "extension": ["py"] * (len(files) - 1),
            "repo_name": [current_repo_name] * (len(files) - 1),
            "content_len": [len(file_[0]) for file_ in files[:-1]],
            "content_len_without_blank": [
                len(file_[0].replace(" ", "").replace("\n", "").replace("\t", ""))
                for file_ in files[:-1]
            ],
            "count_lines_without_blank_lines": [
                len(file_[0].splitlines()) for file_ in files[:-1]
            ],
        }
    )
    df = df[df["count_lines_without_blank_lines"] > 5]
    df.to_csv(os.path.join("./data/", current_repo_name + ".csv"), sep=";")


def get_time_to_meta(df: pd.DataFrame, iterations: int = 10) -> pd.DataFrame:
    count_lines = []
    to_meta_time = []
    for index, content in df[
        ["content", "link", "count_lines_without_blank_lines"]
    ].iterrows():
        print(index, " " * 20, end="\r")
        for _ in range(iterations):
            tree = get_ast_from_content(content[0], content[1])
            if tree is None:
                break
            try:
                start = perf_counter()
                get_features_from_ast(tree, content[1])
                end = perf_counter() - start
                to_meta_time.append(end)
                count_lines.append(content[2])
            except Exception:
                break

    output = pd.DataFrame({"count_lines": count_lines, "times": to_meta_time})

    return output


def plot_and_save_result(
    df: pd.DataFrame,
    xlabel: str,
    ylabel: str,
    title: str,
    what: str,
    trend: Literal["linear", "n^2", "n^3", "n^4"] = "linear",
) -> None:
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

    if trend == "linear":
        z = np.polyfit(unique_count_lines, mean_times, 1)
        p = np.poly1d(z)
        plt.plot(
            unique_count_lines, p(unique_count_lines), "r--", label="Линейный тренд."
        )
    elif trend == "n^2":
        popt_cons, _ = curve_fit(
            square_func,
            unique_count_lines,
            mean_times,
            bounds=([-np.inf, 0.0, 0.0], [np.inf, 0.1**100, 0.1**100]),
        )
        p = np.poly1d(popt_cons)
        plt.plot(
            unique_count_lines,
            p(unique_count_lines),
            "r--",
            label="Квадратичный тренд.",
        )
    elif trend == "n^3":
        popt_cons, _ = curve_fit(
            cube_func,
            unique_count_lines,
            mean_times,
            bounds=(
                [-np.inf, 0.0, 0.0, 0.0],
                [np.inf, 0.1**100, 0.1**100, 0.1**100],
            ),
        )
        p = np.poly1d(popt_cons)
        plt.plot(
            unique_count_lines, p(unique_count_lines), "r--", label="Кубический тренд."
        )
    elif trend == "n^4":
        popt_cons, _ = curve_fit(
            quart_func,
            unique_count_lines,
            mean_times,
            bounds=(
                [-np.inf, 0.0, 0.0, 0.0, 0.0],
                [np.inf, 0.1**100, 0.1**100, 0.1**100, 0.1**100],
            ),
        )
        p = np.poly1d(popt_cons)
        plt.plot(unique_count_lines, p(unique_count_lines), "r--", label="n^4.")
    else:
        raise Exception(f"Incorrect tred '{trend}'.")

    rolling = pd.DataFrame(
        {"unique_count_lines": unique_count_lines, "mean_times": mean_times}
    )
    num_window = 20
    plt.plot(
        rolling.unique_count_lines,
        rolling.mean_times.rolling(window=num_window).mean(),
        label=f"Скользящее среднее по {num_window}ти замерам.",
    )

    plt.ylabel(ylabel, fontsize=15)
    plt.xlabel(xlabel, fontsize=15)
    plt.title(title, fontsize=17)
    plt.legend(loc="upper left")
    plt.savefig(
        "./graphics/need_time_{}_{}.png".format(
            what, datetime.now().strftime("%d%m%Y_%H%M%S")
        )
    )


def get_time_algorithms(
    df: pd.DataFrame,
    work,
    iterations: int = 5,
    metric: Literal["fast", "gst", "structure"] = "fast",
) -> pd.DataFrame:
    count_lines = []
    times = []
    tree1 = get_ast_from_content(work.content, work.link)
    if tree1 is None:
        raise Exception("Unexpected error when parsing first work.")

    features1 = get_features_from_ast(tree1, work.link)
    for index, content in df[
        ["content", "link", "count_lines_without_blank_lines"]
    ].iterrows():
        for _ in range(iterations):
            print(index, " " * 20, end="\r")
            tree2 = get_ast_from_content(content[0], content[1])
            if tree2 is None:
                continue
            try:
                features2 = get_features_from_ast(tree2, content[1])
            except Exception:
                continue

            if metric == "fast":
                start = perf_counter()
                value_jakkar_coef(features1.tokens, features2.tokens)
                counter_metric(features1.operators, features2.operators)
                counter_metric(features1.keywords, features2.keywords)
                counter_metric(features1.literals, features2.literals)
                end = perf_counter() - start
                times.append(end)
            elif metric == "gst":
                start = perf_counter()
                gst(features1.tokens, features2.tokens, 6)
                end = perf_counter() - start
                times.append(end)
            elif metric == "structure":
                start = perf_counter()
                struct_compare(features1.structure, features2.structure)
                end = perf_counter() - start
                times.append(end)
            else:
                raise Exception("Incorrect metric!")

            count_lines.append(content[2])

    output = pd.DataFrame({"count_lines": count_lines, "times": times})

    return output
