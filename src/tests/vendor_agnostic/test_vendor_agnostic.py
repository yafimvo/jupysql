import pytest
from vendor_agnostic.results_collector import ResultsCollector
from datetime import timedelta


IP = ["snowflake"]
# IP = ["postgresql", "mssql", "sqlite", "duckdb", "mariadb", "snowflake", "questdb"]

BASE_DIR = "./src/tests/vendor_agnostic"


def test_ggplot(capsys):
    files = ["test_ggplot.py"]
    run(files, capsys)


def test_plot(capsys):
    files = ["test_plot.py"]
    run(files, capsys)


def run(files, capsys):
    collector = ResultsCollector()
    for file in files:
        test_file = f"{BASE_DIR}/{file}"

        for ip in IP:
            if ip == "snowflake":
                args_ = ["--live", "-s", "--ip", ip, test_file]
            else:
                args_ = ["-s", "--ip", ip, test_file]

            with capsys.disabled():
                pytest.main(plugins=[collector], args=args_)

                time_sconds = collector.total_duration.__round__(2)
                time_delta_ = timedelta(seconds=time_sconds)

                print(
                    f"\n\n============ {file} results for {ip} \
                        in {time_sconds}s ({time_delta_}) ============"
                )
                print("passed : ", collector.passed)
                print("failed : ", collector.failed)
                print("xfailed : ", collector.xfailed)
                print("skipped : ", collector.skipped)

        assert collector.failed == 0
