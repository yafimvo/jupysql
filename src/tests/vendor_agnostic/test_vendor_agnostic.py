import pytest
from tests.vendor_agnostic.results_collector import ResultsCollector

# IP = ["postgresql", "mssql", "sqlite", "duckdb", "mariadb", "snowflake"]
IP = ["postgresql"]

BASE_DIR = "./src/tests/vendor_agnostic"


def test_ggplot(capsys):
    files = ["test_ggplot.py"]
    run(files, capsys)


def run(files, capsys):
    files = [f"{BASE_DIR}/{file}" for file in files]

    collector = ResultsCollector()
    for test_file in files:
        for ip in IP:
            args_ = ["-s", "--ip", ip, test_file]

            with capsys.disabled():
                pytest.main(plugins=[collector], args=args_)
