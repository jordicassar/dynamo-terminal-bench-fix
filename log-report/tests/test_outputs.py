import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

LOG_PATH = Path("/app/access.log")
REPORT_PATH = Path("/app/report.json")

LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+\S+\s+\[[^\]]+\]\s+'
    r'"(?P<method>GET|POST|PUT|DELETE|HEAD|PATCH)\s+'
    r'(?P<path>\S+)\s+HTTP/\d(?:\.\d)?"\s+\d{3}\s+\S+$'
)

EXPECTED_KEYS = {
    "total_requests",
    "unique_ips",
    "top_path",
}


def calculate_expected_report() -> dict[str, Any]:
    """Independently calculate the required report from the access log."""
    path_counts: Counter[str] = Counter()
    first_seen: dict[str, int] = {}
    unique_ips: set[str] = set()
    total_requests = 0

    with LOG_PATH.open(encoding="utf-8") as log_file:
        for line_number, raw_line in enumerate(log_file):
            line = raw_line.strip()

            if not line:
                continue

            match = LOG_PATTERN.fullmatch(line)

            if match is None:
                continue

            ip_address = match.group("ip")
            path = match.group("path")

            total_requests += 1
            unique_ips.add(ip_address)
            path_counts[path] += 1
            first_seen.setdefault(path, line_number)

    if path_counts:
        top_path = min(
            path_counts,
            key=lambda path: (
                -path_counts[path],
                first_seen[path],
            ),
        )
    else:
        top_path = ""

    return {
        "total_requests": total_requests,
        "unique_ips": len(unique_ips),
        "top_path": top_path,
    }


def load_report() -> dict[str, Any]:
    """Load the generated report and return its JSON object."""
    assert REPORT_PATH.is_file(), (
        f"Missing required artifact: {REPORT_PATH}"
    )

    try:
        with REPORT_PATH.open(encoding="utf-8") as report_file:
            report = json.load(report_file)
    except json.JSONDecodeError as error:
        raise AssertionError(
            f"{REPORT_PATH} is not valid JSON: {error}"
        ) from error

    assert isinstance(report, dict), (
        "The report root must be a JSON object"
    )

    return report


def test_report_schema() -> None:
    """Criterion 1: The report is valid JSON with exactly the required fields."""
    report = load_report()

    assert set(report) == EXPECTED_KEYS, (
        f"Expected exactly {sorted(EXPECTED_KEYS)}, "
        f"but found {sorted(report)}"
    )


def test_report_field_types() -> None:
    """Criterion 2: Each report field uses its required JSON data type."""
    report = load_report()

    assert type(report["total_requests"]) is int, (
        "total_requests must be an integer"
    )
    assert type(report["unique_ips"]) is int, (
        "unique_ips must be an integer"
    )
    assert type(report["top_path"]) is str, (
        "top_path must be a string"
    )


def test_total_requests() -> None:
    """Criterion 3: total_requests equals the number of valid log entries."""
    report = load_report()
    expected = calculate_expected_report()

    assert report["total_requests"] == expected["total_requests"], (
        f"Expected total_requests={expected['total_requests']}, "
        f"got {report['total_requests']}"
    )


def test_unique_ips() -> None:
    """Criterion 4: unique_ips equals the number of distinct valid client IPs."""
    report = load_report()
    expected = calculate_expected_report()

    assert report["unique_ips"] == expected["unique_ips"], (
        f"Expected unique_ips={expected['unique_ips']}, "
        f"got {report['unique_ips']}"
    )


def test_top_path() -> None:
    """Criterion 5: top_path is the most frequent path with first-seen tie-breaking."""
    report = load_report()
    expected = calculate_expected_report()

    assert report["top_path"] == expected["top_path"], (
        f"Expected top_path={expected['top_path']!r}, "
        f"got {report['top_path']!r}"
    )