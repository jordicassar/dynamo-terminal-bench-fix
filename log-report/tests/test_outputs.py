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

EXPECTED_KEYS = {"total_requests", "unique_ips", "top_path"}


def calculate_expected_report() -> dict[str, Any]:
    path_counts: Counter[str] = Counter()
    unique_ips: set[str] = set()
    total_requests = 0

    with LOG_PATH.open(encoding="utf-8") as log_file:
        for raw_line in log_file:
            line = raw_line.strip()
            if not line:
                continue

            match = LOG_PATTERN.match(line)
            if match is None:
                continue

            total_requests += 1
            unique_ips.add(match.group("ip"))
            path_counts[match.group("path")] += 1

    top_path = path_counts.most_common(1)[0][0] if path_counts else ""

    return {
        "total_requests": total_requests,
        "unique_ips": len(unique_ips),
        "top_path": top_path,
    }


def load_report() -> dict[str, Any]:
    try:
        with REPORT_PATH.open(encoding="utf-8") as report_file:
            report = json.load(report_file)
    except json.JSONDecodeError as error:
        raise AssertionError(
            f"{REPORT_PATH} is not valid JSON: {error}"
        ) from error

    assert isinstance(report, dict), "Report root must be a JSON object"
    return report


def test_report_exists() -> None:
    """The agent must write the required /app/report.json artifact."""
    assert REPORT_PATH.is_file(), f"Missing required artifact: {REPORT_PATH}"


def test_report_is_valid_json_object() -> None:
    """The report must be valid JSON with an object at the root."""
    report = load_report()
    assert isinstance(report, dict), "Report root must be a JSON object"


def test_report_has_exact_schema() -> None:
    """The report must contain exactly the three required fields."""
    report = load_report()

    assert set(report) == EXPECTED_KEYS, (
        f"Expected exactly {sorted(EXPECTED_KEYS)}, "
        f"but found {sorted(report)}"
    )


def test_report_field_types() -> None:
    """The report fields must use the required JSON data types."""
    report = load_report()

    assert type(report["total_requests"]) is int, (
        "total_requests must be a JSON integer"
    )
    assert type(report["unique_ips"]) is int, (
        "unique_ips must be a JSON integer"
    )
    assert isinstance(report["top_path"], str), (
        "top_path must be a JSON string"
    )


def test_total_requests() -> None:
    """total_requests must equal the number of valid access-log entries."""
    report = load_report()
    expected = calculate_expected_report()

    assert report["total_requests"] == expected["total_requests"], (
        f"Expected total_requests={expected['total_requests']}, "
        f"got {report['total_requests']}"
    )


def test_unique_ips() -> None:
    """unique_ips must equal the number of distinct valid client IPs."""
    report = load_report()
    expected = calculate_expected_report()

    assert report["unique_ips"] == expected["unique_ips"], (
        f"Expected unique_ips={expected['unique_ips']}, "
        f"got {report['unique_ips']}"
    )


def test_top_path() -> None:
    """top_path must equal the most frequently requested valid URL path."""
    report = load_report()
    expected = calculate_expected_report()

    assert report["top_path"] == expected["top_path"], (
        f"Expected top_path={expected['top_path']!r}, "
        f"got {report['top_path']!r}"
    )