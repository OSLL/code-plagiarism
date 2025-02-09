import re
import subprocess
from typing import Final

import pytest

TARGET_PATTERN = re.compile(r"^[a-zA-Z0-9-]*:\s*")
MAKEFILE_NAME: Final = "Makefile"


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
        if not TARGET_PATTERN.search(line):
            continue
        target_name = line.split(":")[0]
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
    targets_without_help = {
        target for target in makefile_targets if target not in make_help_stdout
    }
    assert (
        not targets_without_help
    ), f"Help message for the '{targets_without_help}' targets not found."
