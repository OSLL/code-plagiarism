"""This module consist the CLI of the codeplag util and necessary internal classes for it."""

from __future__ import annotations

import argparse
import builtins
import getpass
from pathlib import Path

from typing_extensions import Self

from codeplag.consts import (
    DEFAULT_MODE,
    DEFAULT_REPORT_TYPE,
    EXTENSION_CHOICE,
    LANGUAGE_CHOICE,
    LOG_LEVEL_CHOICE,
    MAX_DEPTH_CHOICE,
    MODE_CHOICE,
    NGRAMS_LENGTH_CHOICE,
    REPORT_TYPE_CHOICE,
    REPORTS_EXTENSION_CHOICE,
    UTIL_NAME,
    UTIL_VERSION,
    WORKERS_CHOICE,
)
from codeplag.types import Settings
from webparsers.types import GitHubContentUrl

# FIXME: dirty hook for using logic without translations
builtins.__dict__["_"] = builtins.__dict__.get("_", str)


class CheckUniqueStore(argparse.Action):
    """Checks that the list of arguments contains no duplicates, then stores."""

    def __call__(
        self: Self,
        _parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: list[str],
        _option_string: str | None = None,
    ) -> None:
        if len(values) > len(set(values)):
            str_values = ", ".join(str(path) for path in values)
            raise argparse.ArgumentError(
                self,
                _(
                    "You cannot specify the same value multiple times. You provided '{values}'."
                ).format(values=str_values),
            )
        setattr(namespace, self.dest, values)


class PasswordPromptAction(argparse.Action):
    def __call__(
        self: Self,
        _parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | None = None,
        _option_string: str | None = None,
    ):
        if values:
            setattr(namespace, self.dest, values)
        else:
            setattr(namespace, self.dest, getpass.getpass(_("Enter MongoDB password: ")))


class DirPath(Path):
    """Raises `argparse.ArgumentTypeError` if the directory doesn't exist."""

    def __new__(cls: type["DirPath"], *args: str, **kwargs) -> Path:
        path = Path(*args, **kwargs).resolve()
        if not path.is_dir():
            raise argparse.ArgumentTypeError(
                _("Directory '{path}' not found or not a directory.").format(path=path)
            )

        return Path.__new__(Path, *args, **kwargs).resolve()


class FilePath(Path):
    """Raises `argparse.ArgumentTypeError` if the file doesn't exist."""

    def __new__(cls: type["FilePath"], *args: str, **kwargs) -> Path:
        path = Path(*args, **kwargs).resolve()
        if not path.is_file():
            raise argparse.ArgumentTypeError(
                _("File '{path}' not found or not a file.").format(path=path)
            )

        return Path.__new__(Path, *args, **kwargs).resolve()


