# Log File Analyzer

This project is a command-line tool for analyzing JSON-formatted log files. It processes one or more log files, optionally filters log records by date, and generates reports based on the log data.

## Features

-   Load and parse multiple JSON log files
-   Filter log records by date (YYYY-MM-DD)
-   Generate reports on log data (currently supports average response time per endpoint)
-   Pretty-print reports using the `tabulate` library if installed
-   Includes automated tests using `pytest`

## Usage

Run the analyzer with the following command-line arguments:

```
python main.py --file <logfile1> [--file <logfile2> ...] --report average [--date YYYY-MM-DD]
```

-   `--file`: Path to a log file. Can be specified multiple times to analyze multiple files.
-   `--report`: Type of report to generate. Currently, only `average` is supported.
-   `--date`: (Optional) Filter log records by the specified date (format: YYYY-MM-DD).

Example:

```
python main.py --file example1.log --file example2.log --report average --date 2025-06-22
```

## Log File Format

The log files should contain one JSON object per line with at least the following fields:

-   `@timestamp`: ISO 8601 timestamp string
-   `url`: The endpoint URL accessed
-   `response_time`: Response time in seconds (float)

Example log line:

```json
{
    "@timestamp": "2025-06-22T10:00:00+00:00",
    "url": "/api/test",
    "response_time": 0.123
}
```

## Testing

Tests are implemented using `pytest`. To run the tests, install pytest and run:

```
pytest
```

## Dependencies

-   Python 3.7+
-   Optional: `tabulate` library for pretty-printing reports

Install `tabulate` with:

```
pip install tabulate
```

## License

This project is provided as-is without any warranty.
