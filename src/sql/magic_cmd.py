# flake8: noqa
import sys
import argparse

from IPython.utils.process import arg_split
from IPython.core.magic import Magics, line_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments
from IPython.core.error import UsageError
from sqlglot import select, condition
from sqlalchemy import text

try:
    from traitlets.config.configurable import Configurable
except ImportError:
    from IPython.config.configurable import Configurable

import sql.connection
from sql import inspect
import sql.run

from IPython.display import display, HTML


class CmdParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)

    def error(self, message):
        raise UsageError(message)


@magics_class
class SqlCmdMagic(Magics, Configurable):
    """%sqlcmd magic"""

    @line_magic("sqlcmd")
    @magic_arguments()
    @argument("line", type=str, help="Command name")
    def _validate_execute_inputs(self, line):
        """
        Function to validate %sqlcmd inputs.
        Raises UsageError in case of an invalid input, executes command otherwise.
        """

        AVAILABLE_SQLCMD_COMMANDS = ["tables", "columns", "test", "profile", "explore"]

        if line == "":
            raise UsageError(
                "Missing argument for %sqlcmd. "
                "Valid commands are: {}".format(", ".join(AVAILABLE_SQLCMD_COMMANDS))
            )
        else:
            split = arg_split(line)
            command, others = split[0].strip(), split[1:]

            if command in AVAILABLE_SQLCMD_COMMANDS:
                return self.execute(command, others)
            else:
                raise UsageError(
                    f"%sqlcmd has no command: {command!r}. "
                    "Valid commands are: {}".format(
                        ", ".join(AVAILABLE_SQLCMD_COMMANDS)
                    )
                )

    @argument("cmd_name", default="", type=str, help="Command name")
    @argument("others", default="", type=str, help="Other tags")
    def execute(self, cmd_name="", others="", cell="", local_ns=None):
        """
        Command
        """

        if cmd_name == "tables":
            parser = CmdParser()

            parser.add_argument(
                "-s", "--schema", type=str, help="Schema name", required=False
            )

            args = parser.parse_args(others)

            return inspect.get_table_names(schema=args.schema)
        elif cmd_name == "columns":
            parser = CmdParser()

            parser.add_argument(
                "-t", "--table", type=str, help="Table name", required=True
            )
            parser.add_argument(
                "-s", "--schema", type=str, help="Schema name", required=False
            )

            args = parser.parse_args(others)
            return inspect.get_columns(name=args.table, schema=args.schema)
        elif cmd_name == "test":
            parser = CmdParser()

            parser.add_argument(
                "-t", "--table", type=str, help="Table name", required=True
            )
            parser.add_argument(
                "-c", "--column", type=str, help="Column name", required=False
            )
            parser.add_argument(
                "-g",
                "--greater",
                type=str,
                help="Greater than a certain number.",
                required=False,
            )
            parser.add_argument(
                "-goe",
                "--greater-or-equal",
                type=str,
                help="Greater or equal than a certain number.",
                required=False,
            )
            parser.add_argument(
                "-l",
                "--less-than",
                type=str,
                help="Less than a certain number.",
                required=False,
            )
            parser.add_argument(
                "-loe",
                "--less-than-or-equal",
                type=str,
                help="Less than or equal to a certain number.",
                required=False,
            )
            parser.add_argument(
                "-nn",
                "--no-nulls",
                help="Returns rows in specified column that are not null.",
                action="store_true",
            )

            args = parser.parse_args(others)
            if args.greater and args.greater_or_equal:
                return ValueError(
                    "You cannot use both greater and greater "
                    "than or equal to arguments at the same time."
                )
            elif args.less_than and args.less_than_or_equal:
                return ValueError(
                    "You cannot use both less and less than "
                    "or equal to arguments at the same time."
                )

            conn = sql.connection.Connection.current.session
            result_dict = run_each_individually(args, conn)

            if len(result_dict.keys()):
                print(
                    "Test failed. Returned are samples of the failures from your data:"
                )
                return result_dict
            else:
                return True

        elif cmd_name == "profile":
            parser = CmdParser()
            parser.add_argument(
                "-t", "--table", type=str, help="Table name", required=True
            )

            parser.add_argument(
                "-s", "--schema", type=str, help="Schema name", required=False
            )

            parser.add_argument(
                "-o", "--output", type=str, help="Store report location", required=False
            )

            args = parser.parse_args(others)

            report = inspect.get_table_statistics(schema=args.schema, name=args.table)

            if args.output:
                with open(args.output, "w") as f:
                    f.write(report._repr_html_())

            return report

        elif cmd_name == "explore":
            parser = CmdParser()
            parser.add_argument(
                "-t", "--table", type=str, help="Table name", required=True
            )
            args = parser.parse_args(others)
            # https://stackoverflow.com/questions/38893448/pagination-on-pandas-dataframe-to-html

            # SET CONNECTION
            import sqlalchemy

            query = f"SELECT * FROM {args.table}"
            # query = f"SELECT * FROM {args.table} limit 50"
            # Run query on a given table to fetch first X rows
            conn = sql.connection.Connection.current
            # TODO Change this to match custom drivers
            query = conn._transpile_query(query)
            rows = conn.session.execute(sqlalchemy.sql.text(query)).fetchall()

            # MAKE THE RESULTS WORKABLE ON JS
            import json

            columns = sql.run.raw_run(
                conn, f"SELECT * FROM {args.table} WHERE 1=0"
            ).keys()

            dicts = [dict(zip(list(columns), row)) for row in rows]
            rows_json = json.dumps(dicts).replace("null", "'None'")

            # CREATE THE SELECT DROPDOWN
            options = [10, 25, 50, 100]

            options_html = ""
            for option in options:
                option_html = f"<option value={option}>{option}</option>"
                options_html += option_html
            select = f"""
            <div style="display: inline-flex">
                <span style="margin-right: 5px">Show</span>
                <select onchange="handleRowsNumberOfRowsChange(this)">{options_html}</select>
                <span style="margin-left: 5px">entries</span>
            </div>
            """

            table = results_to_html_table(columns, rows)

            display(HTML(select))

            # INJECT JS
            display(
                HTML(
                    f"""
                <style>
                    #pagesButtons button.selected {{
                        background: #efefef;
                        border: 1px solid #767676;
                        border-radius: 2px;
                    }}
                    #pagesButtons button {{
                        background: none;
                        border: none;
                        padding: 0 10px;
                    }}                    
                </style>

                <script>
                    function handleRowsNumberOfRowsChange(e) {{
                        const rows = {rows_json};
                        const rowsPerPage = parseInt(e.value);
                        let table = document.querySelector('#resultsTable');
                        table.setAttribute('rows-per-page', rowsPerPage);
                        const maxPages = Math.ceil(rows.length / rowsPerPage)
                        document.querySelector('#resultsTable').setAttribute('max-pages', maxPages);

                        setTimeout(() => {{
                            updateTable(rowsPerPage);
                        }}, 100);                        
                    }}
                    function updateTable(rowsPerPage) {{
                        const trs = document.querySelectorAll("#resultsTable tbody tr");
                        const tbody = document.querySelector("#resultsTable tbody");
                        tbody.innerHTML = "";

                        const rows = {rows_json};
                        const _html = rows.slice(0, rowsPerPage).map(row => {{
                            const tds = Object.keys(row).map(key => `<td>${{row[key]}}</td>`).join("");
                            return `<tr>${{tds}}</tr>`;
                        }}).join("");

                        tbody.innerHTML = _html
                        
                        setTimeout(() => {{
                            updatePaginationBar(0)
                        }}, 100)
                    }}

                    function showTablePage(page, rowsPerPage) {{
                        const trs = document.querySelectorAll("#resultsTable tbody tr");
                        const tbody = document.querySelector("#resultsTable tbody");
                        tbody.innerHTML = "";

                        const rows = {rows_json};
                        const startIndex = page * rowsPerPage;
                        const endIndex = startIndex + rowsPerPage;
                        const _html = rows.slice(startIndex, endIndex).map(row => {{
                            const tds = Object.keys(row).map(key => `<td>${{row[key]}}</td>`).join("");
                            return `<tr>${{tds}}</tr>`;
                        }}).join("");

                        tbody.innerHTML = _html;

                        document.getElementById("resultsTable").setAttribute("curr-page-idx", page);

                        updatePaginationBar(page);
                    }}

                    function nextPageClick() {{
                        const table = document.getElementById("resultsTable");
                        const currPageIndex = parseInt(table.getAttribute("curr-page-idx"));
                        const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                        const maxPages = parseInt(table.getAttribute("max-pages"));

                        const nextPage = currPageIndex + 1;
                        if (nextPage < maxPages) {{
                            showTablePage(nextPage, rowsPerPage);
                        }}
                        
                    }}

                    function prevPageClick() {{
                        const table = document.getElementById("resultsTable");
                        const currPageIndex = parseInt(table.getAttribute("curr-page-idx"));
                        const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                        const prevPage = currPageIndex - 1;
                        if (prevPage >= 0) {{
                            showTablePage(prevPage, rowsPerPage);                    
                        }}
                    }}

                    function updatePaginationBar(currPage) {{
                        const table = document.getElementById("resultsTable");
                        const maxPages = parseInt(table.getAttribute("max-pages"));
                        const maxPagesInRow = 6;
                        const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));

                        let buttonsArray = []
                        
                        let startEllipsisAdded = false
                        let endEllipsisAdded = false


                        // add first
                        let selected = currPage === 0 ? "selected" : "";
                        buttonsArray.push(`<button class="${{selected}}" onclick="showTablePage(0, ${{rowsPerPage}})">1</button>`);

                        for (i = 1; i < maxPages - 1; i++) {{
                            selected = currPage === i ? "selected" : "";
                            const inStartRange = currPage < maxPagesInRow;
                            const inEndRange = maxPages - 1 - currPage < maxPagesInRow;

                            if (inStartRange) {{
                                if (i < maxPagesInRow) {{
                                    buttonsArray.push(`<button class="${{selected}}" onclick="showTablePage(${{i}}, ${{rowsPerPage}})">${{i + 1}}</button>`);
                                }} else {{
                                if (!startEllipsisAdded) {{
                                    buttonsArray.push("...");
                                    startEllipsisAdded = true;
                                }}
                                }}
                            }} else if (inEndRange) {{
                                if (maxPages - 1 - i < maxPagesInRow) {{
                                    buttonsArray.push(`<button class="${{selected}}" onclick="showTablePage(${{i}}, ${{rowsPerPage}})">${{i + 1}}</button>`);
                                }} else {{
                                if (!endEllipsisAdded) {{
                                    buttonsArray.push("...");
                                    endEllipsisAdded = true;
                                }}
                                }}                                
                            }}

                            if (!inStartRange && !inEndRange) {{
                            
                                if (currPage === i-2) {{
                                    buttonsArray.push("...");
                                }}
                                if (
                                    currPage === i - 1 ||
                                    currPage === i ||
                                    currPage === i + 1
                                ) {{
                                    buttonsArray.push(`<button class="${{selected}}" onclick="showTablePage(${{i}}, ${{rowsPerPage}})">${{i + 1}}</button>`);                                    
                                }}

                                if (currPage === i+2) {{
                                    buttonsArray.push("...");
                                }}

                            }}
                        }}

                        selected = currPage === maxPages - 1 ? "selected" : "";
                        buttonsArray.push(`<button class="${{selected}}" onclick="showTablePage(${{maxPages - 1}}, ${{rowsPerPage}})">${{maxPages}}</button>`);


                        const buttonsHtml = buttonsArray.join("");
                        document.querySelector("#pagesButtons").innerHTML = buttonsHtml;
                    }}
                </script>
                """
                )
            )

            display(HTML(table))


