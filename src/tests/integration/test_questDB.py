import pytest
import time
from dockerctx import new_container
from contextlib import contextmanager
import pandas as pd


import urllib.request
import requests
from pathlib import Path

from sql.ggplot import ggplot, aes, geom_histogram
from matplotlib.testing.decorators import image_comparison, cleanup

"""
This test class includes all QuestDB-related tests and specifically focuses 
on testing the custom engine initialization.

TODO: We should generelize this test to handle different engines/connections.
"""


@pytest.fixture
def penguins_data(tmpdir):
    """
    Downloads penguins dataset
    """
    file_path_str = str(tmpdir.join("penguins.csv"))

    if not Path(file_path_str).is_file():
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv",  # noqa breaks the check-for-broken-links
            file_path_str,
        )

    yield file_path_str


def import_data(file_name, table_name):
    """
    Loads csv file to questdb container
    """
    query_url = "http://127.0.0.1:9000/imp"

    df = pd.read_csv(file_name, sep=",")
    df.drop_duplicates(subset=None, inplace=True)
    df.to_csv(file_name, index=False)

    with open(file_name, "rb") as csv:
        file_data = csv.read()
        files = {"data": (table_name, file_data)}
        requests.post(query_url, files=files)


def custom_database_ready(
    custom_connection,
    timeout=20,
    poll_freq=0.5,
):
    """Wait until the container is ready to receive connections.


    :type host: str
    :type port: int
    :type timeout: float
    :type poll_freq: float
    """

    errors = []

    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            custom_connection()
            return True
        except Exception as e:
            errors.append(str(e))

        time.sleep(poll_freq)

    # print all the errors so we know what's goin on since failing to connect might be
    # to some misconfiguration error
    errors_ = "\n".join(errors)
    print(f"ERRORS: {errors_}")

    return False


@contextmanager
def questdb_container(is_bypass_init=False):
    if is_bypass_init:
        yield None
        return

    def test_questdb_connection():
        import psycopg as pg

        engine = pg.connect(
            "dbname='qdb' user='admin' host='127.0.0.1' port='8812' password='quest'"
        )
        engine.close()

    with new_container(
        image_name="questdb/questdb",
        ports={"8812": "8812", "9000": "9000", "9009": "9009"},
        ready_test=lambda: custom_database_ready(test_questdb_connection),
        healthcheck={
            "interval": 10000000000,
            "timeout": 5000000000,
            "retries": 5,
        },
    ) as container:
        yield container


@pytest.fixture
def ip_questdb(penguins_data, ip_empty):
    """
    Initalizes questdb database container and loads it with data
    """
    with questdb_container():
        ip_empty.run_cell(
            """
            import psycopg2 as pg
            engine = pg.connect(
                "dbname='qdb' user='admin' host='127.0.0.1' port='8812' password='quest'"
            )
            %sql engine
            """
        )

        # Load pre-defined datasets
        import_data(penguins_data, "penguins.csv")
        yield ip_empty


@pytest.fixture
def penguins_no_nulls_questdb(ip_questdb):
    ip_questdb.run_cell(
        """
%%sql --save no_nulls --no-execute
SELECT *
FROM penguins.csv
WHERE body_mass_g IS NOT NULL and
sex IS NOT NULL
    """
    ).result


@cleanup
@image_comparison(
    baseline_images=["custom_engine_histogram"],
    extensions=["png"],
    remove_text=False,
)
def test_ggplot_histogram(ip_questdb, penguins_no_nulls_questdb):
    (
        ggplot(
            table="no_nulls",
            with_="no_nulls",
            mapping=aes(x=["bill_length_mm", "bill_depth_mm"]),
        )
        + geom_histogram(bins=50)
    )


@cleanup
@image_comparison(
    baseline_images=["custom_engine_histogram"],
    extensions=["png"],
    remove_text=False,
)
def test_sqlplot_histogram(ip_questdb, penguins_no_nulls_questdb):
    ip_questdb.run_cell(
        """%sqlplot histogram --column bill_length_mm bill_depth_mm --table no_nulls --with no_nulls"""  # noqa
    )


@pytest.mark.parametrize(
    "query, expected_results",
    [
        (
            "select * from penguins.csv limit 2",
            [
                ("Adelie", "Torgersen", 39.1, 18.7, 181, 3750, "MALE"),
                ("Adelie", "Torgersen", 39.5, 17.4, 186, 3800, "FEMALE"),
            ],
        ),
        (
            "select * from penguins.csv where sex = 'MALE' limit 2",
            [
                ("Adelie", "Torgersen", 39.1, 18.7, 181, 3750, "MALE"),
                ("Adelie", "Torgersen", 39.3, 20.6, 190, 3650, "MALE"),
            ],
        ),
        (
            "select species, island from penguins.csv where sex = 'MALE' limit 2",
            [("Adelie", "Torgersen"), ("Adelie", "Torgersen")],
        ),
    ],
)
def test_sql(ip_questdb, query, expected_results):
    resultSet = ip_questdb.run_cell(f"%sql {query}").result
    for i, row in enumerate(resultSet):
        assert row == expected_results[i]
