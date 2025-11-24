import argparse
import csv
import os
import sys
from abc import ABC
from collections import defaultdict

from tabulate import tabulate


REPORTS = {"performance": "PerformanceReport"}


def parse_file(file) -> list[dict]:
    field_funcs = {
        "name": str,
        "position": str,
        "completed_tasks": int,
        "performance": float,
        "skills": str,
        "team": str,
        "experience_years": int,
    }
    data = []
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {field: field_funcs[field](val) for field, val in row.items()}
            row["skills"] = list(map(str.strip, row["skills"].split(",")))
            data.append(row)
    return data


class Report(ABC):
    def __init__(self, data, *args, **kwargs):
        self.data = data

    def get_report(self, *args, **kwargs) -> str:
        raise NotImplementedError()


class PerformanceReport(Report):
    def get_report(self) -> str:
        sums_by_pos = defaultdict(float)
        counts_by_pos = defaultdict(int)
        for row in self.data:
            position = row["position"]
            sums_by_pos[position] += row["performance"]
            counts_by_pos[position] += 1
        report_data = [
            {"position": position, "avg_performance": sum_ / counts_by_pos[position]}
            for position, sum_ in sums_by_pos.items()
        ]
        report_data.sort(key=lambda x: x["avg_performance"], reverse=True)
        return tabulate(report_data, headers="keys")


def main():
    parser = argparse.ArgumentParser(description="Report generator.")
    parser.add_argument("--files", nargs="*", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    data = []
    for file in args.files:
        if not os.path.exists(file):
            print(f"File {file} does not exist")
            sys.exit(1)
        file_data = parse_file(file)
        data += file_data

    report_class_name = REPORTS.get(args.report, None)
    report_class = globals().get(report_class_name, None)
    if report_class is None:
        print(f"Report {args.report} not found")
        sys.exit(1)
    report = report_class(data)
    print(report.get_report())


if __name__ == "__main__":
    main()
