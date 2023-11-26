import json
import logging
import math
import uuid
from datetime import datetime
from itertools import combinations
from pathlib import Path
from time import perf_counter, time
from typing import Any, Dict, Generator, List, Literal, Optional, Tuple

import jinja2
import numpy as np
import pandas as pd
from numpy.typing import NDArray

from codeplag.algorithms.featurebased import counter_metric, struct_compare
from codeplag.algorithms.tokenbased import value_jakkar_coef
from codeplag.config import read_settings_conf, write_config, write_settings_conf
from codeplag.consts import (
    CSV_REPORT_COLUMNS,
    CSV_REPORT_FILENAME,
    CSV_SAVE_TICK,
    DEFAULT_GENERAL_REPORT_NAME,
    DEFAULT_LANGUAGE,
    DEFAULT_THRESHOLD,
    DEFAULT_WEIGHTS,
    TEMPLATE_PATH,
)
from codeplag.cplag.utils import CFeaturesGetter
from codeplag.display import print_compare_result
from codeplag.getfeatures import AbstractGetter
from codeplag.pyplag.utils import PyFeaturesGetter
from codeplag.types import (
    ASTFeatures,
    CompareInfo,
    Extension,
    FastMetrics,
    Flag,
    Language,
    Mode,
    ReportsExtension,
    SameFuncs,
    SameHead,
    Settings,
    StructuresInfo,
    WorksReport,
)


def get_compliance_matrix_df(
    compliance_matrix: NDArray,
    head_nodes1: List[str],
    head_nodes2: List[str],
) -> pd.DataFrame:
    data = np.zeros(
        (
            compliance_matrix.shape[0],
            compliance_matrix.shape[1],
        ),
        dtype=np.float64,
    )
    for row in range(compliance_matrix.shape[0]):
        for col in range(compliance_matrix.shape[1]):
            data[row][col] = (
                compliance_matrix[row][col][0] / compliance_matrix[row][col][1]
            )
    compliance_matrix_df = pd.DataFrame(
        data=data, index=head_nodes1, columns=head_nodes2
    )
    return compliance_matrix_df


def convert_similarity_matrix_to_percent_matrix(matrix: NDArray) -> NDArray:
    """Convert compliance matrix of size N x M x 2 to percent 2 dimensional matrix."""
    percent_matrix = np.zeros((matrix.shape[0], matrix.shape[1]), dtype=np.float64)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            percent_matrix[i][j] = round(matrix[i][j][0] / matrix[i][j][1] * 100, 2)
    return percent_matrix


def fast_compare(
    features_f: ASTFeatures,
    features_s: ASTFeatures,
    weights: Tuple[float, float, float, float] = DEFAULT_WEIGHTS,
) -> FastMetrics:
    """The function calculates the similarity of features of two programs
    using four algorithms, calculates their weighted average, and returns
    all of this  in 'FastMetrics' structure.

    @features_f - the features of the first  source file
    @features_s - the features of the second  source file
    @weights - weights of fast metrics that participate in
    counting total similarity coefficient
    """

    jakkar_coef = value_jakkar_coef(features_f.tokens, features_s.tokens)
    ops_res = counter_metric(features_f.operators, features_s.operators)
    kw_res = counter_metric(features_f.keywords, features_s.keywords)
    lits_res = counter_metric(features_f.literals, features_s.literals)
    weighted_average = np.average(
        [jakkar_coef, ops_res, kw_res, lits_res], weights=weights
    )

    fast_metrics = FastMetrics(
        jakkar=jakkar_coef,
        operators=ops_res,
        keywords=kw_res,
        literals=lits_res,
        weighted_average=weighted_average,
    )

    return fast_metrics


def compare_works(
    features1: ASTFeatures, features2: ASTFeatures, threshold: int = 60
) -> CompareInfo:
    """The function returns the result of comparing two files

    @features1 - the features of the first  source file
    @features2 - the features of the second  source file
    @threshold - threshold of plagiarism searcher alarm
    """

    fast_metrics = fast_compare(features1, features2)
    if (fast_metrics.weighted_average * 100.0) < threshold:
        return CompareInfo(fast=fast_metrics)

    compliance_matrix = np.zeros(
        (len(features1.head_nodes), len(features2.head_nodes), 2), dtype=np.int64
    )
    struct_res = struct_compare(
        features1.structure, features2.structure, compliance_matrix
    )
    struct_res = struct_res[0] / struct_res[1]

    structure_info = StructuresInfo(
        similarity=struct_res, compliance_matrix=compliance_matrix
    )

    return CompareInfo(fast=fast_metrics, structure=structure_info)