def run_each_individually(args, conn):
    base_query = select("*").from_(args.table)
    storage = {}

    if args.greater:
        where = condition(args.column + ">" + args.greater)
        current_query = base_query.where(where).sql()

        res = conn.execute(text(current_query)).fetchone()

        if res is not None:
            storage["greater"] = res
    if args.greater_or_equal:
        where = condition(args.column + ">=" + args.greater_or_equal)

        current_query = base_query.where(where).sql()

        res = conn.execute(text(current_query)).fetchone()
        if res is not None:
            storage["greater_or_equal"] = res
    if args.less_than_or_equal:
        where = condition(args.column + "<=" + args.less_than_or_equal)
        current_query = base_query.where(where).sql()

        res = conn.execute(text(current_query)).fetchone()
        if res is not None:
            storage["less_than_or_equal"] = res
    if args.less_than:
        where = condition(args.column + "<" + args.less_than)
        current_query = base_query.where(where).sql()

        res = conn.execute(text(current_query)).fetchone()
        if res is not None:
            storage["less_than"] = res
    if args.no_nulls:
        where = condition("{} is NULL".format(args.column))
        current_query = base_query.where(where).sql()

        res = conn.execute(text(current_query)).fetchone()
        if res is not None:
            storage["null"] = res

    return storage


