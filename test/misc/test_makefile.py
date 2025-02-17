import re
import subprocess
from typing import Final

import pytest

TARGET_PATTERN = re.compile(r"^(?P<target_name>[a-zA-Z0-9-]+):\s*")
MAKEFILE_HELP_TARGET_PATTERN = re.compile(r"^  (?P<target_name>[a-zA-Z0-9-]+)\s+")
MAKEFILE_NAME: Final = "Makefile"
MAKEFILE_HELP_TARGETS_IGNORE: Final = {"make"}


@pytest.fixture
def makefile_targets() -> set[str]:
    result = subprocess.run(
        ["make", "-qp"],
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    targets = set()
    for line in result.stdout.splitlines():
        target_match = TARGET_PATTERN.search(line)
        if not target_match:
            continue
        target_name = target_match.group("target_name")
        if target_name == MAKEFILE_NAME:
            continue
        targets.add(target_name)
    assert targets, "No targets found, maybe error occurred."
    return targets


def test_makefile_consist_help_msgs_for_all_targets(makefile_targets: set[str]):
    make_help_stdout = subprocess.run(
        ["make", "help"],
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout
    makefile_help_targets = []
    for line in make_help_stdout.splitlines():
        target_match = MAKEFILE_HELP_TARGET_PATTERN.search(line)
        if not target_match:
            continue
        makefile_help_targets.append(target_match.group("target_name"))
    unique_makefile_help_targets = set(makefile_help_targets)
    assert len(makefile_help_targets) == len(
        unique_makefile_help_targets
    ), "Some targets' help messages repeats."
    unique_makefile_help_targets -= MAKEFILE_HELP_TARGETS_IGNORE
    targets_without_help_message = makefile_targets - unique_makefile_help_targets
    targets_which_only_in_the_makehelp = unique_makefile_help_targets - makefile_targets
    assert unique_makefile_help_targets == makefile_targets, (
        f"Help message for the '{targets_without_help_message}' targets not found. "
        f"Help message for the '{targets_which_only_in_the_makehelp}' targets found."
    )