def serialize_compare_result(
    first_work: ASTFeatures,
    second_work: ASTFeatures,
    compare_info: CompareInfo,
) -> pd.DataFrame:
    assert compare_info.structure is not None

    return pd.DataFrame(
        {
            "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "first_modify_date": first_work.modify_date,
            "second_modify_date": second_work.modify_date,
            "first_path": first_work.filepath.__str__(),
            "second_path": second_work.filepath.__str__(),
            "jakkar": compare_info.fast.jakkar,
            "operators": compare_info.fast.operators,
            "keywords": compare_info.fast.keywords,
            "literals": compare_info.fast.literals,
            "weighted_average": compare_info.fast.weighted_average,
            "struct_similarity": compare_info.structure.similarity,
            "first_heads": [first_work.head_nodes],
            "second_heads": [second_work.head_nodes],
            "compliance_matrix": [compare_info.structure.compliance_matrix.tolist()],
        },
        dtype=object,
    )


def deserialize_head_nodes(head_nodes: str) -> List[str]:
    return [head[1:-1] for head in head_nodes[1:-1].split(", ")]


def deserialize_compare_result(compare_result: pd.Series) -> CompareInfo:
    if isinstance(compare_result.compliance_matrix, str):
        similarity_matrix = np.array(json.loads(compare_result.compliance_matrix))
    else:
        similarity_matrix = np.array(compare_result.compliance_matrix)

    compare_info = CompareInfo(
        fast=FastMetrics(
            jakkar=float(compare_result.jakkar),
            operators=float(compare_result.operators),
            keywords=float(compare_result.keywords),
            literals=float(compare_result.literals),
            weighted_average=np.float64(compare_result.weighted_average),
        ),
        structure=StructuresInfo(
            compliance_matrix=similarity_matrix,
            similarity=float(compare_result.struct_similarity),
        ),
    )

    return compare_info


def replace_minimal_value(same_parts: dict, new_key: str, new_value: float) -> None:
    min_key = next(iter(same_parts))
    min_value = same_parts[min_key]
    for key, value in same_parts.items():
        if value >= min_value:
            continue
        min_value = value
        min_key = key
    if new_value <= min_value:
        return
    del same_parts[min_key]
    same_parts[new_key] = new_value


def get_same_funcs(
    first_heads: List[str],
    second_heads: List[str],
    percent_matrix: NDArray,
    threshold: int = DEFAULT_THRESHOLD,
    n: int = 3,
) -> SameFuncs:
    result = {}
    for i, first_head in enumerate(first_heads):
        result[first_head] = {}
        inner_result = result[first_head]
        for j, second_head in enumerate(second_heads):
            same_percent = percent_matrix[i][j]
            cnt_items = len(inner_result)
            if not cnt_items:
                inner_result[second_head] = same_percent
            elif same_percent < threshold:
                if (
                    cnt_items == 1
                    and inner_result[(key := next(iter(inner_result)))] < same_percent
                ):
                    inner_result[second_head] = same_percent
                    del inner_result[key]
                continue
            elif cnt_items < n:
                inner_result[second_head] = same_percent
            else:
                replace_minimal_value(inner_result, second_head, same_percent)
    for first_head in result:
        result[first_head] = sorted(
            (SameHead(key, value) for key, value in result[first_head].items()),
            key=lambda element: element.percent,
            reverse=True,
        )
    return result


def get_parsed_line(
    df: pd.DataFrame,
) -> Generator[Tuple[pd.Series, CompareInfo, SameFuncs, SameFuncs], None, None]:
    for _, line in df.iterrows():
        cmp_res = deserialize_compare_result(line)
        first_heads = deserialize_head_nodes(line.first_heads)
        second_heads = deserialize_head_nodes(line.second_heads)
        assert cmp_res.structure is not None
        percent_matrix = convert_similarity_matrix_to_percent_matrix(
            cmp_res.structure.compliance_matrix
        )
        same_parts_of_second = get_same_funcs(first_heads, second_heads, percent_matrix)
        same_parts_of_first = get_same_funcs(
            second_heads, first_heads, percent_matrix.T
        )
        if isinstance(line.first_modify_date, float):
            line.first_modify_date = ""
        if isinstance(line.second_modify_date, float):
            line.second_modify_date = ""
        yield line, cmp_res, same_parts_of_second, same_parts_of_first


