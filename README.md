# Генератор отчетов

## Запуск
`python workmate/main.py --files file1.csv file2.csv --report performance`

## Добавление новых отчетов
Создайте класс:
```
class MyReport(Report):
    def get_report(self) -> str:
        # ваш код
        # report_data - список словарей
        return tabulate(report_data, headers="keys")
```
Добавьте его в словарь REPORTS:
`REPORTS = {..., "my": "MyReport"}`
Сгенерируйте отчет:
`python main.py --files file1.csv file2.csv --report my`

## Запуск тестов
`pytest --cov=workmate.main`
