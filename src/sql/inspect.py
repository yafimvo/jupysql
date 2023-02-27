from sqlalchemy import inspect
from prettytable import PrettyTable
from ploomber_core.exceptions import modify_exceptions
from sql.connection import Connection
from sql.telemetry import telemetry
import sql.run
import math


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

    Count - Number of all non empty values

    Mean - Mean of the values

    Max - Maximum of the values in the object.

    Min - Minimum of the values in the object.

    STD - Standard deviation of the observations

    25h, 50h and 75h percentiles

    Unique - Number of unique values

    Top - The most frequent value

    Freq - Frequency of the top value

    """

    def __init__(self, table_name, config=None, user_ns=None) -> None:
        result_table_columns = sql.run.run(
            Connection.current, f"SELECT * FROM {table_name} WHERE 1=0", config, user_ns
        )

        columns = result_table_columns.keys

        table_stats = dict({})

        for column in columns:
            table_stats[column] = dict()
            result_col_unique_values = sql.run.run(
                Connection.current,
                f"SELECT COUNT(DISTINCT {column}) as unique_count FROM {table_name}",
                config,
                user_ns,
            )

            result_col_freq_values = sql.run.run(
                Connection.current,
                f"""SELECT {column}, COUNT({column}) as frequency FROM {table_name}
                GROUP BY {column} ORDER BY Count({column}) Desc""",
                config,
                user_ns,
            )

            result_non_empty_values = sql.run.run(
                Connection.current,
                f"""SELECT {column} FROM {table_name} WHERE {column}
                IS NOT NULL AND TRIM({column}) <> ''
                ORDER BY {column} ASC
                """,
                config,
                user_ns,
            )

            col_values = result_non_empty_values.dict()[column]
            count = len(col_values)
            table_stats[column]["count"] = count
            table_stats[column]["freq"] = result_col_freq_values.dict()["frequency"][0]
            table_stats[column]["unique"] = result_col_unique_values.dict()[
                "unique_count"
            ][0]
            table_stats[column]["top"] = result_col_freq_values.dict()[column][0]
            table_stats[column]["min"] = col_values[0]
            table_stats[column]["max"] = col_values[count - 1]

            try:
                mean = sum(col_values) / count
                table_stats[column]["mean"] = mean

                values_sum = sum([(math.pow((v - mean), 2)) for v in col_values])
                std = math.sqrt(values_sum / (count - 1))

                table_stats[column]["std"] = std

                table_stats[column]["25%"] = self._get_n_percentile(25, col_values)
                table_stats[column]["50%"] = self._get_n_percentile(50, col_values)
                table_stats[column]["75%"] = self._get_n_percentile(75, col_values)

            except TypeError:
                # for non numeric values
                table_stats[column]["mean"] = math.nan
                table_stats[column]["std"] = math.nan
                table_stats[column]["25%"] = math.nan
                table_stats[column]["50%"] = math.nan
                table_stats[column]["75%"] = math.nan

        self._table = PrettyTable()
        self._table.field_names = [" "] + list(table_stats.keys())

        rows = list(table_stats.items())[0][1].keys()

        for row in rows:
            values = [row]
            for column in table_stats:
                value = table_stats[column][row]
                values.append(value)

            self._table.add_row(values)

        self._table_html = self._table.get_html_string()
        self._table_txt = self._table.get_string()

    def _get_n_percentile(self, n, list) -> float:
        """
        Calculates the nth percentile of the given data.

        Parameters
        ----------
        n : int
            The Nth percentile to comupte. Must be between 0 and 100 inclusive.

        list : list of numeric values
            An ordered list of numeric values

        Returns
        -------
        nth percentile of the list
        """
        if n < 0 or n > 100:
            raise ValueError("N must be between 0 and 100 inclusive")

        count = len(list)
        lp = ((count + 1) * n) / 100
        index = math.floor(lp)
        if index - 1 >= 0 and index < len(list):
            diff = list[index] - list[index - 1]
            distance = lp - index
            return list[index - 1] + distance * diff
        else:
            return None


@telemetry.log_call()
def get_table_names(schema=None):
    """Get table names for a given connection"""
    return Tables(schema)


@telemetry.log_call()
def get_columns(name, schema=None):
    """Get column names for a given connection"""
    return Columns(name, schema)


@telemetry.log_call()
def get_table_statistics(name, config=None, user_ns=None):
    """Get table statistics for a given connection.

    For all data types the results will include `count`, `mean`, `std`, `min`
    `max`, `25`, `50` and `75` percentiles. It will also include `unique`, `top`
    and `freq` statistics.
    """
    return TableDescription(name, config=config, user_ns=user_ns)
