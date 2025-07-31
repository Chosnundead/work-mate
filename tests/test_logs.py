import os
import pytest
from datetime import datetime
import sys
from pathlib import Path
from io import StringIO

sys.path.append(str(Path(__file__).parent.parent))
from main import load_logs, generate_average_report, parse_args, main


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


def test_load_logs_with_invalid_lines(tmp_path, capsys):
    log_file = tmp_path / "invalid.log"
    data = [
        '{"@timestamp":"2025-06-22T10:00:00+00:00","url":"/api/test","response_time":0.1}',
        "invalid json line",
        '{"@timestamp":"2025-06-22T10:01:00+00:00","url":"/api/test","response_time":"not a number"}',
    ]
    log_file.write_text("\n".join(data))

    logs = load_logs([log_file])
    captured = capsys.readouterr()
    assert "Warning: Invalid record skipped" in captured.err
    assert len(logs) == 1


def test_load_logs_no_matching_date(tmp_path, capsys):
    log_file = tmp_path / "nomatch.log"
    data = [
        '{"@timestamp":"2025-06-22T10:00:00+00:00","url":"/api/test","response_time":0.1}',
    ]
    log_file.write_text("\n".join(data))

    logs = load_logs(
        [log_file], filter_date=datetime.strptime("2025-06-23", "%Y-%m-%d").date()
    )
    captured = capsys.readouterr()
    assert len(logs) == 0


def test_cli_invalid_date_format(monkeypatch, capsys):
    testargs = [
        "main.py",
        "--file",
        "dummy.log",
        "--report",
        "average",
        "--date",
        "invalid-date",
    ]
    monkeypatch.setattr(sys, "argv", testargs)
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "Error: Invalid date format" in captured.err


def test_cli_output_without_tabulate(monkeypatch, tmp_path, capsys):
    log_file = tmp_path / "test.log"
    data = [
        '{"@timestamp":"2025-06-22T10:00:00+00:00","url":"/api/test","response_time":0.1}',
    ]
    log_file.write_text("\n".join(data))

    testargs = ["main.py", "--file", str(log_file), "--report", "average"]
    monkeypatch.setattr(sys, "argv", testargs)

    # Temporarily remove tabulate if present
    import sys as _sys

    tabulate_module = _sys.modules.pop("tabulate", None)

    main()

    # Restore tabulate module if it was present
    if tabulate_module:
        _sys.modules["tabulate"] = tabulate_module

    captured = capsys.readouterr()
    assert "Endpoint" in captured.out
    assert "/api/test" in captured.out
