from sqlalchemy import inspect
from prettytable import PrettyTable
from ploomber_core.exceptions import modify_exceptions
from sql.connection import Connection
from sql.telemetry import telemetry
import sql.run
import math
from sql.util import convert_to_scientific


def _get_inspector(conn):
    if conn:
        return inspect(conn)

    if not Connection.current:
        raise RuntimeError("No active connection")
    else:
        return inspect(Connection.current.session)


class DatabaseInspection:
    def __repr__(self) -> str:
        return self._table_txt

    def _repr_html_(self) -> str:
        return self._table_html


class Tables(DatabaseInspection):
    """
    Displays the tables in a database
    """

    def __init__(self, schema=None, conn=None) -> None:
        inspector = _get_inspector(conn)

        self._table = PrettyTable()
        self._table.field_names = ["Name"]

        for row in inspector.get_table_names(schema=schema):
            self._table.add_row([row])

        self._table_html = self._table.get_html_string()
        self._table_txt = self._table.get_string()


@modify_exceptions
class Columns(DatabaseInspection):
    """
    Represents the columns in a database table
    """

    def __init__(self, name, schema, conn=None) -> None:
        inspector = _get_inspector(conn)

        columns = inspector.get_columns(name, schema)

        if not columns:
            if schema:
                raise ValueError(
                    f"There is no table with name {name!r} in schema {schema!r}"
                )
            else:
                raise ValueError(
                    f"There is no table with name {name!r} in the default schema"
                )

        self._table = PrettyTable()
        self._table.field_names = list(columns[0].keys())

        for row in columns:
            self._table.add_row(list(row.values()))

        self._table_html = self._table.get_html_string()
        self._table_txt = self._table.get_string()


@modify_exceptions
class TableDescription(DatabaseInspection):
    """
    Generates descriptive statistics.

    Descriptive statistics are:

    Count - Number of all not None values

    Mean - Mean of the values

    Max - Maximum of the values in the object.

    Min - Minimum of the values in the object.

    STD - Standard deviation of the observations

    25h, 50h and 75h percentiles

    Unique - Number of not None unique values

    Top - The most frequent value

    Freq - Frequency of the top value

    """

    def __init__(self, table_name, schema=None, config=None) -> None:
        if schema:
            table_name = f"{schema}.{table_name}"

        columns = sql.run.run_raw(
            Connection.current, f"SELECT * FROM {table_name} WHERE 1=0", config
        ).keys

        table_stats = dict({})

        for column in columns:
            table_stats[column] = dict()
            result_col_freq_values = sql.run.run_raw(
                Connection.current,
                f"""SELECT {column} as top,
                COUNT({column}) as frequency FROM {table_name}
                GROUP BY {column} ORDER BY Count({column}) Desc""",
                config,
            ).dict()

            # get all non None values, min, max and avg.
            result_value_values = sql.run.run_raw(
                Connection.current,
                f"""
                SELECT MIN({column}) AS min,
                MAX({column}) AS max,
                COUNT(DISTINCT {column}) AS unique_count,
                COUNT({column}) AS total
                FROM {table_name}
                WHERE {column} IS NOT NULL AND TRIM({column}) <> ''
                """,
                config,
            ).dict()

            table_stats[column]["freq"] = result_col_freq_values["frequency"][0]
            table_stats[column]["top"] = result_col_freq_values["top"][0]
            table_stats[column]["count"] = result_value_values["total"][0]
            table_stats[column]["unique"] = result_value_values["unique_count"][0]
            table_stats[column]["min"] = result_value_values["min"][0]
            table_stats[column]["max"] = result_value_values["max"][0]

            avg = None
            try:
                results_avg = sql.run.run_raw(
                    Connection.current,
                    f"""
                                SELECT AVG({column}) AS avg
                                FROM {table_name}
                                WHERE {column} IS NOT NULL AND TRIM({column}) <> ''
                                """,
                    config,
                ).dict()
                avg = results_avg["avg"][0]
            except BaseException:
                avg = math.nan

            table_stats[column]["mean"] = avg

            try:
                # Note: This STDEV and PERCENTILE_DISC will work only on DuckDB
                result = sql.run.run_raw(
                    Connection.current,
                    f"""
                    SELECT
                        stddev_pop({column}) as std,
                        percentile_disc(0.25) WITHIN GROUP (ORDER BY {column}) as p25,
                        percentile_disc(0.50) WITHIN GROUP (ORDER BY {column}) as p50,
                        percentile_disc(0.75) WITHIN GROUP (ORDER BY {column}) as p75
                    FROM {table_name}
                    """,
                    config,
                ).dict()

                table_stats[column]["std"] = result["std"][0]
                table_stats[column]["25%"] = result["p25"][0]
                table_stats[column]["50%"] = result["p50"][0]
                table_stats[column]["75%"] = result["p75"][0]

            except TypeError:
                # for non numeric values
                table_stats[column]["mean"] = math.nan
                table_stats[column]["std"] = math.nan
                table_stats[column]["25%"] = math.nan
                table_stats[column]["50%"] = math.nan
                table_stats[column]["75%"] = math.nan

            except BaseException:
                # Failed to run sql command.
                # We ignore the cell stats for such case.
                pass

        self._table = PrettyTable()
        self._table.field_names = [" "] + list(table_stats.keys())

        rows = list(table_stats.items())[0][1].keys()

        for row in rows:
            values = [row]
            for column in table_stats:
                if row in table_stats[column]:
                    value = table_stats[column][row]
                else:
                    value = ""
                value = convert_to_scientific(value)
                values.append(value)

            self._table.add_row(values)

        self._table_html = self._table.get_html_string()
        self._table_txt = self._table.get_string()


@telemetry.log_call()
def get_table_names(schema=None):
    """Get table names for a given connection"""
    return Tables(schema)


@telemetry.log_call()
def get_columns(name, schema=None):
    """Get column names for a given connection"""
    return Columns(name, schema)


@telemetry.log_call()
def get_table_statistics(name, schema=None, config=None):
    """Get table statistics for a given connection.

    For all data types the results will include `count`, `mean`, `std`, `min`
    `max`, `25`, `50` and `75` percentiles. It will also include `unique`, `top`
    and `freq` statistics.
    """
    return TableDescription(name, schema=schema, config=config)
