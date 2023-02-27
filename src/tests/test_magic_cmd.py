import sqlite3

import pytest
from IPython.core.error import UsageError


@pytest.mark.parametrize(
    "cell, error_type, error_message",
    [
        [
            "%sqlcmd stuff",
            UsageError,
            "%sqlcmd has no command: 'stuff'. Valid commands are: 'tables', "
            "'columns', 'profile'",
        ],
        [
            "%sqlcmd columns",
            UsageError,
            "the following arguments are required: -t/--table",
        ],
    ],
)
def test_error(tmp_empty, ip, cell, error_type, error_message):
    out = ip.run_cell(cell)

    assert isinstance(out.error_in_exec, error_type)
    assert str(out.error_in_exec) == error_message


def test_tables(ip):
    out = ip.run_cell("%sqlcmd tables").result._repr_html_()
    assert "author" in out
    assert "empty_table" in out
    assert "test" in out


def test_tables_with_schema(ip, tmp_empty):
    with sqlite3.connect("my.db") as conn:
        conn.execute("CREATE TABLE numbers (some_number FLOAT)")

    ip.run_cell(
        """%%sql
ATTACH DATABASE 'my.db' AS some_schema
"""
    )

    out = ip.run_cell("%sqlcmd tables --schema some_schema").result._repr_html_()

    assert "numbers" in out


def test_columns(ip):
    out = ip.run_cell("%sqlcmd columns -t author").result._repr_html_()
    assert "first_name" in out
    assert "last_name" in out
    assert "year_of_death" in out


def test_columns_with_schema(ip, tmp_empty):
    with sqlite3.connect("my.db") as conn:
        conn.execute("CREATE TABLE numbers (some_number FLOAT)")

    ip.run_cell(
        """%%sql
ATTACH DATABASE 'my.db' AS some_schema
"""
    )

    out = ip.run_cell(
        "%sqlcmd columns --table numbers --schema some_schema"
    ).result._repr_html_()

    assert "some_number" in out


def test_table_profile(ip):
    ip.run_cell(
        """
    %%sql sqlite://
    CREATE TABLE numbers (rating, price, number, word);
    INSERT INTO numbers VALUES (14.44, 2.48, 82, 'a');
    INSERT INTO numbers VALUES (13.13, 1.50, 93, 'b');
    INSERT INTO numbers VALUES (12.59, 0.20, 98, 'a');
    INSERT INTO numbers VALUES (11.54, 0.41, 89, 'a');
    INSERT INTO numbers VALUES (10.532, 0.1, 88, 'c');
    INSERT INTO numbers VALUES (11.5, 0.2, 84, '   ');
    INSERT INTO numbers VALUES (11.1, 0.3, 90, 'a');
    INSERT INTO numbers VALUES (12.9, 0.31, 86, '');
    """
    )

    expected = {
        "count": [8, 8, 8, 6],
        "mean": [12.2165, 0.6875, 88.75, float("NaN")],
        "min": [10.532, 0.1, 82, float("NaN")],
        "max": [14.44, 2.48, 98, float("NaN")],
        "std": [
            1.2784055917989632,
            0.8504914545636036,
            5.092010548749033,
            float("NaN"),
        ],
        "25%": [11.2, 0.2, 84.5, float("NaN")],
        "50%": [12.065, 0.305, 88.5, float("NaN")],
        "75%": [13.072500000000002, 1.2275, 92.25, float("NaN")],
        "unique": [8, 7, 8, 4],
        "freq": [1, 2, 1, 4],
        "top": [14.44, 0.2, 98, "a"],
    }

    out = ip.run_cell("%sqlcmd profile -t numbers").result

    stats_table = out._table

    for row in stats_table:
        criteria = row.get_string(fields=[" "], border=False).strip()

        rating = row.get_string(fields=["rating"], border=False, header=False).strip()

        price = row.get_string(fields=["price"], border=False, header=False).strip()

        number = row.get_string(fields=["number"], border=False, header=False).strip()

        if criteria in expected:
            assert rating == str(expected[criteria][0])
            assert price == str(expected[criteria][1])
            assert number == str(expected[criteria][2])