# helper functions
def results_to_html_table(columns, rows):
    import math

    rows_per_page = 10
    n_pages = math.ceil(len(rows) / rows_per_page)

    table = f"<table id='resultsTable' style='width:100%' curr-page-idx=0 rows-per-page={rows_per_page} max-pages = {n_pages}>"

    # Prepare table headers
    ths = [f"<th>{column}</th>" for column in columns]
    ths = "".join(ths)
    table += f"<thead><tr>{ths}</tr></thead>"

    table += "<tbody>"
    # prepare html table from this array
    for row in rows[:rows_per_page]:
        tr = "<tr>"
        for i in range(len(row)):
            cell_value = row[i]
            td = f"<td>{cell_value}</td>"
            tr += td
        tr += "</tr>"

        table += tr

    table += "</tbody></table>"

    # table pagination
    pages_html = ""
    max_pages_in_row = 6
    ellipsis_added = False
    for page in range(n_pages):
        if page < max_pages_in_row or page == n_pages - 1:
            page_to_display = page + 1
            selected = "selected" if page == 0 else ""
            page_html = f"""<button class="{selected}" onclick="showTablePage({page}, {rows_per_page})">{page_to_display}</button>"""
        else:
            if not ellipsis_added:
                page_html = "..."
                ellipsis_added = True
            else:
                page_html = ""

        pages_html += page_html

    pagination_html = f"""
    <div style = "display: inline-flex">
        <button onclick="prevPageClick()">Previous</button>
        <div id = "pagesButtons" style = "display: inline-flex">
            {pages_html}
        </div>
        <button onclick="nextPageClick()">Next</button>
    </div>
    """

    table += pagination_html

    return table