class CodeplagCLI(argparse.ArgumentParser):
    """The argument parser of the codeplag util."""

    def __add_settings_path(self: Self, subparsers: argparse._SubParsersAction) -> None:
        settings = subparsers.add_parser(
            "settings",
            help=_("Modifies and shows static settings of the '{util_name}' util.").format(
                util_name=UTIL_NAME
            ),
        )

        settings_commands = settings.add_subparsers(
            help=_("Settings commands of the '{util_name}' util.").format(util_name=UTIL_NAME),
            required=True,
            metavar="COMMAND",
            dest="settings",
        )

        # settings modify
        settings_modify = settings_commands.add_parser(
            "modify",
            help=_("Manage the '{util_name}' util settings.").format(util_name=UTIL_NAME),
        )
        settings_modify.add_argument(
            "-env",
            "--environment",
            help=_("Path to the environment file with GitHub access token."),
            type=FilePath,
        )
        settings_modify.add_argument(
            "-r",
            "--reports",
            help=_(
                "If defined, then saves reports about suspect works into provided file or "
                "directory. If directory by provided path doesn't exists than saves reports "
                "as a file."
            ),
            metavar="PATH",
            type=Path,
        )
        settings_modify.add_argument(
            "-re",
            "--reports_extension",
            help=_(
                "When provided 'csv' saves similar works compare info into csv file. "
                "When provided 'mongo' saves similar works compare info "
                "and works metadata into MongoDB."
            ),
            type=str,
            choices=REPORTS_EXTENSION_CHOICE,
        )
        settings_modify.add_argument(
            "-sp",
            "--show_progress",
            help=_("Show progress of searching plagiarism."),
            type=int,
            choices=[0, 1],
        )
        settings_modify.add_argument(
            "-so",
            "--short-output",
            help=_(
                "When provided '0' show all check works results in the stdout. "
                "When provided '1' show only new found check works results in the stdout. "
                "When provided '2' do not show check works result in the stdout."
            ),
            type=int,
            choices=[0, 1, 2],
        )
        settings_modify.add_argument(
            "-t",
            "--threshold",
            help=_(
                "Threshold of analyzer which classifies two work as same. "
                "If this number is too large, such as 99, "
                "then completely matching jobs will be found. "
                "Otherwise, if this number is small, such as 50, "
                "then all work with minimal similarity will be found."
            ),
            type=int,
            choices=range(50, 100),
            metavar="{50, 51, ..., 99}",
        )
        settings_modify.add_argument(
            "-md",
            "--max-depth",
            help=_("The maximum depth of the AST structure which play role in calculations."),
            type=int,
            choices=MAX_DEPTH_CHOICE,
        )
        settings_modify.add_argument(
            "-nl",
            "--ngrams-length",
            help=_(
                "The length of N-grams generated to calculate the Jakkar coefficient. A long "
                "length of N-grams reduces the Jakkar coefficient because there are fewer equal "
                "sequences of two works."
            ),
            type=int,
            choices=NGRAMS_LENGTH_CHOICE,
        )
        settings_modify.add_argument(
            "-l",
            "--language",
            help=_("The language of help messages, generated reports, errors."),
            type=str,
            choices=LANGUAGE_CHOICE,
        )
        settings_modify.add_argument(
            "--log-level",
            help=_(
                "Sets the threshold for the '{util_name}' util loggers'. "
                "Logging messages that are less severe than the level will be ignored."
            ).format(util_name=UTIL_NAME),
            type=str,
            choices=LOG_LEVEL_CHOICE,
        )
        settings_modify.add_argument(
            "-w",
            "--workers",
            help=_("The maximum number of processes that can be used to compare works."),
            type=int,
            choices=WORKERS_CHOICE,
        )
        settings_modify.add_argument(
            "-mh",
            "--mongo-host",
            help=_("The host address of the MongoDB server."),
            type=str,
        )
        settings_modify.add_argument(
            "-mpt",
            "--mongo-port",
            help=_("The port of the MongoDB."),
            type=int,
            choices=range(1, 65536),
            metavar="{1, 2, ..., 65535}",
        )
        settings_modify.add_argument(
            "-mu",
            "--mongo-user",
            help=_("The username for connecting to the MongoDB server."),
            type=str,
        )
        settings_modify.add_argument(
            "-mps",
            "--mongo-pass",
            help=_("The password for connecting to the MongoDB server. If empty - hide input."),
            type=str,
            action=PasswordPromptAction,
            nargs="?",
        )

        # settings show
        settings_commands.add_parser(
            "show",
            help=_("Show the '{util_name}' util settings.").format(util_name=UTIL_NAME),
        )

    def __add_check_path(self: Self, subparsers: argparse._SubParsersAction) -> None:
        check = subparsers.add_parser("check", help=_("Start searching similar works."))
        check.add_argument(
            "-d",
            "--directories",
            metavar="DIRECTORY",
            type=DirPath,
            help=_("Absolute or relative path to a local directories with project files."),
            nargs="+",
            action=CheckUniqueStore,
            default=[],
        )
        check.add_argument(
            "-f",
            "--files",
            metavar="FILE",
            type=FilePath,
            help=_("Absolute or relative path to files on a computer."),
            nargs="+",
            action=CheckUniqueStore,
            default=[],
        )
        check.add_argument(
            "--mode",
            help=_(
                "Choose one of the following modes of searching plagiarism. "
                "The 'many_to_many' mode may require more free memory."
            ),
            type=str,
            choices=MODE_CHOICE,
            default=DEFAULT_MODE,
        )
        check.add_argument(
            "-pe",
            "--path-regexp",
            help=_(
                "A regular expression for filtering checked works by name. "
                "Used with options 'directories', 'github-user' and 'github-project-folders'."
            ),
            type=str,
        )
        check.add_argument(
            "--ignore-threshold",
            action="store_true",
            help=_("Ignore the threshold when checking of works."),
        )

        check_required = check.add_argument_group("required options")
        check_required.add_argument(
            "-ext",
            "--extension",
            help=_("Extension responsible for the analyzed programming language."),
            type=str,
            choices=EXTENSION_CHOICE,
            required=True,
        )

        check_github = check.add_argument_group("GitHub options")
        check_github.add_argument(
            "-ab",
            "--all-branches",
            help=_("Searching in all branches."),
            action="store_true",
        )
        check_github.add_argument(
            "-re",
            "--repo-regexp",
            type=str,
            help=_("A regular expression to filter searching repositories on GitHub."),
        )
        check_github.add_argument(
            "-gf",
            "--github-files",
            metavar="GITHUB_FILE",
            type=GitHubContentUrl,
            help=_("URL to file in a GitHub repository."),
            nargs="+",
            action=CheckUniqueStore,
            default=[],
        )
        check_github.add_argument(
            "-gu", "--github-user", type=str, help=_("GitHub organization/user name.")
        )
        check_github.add_argument(
            "-gp",
            "--github-project-folders",
            metavar="GITHUB_PROJECT_FOLDER",
            type=GitHubContentUrl,
            help=_("URL to a GitHub project folder."),
            nargs="+",
            action=CheckUniqueStore,
            default=[],
        )

    def __add_report_path(self: Self, subparsers: argparse._SubParsersAction) -> None:
        report = subparsers.add_parser(
            "report",
            help=_(
                _(
                    "Handling generated by the {util_name} reports as "
                    "creating html report file or show it on console."
                ).format(util_name=UTIL_NAME)
            ),
        )

        report_commands = report.add_subparsers(
            help=_("Report commands of the '{util_name}' util.").format(util_name=UTIL_NAME),
            required=True,
            metavar="COMMAND",
            dest="report",
        )

        # report create
        report_create = report_commands.add_parser(
            "create",
            help=_("Generate general report from created some time ago report files."),
        )
        report_create.add_argument(
            "-p",
            "--path",
            help=_(
                "Path to save generated report. If it's a directory, then create a file in it."
            ),
            required=True,
            type=Path,
        )
        report_create.add_argument(
            "-t",
            "--type",
            help=_("Type of the created report file."),
            type=str,
            choices=REPORT_TYPE_CHOICE,
            default=DEFAULT_REPORT_TYPE,
        )
        report_create.add_argument(
            "-frp",
            "--first-root-path",
            help=_(
                "Path to first compared works. "
                "Can be path to directory or URL to the project folder."
            ),
            type=str,
            required=False,
        )
        report_create.add_argument(
            "-srp",
            "--second-root-path",
            help=_(
                "Path to second compared works. "
                "Can be path to directory or URL to the project folder."
            ),
            type=str,
            required=False,
        )

    def __init__(self: Self) -> None:
        super(CodeplagCLI, self).__init__(
            prog=UTIL_NAME,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description=_(
                "Program help to find similar parts of source codes for the different languages."
            ),
        )
        self.add_argument(
            "-v",
            "--version",
            help=_("Print current version number and exit."),
            action="version",
            version=f"{UTIL_NAME} {UTIL_VERSION}",
        )

        subparsers = self.add_subparsers(
            help=_("Commands help."),
            parser_class=argparse.ArgumentParser,
            required=True,
            metavar="COMMAND",
            dest="root",
        )

        self.__add_settings_path(subparsers)
        self.__add_check_path(subparsers)
        self.__add_report_path(subparsers)

    def validate_args(self: Self, parsed_args: argparse.Namespace) -> None:
        parsed_args_dict = vars(parsed_args)
        root = parsed_args_dict.get("root")
        if root is None:
            self.error(_("No command is provided; please choose one from the available (--help)."))
        command = parsed_args_dict.get(root)
        if (
            root == "settings"
            and command == "modify"
            and not any(
                key in Settings.__annotations__
                for key in parsed_args_dict
                if parsed_args_dict.get(key) is not None
            )
        ):
            self.error(_("There is nothing to modify; please provide at least one argument."))
        elif root == "check":
            if parsed_args.repo_regexp and not parsed_args.github_user:
                self.error(
                    _("The'repo-regexp' option requires the provided 'github-user' option.")
                )
            elif parsed_args.path_regexp and not (
                parsed_args.directories
                or parsed_args.github_user
                or parsed_args.github_project_folders
            ):
                self.error(
                    _(
                        "The'path-regexp' option requires the provided 'directories', "
                        "'github-user', or 'github-project-folder' options."
                    )
                )
        elif (
            root == "report"
            and command == "create"
            and not all([parsed_args.first_root_path, parsed_args.second_root_path])
            and any([parsed_args.first_root_path, parsed_args.second_root_path])
        ):
            self.error(_("All paths must be provided."))

    def parse_args(self: Self, args: list[str] | None = None) -> argparse.Namespace:
        parsed_args = super(CodeplagCLI, self).parse_args(args)
        self.validate_args(parsed_args)
        return parsed_args
