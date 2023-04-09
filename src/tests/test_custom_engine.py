import pytest
from sql.ggplot import ggplot, aes, geom_histogram
from matplotlib.testing.decorators import image_comparison, cleanup
import math

# TODO: Include these test in CI
# TODO: Remove this skip
SKIP_CI = True
SKIP_REASON_NO_ENGINE = "Didn't setup quest db on CI"


@pytest.mark.skipif(SKIP_CI, reason=SKIP_REASON_NO_ENGINE)
@pytest.fixture
def questdb_engine(ip_empty):
    """
    Creates a custom connection to
    QuestDB which is not supported by SQLAlchemy
    """
    ip_empty.run_cell(
        """
        import psycopg2 as pg
        engine = pg.connect(
            "dbname='qdb' user='admin' host='127.0.0.1' port='8812' password='quest'"
        )
        %sql engine
        """
    )


@pytest.mark.skipif(SKIP_CI, reason=SKIP_REASON_NO_ENGINE)
@pytest.fixture
def penguins_no_nulls_questdb(ip_empty, questdb_engine):
    # Assume we have a table called penguins.csv
    # in our questdb

    ip_empty.run_cell(
        """
%%sql --save no_nulls --no-execute
SELECT *
FROM penguins.csv
WHERE body_mass_g IS NOT NULL and
sex IS NOT NULL
    """
    ).result


# TEST %sqlplot and ggplot api


@pytest.mark.skipif(SKIP_CI, reason=SKIP_REASON_NO_ENGINE)
@cleanup
@image_comparison(
    baseline_images=["custom_engine_histogram"],
    extensions=["png"],
    remove_text=False,
)
def test_ggplot_histogram(penguins_no_nulls_questdb):
    (
        ggplot(
            table="no_nulls",
            with_="no_nulls",
            mapping=aes(x=["bill_length_mm", "bill_depth_mm"]),
        )
        + geom_histogram(bins=50)
    )


@pytest.mark.skipif(SKIP_CI, reason=SKIP_REASON_NO_ENGINE)
@cleanup
@image_comparison(
    baseline_images=["custom_engine_histogram"],
    extensions=["png"],
    remove_text=False,
)
def test_sqlplot_histogram(ip_empty, penguins_no_nulls_questdb):
    ip_empty.run_cell(
        """%sqlplot histogram --column bill_length_mm bill_depth_mm --table no_nulls --with no_nulls"""  # noqa
    )


# TEST %sql


@pytest.mark.skipif(SKIP_CI, reason=SKIP_REASON_NO_ENGINE)
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
def test_sql(ip_empty, questdb_engine, query, expected_results):
    resultSet = ip_empty.run_cell(f"%sql {query}").result
    for i, row in enumerate(resultSet):
        assert row == expected_results[i]


# TEST %sqlcmd
@pytest.mark.skipif(True, reason=SKIP_REASON_NO_ENGINE)
@pytest.mark.parametrize(
    "expected",
    [
        {
            "top": ["Adelie", "Biscoe", 41.1, 17.0, 190, 3800, "MALE"],
            "min": ["Adelie", "Biscoe", 32.1, 13.1, 172, 2700, "FEMALE"],
            "mean": [
                math.nan,
                math.nan,
                "4.392e+01",
                "1.715e+01",
                "2.009e+02",
                "4.202e+03",
                math.nan,
            ],
            "max": ["Gentoo", "Torgersen", 59.6, 21.5, 231, 6300, "MALE"],
            "freq": [152, 168, 7, 12, 22, 12, 168],
            "count": [344, 344, 342, 342, 342, 342, 333],
        },
    ],
)
def test_sqlcmd_profile(ip_empty, questdb_engine, expected):
    out = ip_empty.run_cell("%sqlcmd profile --table penguins.csv").result

    stats_table = out._table

    for row in stats_table:
        criteria = row.get_string(fields=[" "], border=False).strip()
        species = row.get_string(fields=["species"], border=False, header=False).strip()
        island = row.get_string(fields=["island"], border=False, header=False).strip()
        bill_length_mm = row.get_string(
            fields=["bill_length_mm"], border=False, header=False
        ).strip()
        bill_depth_mm = row.get_string(
            fields=["bill_depth_mm"], border=False, header=False
        ).strip()
        flipper_length_mm = row.get_string(
            fields=["flipper_length_mm"], border=False, header=False
        ).strip()
        body_mass_g = row.get_string(
            fields=["body_mass_g"], border=False, header=False
        ).strip()
        sex = row.get_string(fields=["sex"], border=False, header=False).strip()

        assert criteria in expected
        assert species == str(expected[criteria][0])
        assert island == str(expected[criteria][1])
        assert bill_length_mm == str(expected[criteria][2])
        assert bill_depth_mm == str(expected[criteria][3])
        assert flipper_length_mm == str(expected[criteria][4])
        assert body_mass_g == str(expected[criteria][5])
        assert sex == str(expected[criteria][6])
