from unittest.mock import MagicMock, mock_open, patch

import pytest
from workmate.main import PerformanceReport, Report, main, parse_file


@pytest.fixture
def employees2():
    return [
        {
            "name": "David Chen",
            "position": "Mobile Developer",
            "completed_tasks": 36,
            "performance": 4.6,
            "skills": ["Swift", "Kotlin", "React Native", "iOS"],
            "team": "Mobile Team",
            "experience_years": 3,
        },
        {
            "name": "Elena Popova",
            "position": "Backend Developer",
            "completed_tasks": 43,
            "performance": 4.8,
            "skills": ["Java", "Spring Boot", "MySQL", "Redis"],
            "team": "API Team",
            "experience_years": 4,
        },
    ]


@pytest.fixture
def employees4_2fields():
    return [
        {"position": "Mobile Developer", "performance": 4.9},
        {"position": "Mobile Developer", "performance": 4.7},
        {"position": "Backend Developer", "performance": 4.8},
        {"position": "Backend Developer", "performance": 4.6},
    ]


def test_parse_file_not_exists():
    with pytest.raises(OSError):
        parse_file("8241b751-6c4d-4c35-85bc-0135ded13a56")


def test_parse_file_field_missing():
    reader_mock = MagicMock()
    reader_mock.return_value = [
        {"name": "a", "position": "b"},
        {"name": "c", "position": "d"},
    ]
    with pytest.raises(KeyError), patch("csv.DictReader", reader_mock), patch(
        "workmate.main.open", MagicMock()
    ):
        parse_file("8241b751-6c4d-4c35-85bc-0135ded13a56")


def test_file(employees2):
    csv_text = """name,position,completed_tasks,performance,skills,team,experience_years
David Chen,Mobile Developer,36,4.6,"Swift, Kotlin, React Native, iOS",Mobile Team,3
Elena Popova,Backend Developer,43,4.8,"Java, Spring Boot, MySQL, Redis",API Team,4"""
    with patch("builtins.open", mock_open(read_data=csv_text)):
        data = parse_file("8241b751-6c4d-4c35-85bc-0135ded13a56")
        assert employees2 == data


def test_report_class():
    data = [
        {"name": "a", "position": "b"},
        {"name": "c", "position": "d"},
    ]
    report = Report(data)
    assert report.data == data
    with pytest.raises(NotImplementedError):
        report.get_report()


def test_performance_report_class(employees4_2fields):
    report = PerformanceReport(employees4_2fields)
    assert report.data == employees4_2fields

    expected = [
        {"position": "Mobile Developer", "avg_performance": 4.8},
        {"position": "Backend Developer", "avg_performance": 4.7},
    ]
    with patch("workmate.main.tabulate", lambda *args, **kwargs: args[0]):
        result = report.get_report()
        result = list(map(pytest.approx, result))
        assert expected == result


def test_main_file_not_exists(capsys):
    args = MagicMock()
    args.files = ["abc"]
    with pytest.raises(SystemExit), patch("os.path.exists", lambda x: False), patch(
        "argparse.ArgumentParser.parse_args", args
    ):
        main()
        text = capsys.readouterr().out
        assert "File " in text and " does not exist" in text


def test_main(capsys, employees4_2fields):
    args = MagicMock()
    args.report = "performance"
    args.files = ["abc"]
    with patch("os.path.exists", lambda x: True), patch(
        "argparse.ArgumentParser.parse_args", lambda x: args
    ), patch("workmate.main.parse_file", lambda x: employees4_2fields):
        main()
        text = capsys.readouterr().out
        assert "position" in text and "avg_performance" in text
        assert "Mobile Developer" in text and "Backend Developer" in text
