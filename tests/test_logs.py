import os
import pytest
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from main import load_logs, generate_average_report


@pytest.fixture
def sample_logs(tmp_path):
    log_file = tmp_path / "test.log"
    data = [
        '{"@timestamp":"2025-06-22T10:00:00+00:00","url":"/api/test","response_time":0.1}',
        '{"@timestamp":"2025-06-22T10:01:00+00:00","url":"/api/test","response_time":0.2}',
        '{"@timestamp":"2025-06-23T10:00:00+00:00","url":"/api/other","response_time":0.3}',
    ]
    log_file.write_text("\n".join(data))
    return log_file


def test_load_logs(sample_logs):
    logs = load_logs([sample_logs])
    assert len(logs) == 3

    filtered = load_logs(
        [sample_logs], datetime.strptime("2025-06-22", "%Y-%m-%d").date()
    )
    assert len(filtered) == 2


def test_average_report(sample_logs):
    logs = load_logs([sample_logs])
    report = generate_average_report(logs)

    results = {url: (count, avg) for url, count, avg in report}
    assert results["/api/test"] == (2, 0.15)
    assert results["/api/other"] == (1, 0.3)