def create_report(
    df_path: Path,
    save_path: Path,
    threshold: int = DEFAULT_THRESHOLD,
    language: Language = DEFAULT_LANGUAGE,
):
    environment = jinja2.Environment()
    # TODO: use JinJa2 i18n
    template = environment.from_string(TEMPLATE_PATH[language].read_text())
    if save_path.is_dir():
        save_path = save_path / DEFAULT_GENERAL_REPORT_NAME
    save_path.write_text(
        template.render(
            data=get_parsed_line(read_df(df_path)),
            list=list,
            len=len,
            round=round,
            threshold=threshold,
        )
    )


def calc_iterations(count: int, mode: Mode = "many_to_many") -> int:
    if count <= 1:
        return 0

    if mode == "many_to_many":
        return (count * (count - 1)) // 2
    if mode == "one_to_one":
        return math.factorial(count) // 2 * math.factorial(count - 2)

    return 0


def calc_progress(
    iteration: int,
    iterations: int,
    internal_iteration: int = 0,
    internal_iterations: int = 0,
) -> float:
    if iterations == 0:
        return 0.0

    progress = iteration / iterations
    if internal_iterations == 0:
        return progress

    if internal_iteration * internal_iterations:
        progress += internal_iteration / (internal_iterations * iterations)

    return progress


