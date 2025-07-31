import argparse
import json
import sys
from datetime import datetime
from collections import defaultdict


def parse_args():
    """Разбирает аргументы командной строки"""
    parser = argparse.ArgumentParser(description="Log file analyzer")
    parser.add_argument(
        "--file",
        action="append",
        required=True,
        help="Log file path (can be specified multiple times)",
    )
    parser.add_argument(
        "--report", required=True, choices=["average"], help="Report type to generate"
    )
    parser.add_argument("--date", help="Filter records by date (YYYY-MM-DD)")
    return parser.parse_args()


def load_logs(file_paths, filter_date=None):
    """Загружает и фильтрует логи из файлов"""
    logs = []
    for file_path in file_paths:
        try:
            with open(file_path, "r") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        if filter_date:
                            ts = datetime.fromisoformat(record["@timestamp"])
                            if ts.date() != filter_date:
                                continue
                        # Validate response_time can be converted to float
                        _ = float(record["response_time"])
                        logs.append(record)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        print(
                            f"Warning: Invalid record skipped in {file_path}",
                            file=sys.stderr,
                        )
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}", file=sys.stderr)
            sys.exit(1)
    return logs


def generate_average_report(logs):
    """Генерирует отчет со средним временем ответа"""
    endpoint_stats = defaultdict(lambda: {"count": 0, "total_time": 0.0})

    for record in logs:
        try:
            url = record["url"]
            response_time = float(record["response_time"])
            endpoint_stats[url]["count"] += 1
            endpoint_stats[url]["total_time"] += response_time
        except (KeyError, ValueError):
            continue

    report = []
    for url, stats in endpoint_stats.items():
        avg_time = stats["total_time"] / stats["count"]
        report.append((url, stats["count"], round(avg_time, 3)))

    report.sort(key=lambda x: x[0])
    return report


def main():
    args = parse_args()
    filter_date = None

    if args.date:
        try:
            filter_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD", file=sys.stderr)
            sys.exit(1)

    logs = load_logs(args.file, filter_date)

    if not logs:
        print("No data found for processing")
        return

    if args.report == "average":
        report_data = generate_average_report(logs)
        headers = ["Endpoint", "Request count", "Average response time"]

        try:
            from tabulate import tabulate

            print(tabulate(report_data, headers, tablefmt="grid"))
        except ImportError:
            print("\t".join(headers))
            for row in report_data:
                print("\t".join(map(str, row)))


if __name__ == "__main__":
    main()
