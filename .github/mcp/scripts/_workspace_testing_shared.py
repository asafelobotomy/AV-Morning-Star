from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path


def unwrap_runner_argv(argv: list[str]) -> list[str]:
    if len(argv) < 2:
        return argv
    executable = Path(argv[0]).name
    if executable in {"poetry", "uv"} and len(argv) >= 3 and argv[1] == "run":
        return argv[2:]
    if executable in {"pnpm", "yarn"} and len(argv) >= 3 and argv[1] == "exec":
        return argv[2:]
    if executable == "npm" and len(argv) >= 3 and argv[1] == "exec":
        return argv[3:] if len(argv) >= 4 and argv[2] == "--" else argv[2:]
    if executable == "npx":
        return argv[2:] if len(argv) >= 3 and argv[1] == "--" else argv[1:]
    return argv


def detect_test_runner(argv: list[str]) -> str:
    runner_argv = unwrap_runner_argv(argv)
    if not runner_argv:
        return "unknown"
    executable = Path(runner_argv[0]).name
    if executable in {"pytest", "py.test"}:
        return "pytest"
    if executable == "unittest":
        return "unittest"
    prefix, _, suffix = executable.partition(".")
    is_python = executable in {"python", "python3"} or (prefix in {"python", "python3"} and suffix.isdigit())
    if not is_python:
        return "unknown"
    for index, value in enumerate(runner_argv[:-1]):
        if value != "-m":
            continue
        module_name = runner_argv[index + 1]
        if module_name == "pytest":
            return "pytest"
        if module_name == "unittest":
            return "unittest"
    return "unknown"


def classify_test_run(argv: list[str], returncode: int, stdout: str = "", stderr: str = "") -> str:
    if returncode == 0:
        return "completed"
    runner = detect_test_runner(argv)
    output = "\n".join(part for part in (stdout, stderr) if part)
    if runner == "pytest":
        return {
            1: "tests_failed",
            2: "interrupted",
            3: "internal_error",
            4: "usage_error",
            5: "no_tests_collected",
        }.get(returncode, "runner_error")
    if runner == "unittest":
        if re.search(r"^(?:FAIL|ERROR):\s+", output, re.MULTILINE) or re.search(r"^FAILED\b", output, re.MULTILINE):
            return "tests_failed"
        if re.search(r"Ran\s+0\s+tests", output, re.IGNORECASE):
            return "no_tests_collected"
        return "runner_error"
    return "runner_error"


def supports_test_discovery(argv: list[str]) -> bool:
    return detect_test_runner(argv) == "pytest"


def supports_typed_targets(argv: list[str]) -> bool:
    runner = detect_test_runner(argv)
    if runner == "pytest":
        return True
    if runner != "unittest":
        return False
    runner_argv = unwrap_runner_argv(argv)
    if not runner_argv:
        return False
    executable = Path(runner_argv[0]).name
    if executable == "unittest":
        return len(runner_argv) == 1
    prefix, _, suffix = executable.partition(".")
    is_python = executable in {"python", "python3"} or (prefix in {"python", "python3"} and suffix.isdigit())
    if not is_python:
        return False
    if runner_argv[:3] != [runner_argv[0], "-m", "unittest"]:
        return False
    # `python -m unittest discover ...` and similar subcommands are not safe for blind positional appends.
    return len(runner_argv) == 3


def parse_discovered_test_ids(text: str, runner: str) -> list[str]:
    if runner != "pytest" or not text:
        return []
    test_ids: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("=") or "collected" in line:
            continue
        if "::" not in line and not line.endswith(".py"):
            continue
        if any(character.isspace() for character in line):
            continue
        test_ids.append(line)
    return test_ids


def parse_test_summary(text: str) -> dict:
    summary = {"format": "unknown", "passed": 0, "failed": 0, "errors": 0, "total": 0, "firstFailure": None}
    if not text:
        return summary
    pytest_counts = re.findall(r"(\d+)\s+(passed|failed|errors?|skipped)", text, re.IGNORECASE)
    if pytest_counts:
        summary["format"] = "pytest"
        skipped = 0
        for raw_count, label in pytest_counts:
            count = int(raw_count)
            label_lower = label.lower()
            if label_lower == "passed":
                summary["passed"] += count
            elif label_lower == "failed":
                summary["failed"] += count
            elif label_lower in {"error", "errors"}:
                summary["errors"] += count
            elif label_lower == "skipped":
                skipped += count
        summary["total"] = summary["passed"] + summary["failed"] + summary["errors"] + skipped
        if failed_match := re.search(r"^FAILED\s+(.+?)\s+-\s+(.+)$", text, re.MULTILINE):
            summary["firstFailure"] = f"{failed_match.group(1)}: {failed_match.group(2)}"
        return summary
    if ran_match := re.search(r"Ran\s+(\d+)\s+tests", text, re.IGNORECASE):
        summary["format"] = "unittest"
        summary["total"] = int(ran_match.group(1))
        result_match = re.search(r"^(OK|FAILED)\s*(?:\((.+)\))?$", text, re.MULTILINE)
        if result_match and result_match.group(1) == "OK":
            skipped = 0
            for part in (result_match.group(2) or "").split(","):
                key, _, value = part.strip().partition("=")
                if key == "skipped" and value.isdigit():
                    skipped = int(value)
            summary["passed"] = max(0, summary["total"] - skipped)
        elif result_match:
            for part in (result_match.group(2) or "").split(","):
                key, _, value = part.strip().partition("=")
                if key == "failures" and value.isdigit():
                    summary["failed"] = int(value)
                elif key == "errors" and value.isdigit():
                    summary["errors"] = int(value)
            summary["passed"] = max(0, summary["total"] - summary["failed"] - summary["errors"])
        if failed_match := re.search(r"^(?:FAIL|ERROR):\s+(\S+)", text, re.MULTILINE):
            summary["firstFailure"] = failed_match.group(1)
    return summary


def parse_coverage_xml_file(path: Path) -> dict:
    root = ET.parse(str(path)).getroot()
    line_rate = float(root.get("line-rate", 0.0))
    lines_valid = int(root.get("lines-valid", 0))
    lines_covered = int(root.get("lines-covered", 0))
    zero_coverage_files = [
        item.get("filename", "unknown")
        for item in root.iter("class")
        if float(item.get("line-rate", 1.0)) == 0.0
    ][:20]
    return {
        "lineRate": round(line_rate, 4),
        "percentCovered": round(line_rate * 100, 1),
        "linesValid": lines_valid,
        "linesCovered": lines_covered,
        "zeroCoverageFiles": zero_coverage_files,
    }