def read_df(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", index_col=0, dtype=object)


class CodeplagEngine:
    def __init__(self, logger: logging.Logger, parsed_args: Dict[str, Any]) -> None:
        self.root: str = parsed_args.pop("root")
        self.command: Optional[str] = None
        # TODO: tmp
        self.logger = logger
        if self.root == "settings":
            self.command = parsed_args.pop(self.root)
            if self.command == "show":
                return

            # Check if all None, print error
            self.environment: Optional[Path] = parsed_args.pop("environment")
            self.reports: Optional[Path] = parsed_args.pop("reports")
            self.threshold: int = parsed_args.pop("threshold")
            self.show_progress: Flag = parsed_args.pop("show_progress")
            self.reports_extension: ReportsExtension = parsed_args.pop(
                "reports_extension"
            )
            self.language: Language = parsed_args.pop("language")
        elif self.root == "report":
            self.path: Path = parsed_args.pop("path")
        else:
            settings_conf = read_settings_conf(logger)
            self._set_features_getter(parsed_args, settings_conf, logger)

            self.mode: str = parsed_args.pop("mode", "many_to_many")
            self.show_progress: Flag = settings_conf["show_progress"]
            self.threshold: int = settings_conf["threshold"]

            self.reports: Optional[Path] = settings_conf.get("reports")
            self.__reports_extension: ReportsExtension = settings_conf[
                "reports_extension"
            ]
            if self.__reports_extension == "csv" and self.reports:
                reports_path = self.reports / CSV_REPORT_FILENAME
                if reports_path.is_file():
                    self.__df_report = read_df(self.reports / CSV_REPORT_FILENAME)
                    self.__start_report_lines = self.__df_report.shape[0]
                else:
                    self.__df_report = pd.DataFrame(
                        columns=CSV_REPORT_COLUMNS, dtype=object
                    )
                    self.__start_report_lines = 0
                self.__csv_last_save = perf_counter()

            self.github_files: List[str] = parsed_args.pop("github_files", [])
            self.github_project_folders: List[str] = parsed_args.pop(
                "github_project_folders", []
            )
            self.github_user: str = parsed_args.pop("github_user", "")

            self.files: List[Path] = parsed_args.pop("files", [])
            self.directories: List[Path] = parsed_args.pop("directories", [])

    def _set_features_getter(
        self,
        parsed_args: Dict[str, Any],
        settings_conf: Settings,
        logger: logging.Logger,
    ) -> None:
        extension: Extension = parsed_args.pop("extension")
        if extension == "py":
            FeaturesGetter = PyFeaturesGetter
        elif extension == "cpp":
            FeaturesGetter = CFeaturesGetter

        self.features_getter: AbstractGetter = FeaturesGetter(
            environment=settings_conf.get("environment"),
            all_branches=parsed_args.pop("all_branches", False),
            logger=logger,
            repo_regexp=parsed_args.pop("repo_regexp", None),
            path_regexp=parsed_args.pop("path_regexp", None),
        )

    def save_result(
        self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        compare_info: CompareInfo,
        reports_extension: ReportsExtension,
    ) -> None:
        if self.reports is None or not self.reports.is_dir():
            self.logger.error(
                "The folder for reports isn't provided or now isn't exists."
            )
            return

        # TODO: use match in the next py version
        if reports_extension == "csv":
            self.__save_result_to_csv(
                first_work,
                second_work,
                compare_info,
            )
        else:
            self.__save_result_to_json(
                first_work,
                second_work,
                compare_info,
            )

    def __save_result_to_json(
        self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        metrics: CompareInfo,
    ) -> None:
        assert metrics.structure is not None

        struct_info_dict = metrics.structure._asdict()
        struct_info_dict["compliance_matrix"] = struct_info_dict[
            "compliance_matrix"
        ].tolist()
        report = WorksReport(
            date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            first_path=first_work.filepath.__str__(),
            second_path=second_work.filepath.__str__(),
            first_heads=first_work.head_nodes,
            second_heads=second_work.head_nodes,
            fast=metrics.fast._asdict(),
            structure=struct_info_dict,
        )
        if first_work.modify_date:
            report["first_modify_date"] = first_work.modify_date
        if second_work.modify_date:
            report["second_modify_date"] = second_work.modify_date

        try:
            report_file = self.reports / f"{uuid.uuid4().hex}.json"  # type: ignore
            write_config(report_file, report)
        except PermissionError:
            self.logger.error("Not enough rights to write reports to the folder.")

    def _write_df_to_fs(self) -> None:
        if self.__reports_extension != "csv" or not self.reports:
            return

        if self.__start_report_lines == self.__df_report.shape[0]:
            self.logger.debug("Nothing new to save to the csv report.")
            return

        report_path = self.reports / CSV_REPORT_FILENAME
        self.logger.debug(f"Saving report to the file '{report_path}'")
        self.__df_report.to_csv(report_path, sep=";")
        self.__start_report_lines = self.__df_report.shape[0]

    def __save_result_to_csv(
        self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        metrics: CompareInfo,
    ) -> None:
        self.__df_report = pd.concat(
            [
                self.__df_report,
                serialize_compare_result(first_work, second_work, metrics),
            ],
            ignore_index=True,
        )
        if perf_counter() - self.__csv_last_save > CSV_SAVE_TICK:
            self._write_df_to_fs()
            # Time to write can be long
            self.__csv_last_save = perf_counter()

    def _do_step(self, work1: ASTFeatures, work2: ASTFeatures) -> None:
        if work1.filepath == work2.filepath:
            return

        work1, work2 = sorted([work1, work2])
        metrics = None
        if self.reports:
            if self.__reports_extension == "csv":
                cache_val = self.__df_report[
                    (self.__df_report.first_path == str(work1.filepath))
                    & (self.__df_report.second_path == str(work2.filepath))
                ]
                if cache_val.shape[0]:
                    metrics = deserialize_compare_result(cache_val.iloc[0])
                    assert metrics.structure is not None
            if metrics is None:
                metrics = compare_works(work1, work2, self.threshold)
                if metrics.structure is None:
                    return
                self.save_result(work1, work2, metrics, self.__reports_extension)
        else:
            metrics = compare_works(work1, work2, self.threshold)
            if metrics.structure is None:
                return

        if (
            metrics.structure is None
            or (metrics.structure.similarity * 100) <= self.threshold
        ):
            print_compare_result(work1, work2, metrics)
        else:
            print_compare_result(
                work1,
                work2,
                metrics,
                get_compliance_matrix_df(
                    metrics.structure.compliance_matrix,
                    work1.head_nodes,
                    work2.head_nodes,
                ),
            )

    def _calc_and_print_progress(
        self,
        iteration: int,
        iterations: int,
        internal_iteration: int = 0,
        internal_iterations: int = 0,
    ) -> None:
        progress = calc_progress(
            iteration, iterations, internal_iteration, internal_iterations
        )
        print(f"Check progress: {progress:.2%}.", end="\r")

    def _settings_show(self) -> None:
        settings_config = read_settings_conf(self.logger)
        table = pd.DataFrame(
            list(settings_config.values()),
            index=[k.capitalize() for k in settings_config],
            columns=pd.Index(["Value"], name="Key"),
        )
        print(table)

    def _settings_modify(self) -> None:
        settings_config = read_settings_conf(self.logger)
        for key in Settings.__annotations__:
            new_value = getattr(self, key, None)
            if new_value is not None:
                if isinstance(new_value, Path):
                    settings_config[key] = new_value.absolute()
                else:
                    settings_config[key] = new_value

            write_settings_conf(settings_config)

    def __check(self) -> None:
        self.logger.debug(
            f"Mode: {self.mode}; Extension: {self.features_getter.extension}."
        )

        begin_time = time()

        features_from_files = self.features_getter.get_from_files(self.files)
        features_from_gh_files = self.features_getter.get_from_github_files(
            self.github_files
        )

        self.logger.info("Starting searching for plagiarism ...")
        if self.mode == "many_to_many":
            works: List[ASTFeatures] = []
            works.extend(features_from_files)
            works.extend(self.features_getter.get_from_dirs(self.directories))
            works.extend(features_from_gh_files)
            works.extend(
                self.features_getter.get_from_github_project_folders(
                    self.github_project_folders
                )
            )
            works.extend(self.features_getter.get_from_users_repos(self.github_user))

            count_works = len(works)
            iterations = calc_iterations(count_works)
            iteration = 0
            for i, work1 in enumerate(works):
                for j, work2 in enumerate(works):
                    if i <= j:
                        continue

                    if self.show_progress:
                        self._calc_and_print_progress(iteration, iterations)
                        iteration += 1

                    self._do_step(work1, work2)
        elif self.mode == "one_to_one":
            combined_elements = filter(
                bool,
                (
                    features_from_files,
                    *self.features_getter.get_from_dirs(
                        self.directories, independent=True
                    ),
                    features_from_gh_files,
                    *self.features_getter.get_from_github_project_folders(
                        self.github_project_folders, independent=True
                    ),
                    *self.features_getter.get_from_users_repos(
                        self.github_user, independent=True
                    ),
                ),
            )
            if self.show_progress:
                combined_elements = list(combined_elements)
                count_sequences = len(combined_elements)
                iterations = calc_iterations(count_sequences, self.mode)
                iteration = 0

            cases = combinations(combined_elements, r=2)
            for case in cases:
                first_sequence, second_sequence = case
                internal_iterations = len(first_sequence) * len(second_sequence)
                internal_iteration = 0
                for work1 in first_sequence:
                    for work2 in second_sequence:
                        if self.show_progress:
                            self._calc_and_print_progress(
                                iteration,  # type: ignore
                                iterations,  # type: ignore
                                internal_iteration,
                                internal_iterations,
                            )
                            internal_iteration += 1

                        self._do_step(work1, work2)
                if self.show_progress:
                    iteration += 1  # type: ignore

        self.logger.debug(f"Time for all {time() - begin_time:.2f}s")
        self.logger.info("Ending searching for plagiarism ...")

    def _report_create(self) -> Literal[0, 1]:
        settings_config = read_settings_conf(self.logger)
        reports_path = settings_config.get("reports")
        if not reports_path:
            self.logger.error(
                "Can't create general report without provided in settings 'report' path."
            )
            return 1
        if settings_config["reports_extension"] == "json":
            self.logger.error("Can create report only when 'reports_extension' is csv.")
            return 1
        if not reports_path.exists():
            self.logger.error(
                f"There is nothing in '{reports_path}' to create a basic html report from."
            )
            return 1
        create_report(
            reports_path / CSV_REPORT_FILENAME,
            self.path,
            threshold=settings_config["threshold"],
            language=settings_config["language"],
        )
        return 0

    def run(self) -> Literal[0, 1]:
        self.logger.debug("Starting codeplag util ...")

        if self.root == "settings":
            if self.command == "show":
                self._settings_show()
            elif self.command == "modify":
                self._settings_modify()
                self._settings_show()
        elif self.root == "report":
            return self._report_create()
        else:
            self.__check()
            self._write_df_to_fs()
        return 0
