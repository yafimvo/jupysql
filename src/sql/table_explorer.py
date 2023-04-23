from sql.connection import Connection
import sql
from IPython.display import display, HTML
from IPython import get_ipython
import math
import sqlalchemy
import json


def parse_sql_to_json(rows, columns) -> str:
    """
    Serialize sql rows to a JSON formatted ``str``
    """
    # parse data to json
    dicts = [dict(zip(list(columns), row)) for row in rows]
    rows_json = json.dumps(dicts, indent=4, sort_keys=True, default=str).replace(
        "null", '"None"'
    )

    return rows_json


def fetch_sql_with_pagination(table, offset, n_rows, with_=None) -> tuple():
    """
    Returns next n_rows and columns from table starting at the offset

    https://stackoverflow.com/questions/109232/what-is-the-best-way-to-paginate-results-in-sql-server
    """
    query = f"SELECT * FROM {table} OFFSET {offset} ROWS FETCH NEXT {n_rows} ROWS ONLY"

    rows = Connection.current.execute(query, with_).fetchall()

    columns = sql.run.raw_run(
        Connection.current, f"SELECT * FROM {table} WHERE 1=0"
    ).keys()

    return rows, columns


def init_table(table) -> None:
    """
    Display an HTML table connected to a SQL engine
    """

    rows, columns = fetch_sql_with_pagination(table, 0, 10)
    rows_json = parse_sql_to_json(rows, columns)

    query = f"SELECT count(*) FROM {table}"
    n_total = Connection.current.session.execute(sqlalchemy.sql.text(query)).fetchone()[
        0
    ]

    rows_per_page = 10
    n_pages = math.ceil(n_total / rows_per_page)

    def front_listener(comm, open_msg):
        @comm.on_msg
        def _recv(msg):
            data = msg["content"]["data"]
            n_rows = data["nRows"]
            page = data["page"]

            offset = page * n_rows

            rows, columns = fetch_sql_with_pagination(table, offset, n_rows)
            rows_json = parse_sql_to_json(rows, columns)

            comm.send({"rows": rows_json})

    # register kernel listener
    get_ipython().kernel.comm_manager.register_target("comm_target", front_listener)

    # output container
    display(
        HTML(
            """
        <div id="tableContainer"></div>
        """
        )
    )

    # inject css
    display(
        HTML(
            """
        <style>
            #pagesButtons button.selected {
                background: #efefef;
                border: 1px solid #767676;
                border-radius: 2px;
            }
            #pagesButtons button {
                background: none;
                border: none;
                padding: 0 10px;
            }
            #resultsTable {
                display: inline;
            }
        </style>
        """
        )
    )

    # inject js
    display(
        HTML(
            f"""
        <script>
            function fetchTableData(page, rowsPerPage, callback) {{
                const comm =
                Jupyter.notebook.kernel.comm_manager.new_comm('comm_target', {{}})

                comm.send({{
                        'nRows' : rowsPerPage,
                        'page': page
                        }})

                comm.on_msg(function(msg) {{
                    const rows = JSON.parse(msg.content.data['rows']);
                    console.log(rows)
                    if (callback) {{
                        callback(rows)
                    }}
                }});
            }}

            function handleRowsNumberOfRowsChange(e) {{
                const rows = {rows_json};
                const rowsPerPage = parseInt(e.value);
                let table = document.querySelector('#resultsTable');
                table.setAttribute('rows-per-page', rowsPerPage);

                const nTotal = table.getAttribute('n-total');

                const maxPages = Math.ceil(nTotal / rowsPerPage)
                table.setAttribute('max-pages', maxPages);

                setTimeout(() => {{
                    fetchTableData(0, rowsPerPage, (rows) => {{
                        updateTable(rowsPerPage, rows);
                    }})
                }}, 100);
            }}

            function updateTable(rowsPerPage, rows) {{
                const trs = document.querySelectorAll("#resultsTable tbody tr");
                const tbody = document.querySelector("#resultsTable tbody");
                tbody.innerHTML = "";

                const _html = rows.map(row => {{
                    const tds =
                    Object.keys(row).map(key => `<td>${{row[key]}}</td>`).join("");
                    return `<tr>${{tds}}</tr>`;
                }}).join("");

                tbody.innerHTML = _html

                setTimeout(() => {{
                    updatePaginationBar(0)
                }}, 100)
            }}

            function showTablePage(page, rowsPerPage, data) {{
                const table = document.getElementById("resultsTable");
                const trs = document.querySelectorAll("#resultsTable tbody tr");
                const tbody = document.querySelector("#resultsTable tbody");
                tbody.innerHTML = "";

                const rows = data;
                const startIndex = page * rowsPerPage;
                const endIndex = startIndex + rowsPerPage;
                const _html = rows.map(row => {{
                    const tds =
                    Object.keys(row).map(key => `<td>${{row[key]}}</td>`).join("");
                    return `<tr>${{tds}}</tr>`;
                }}).join("");

                tbody.innerHTML = _html;

                table.setAttribute("curr-page-idx", page);
                updatePaginationBar(page);
            }}

            function nextPageClick() {{
                const table = document.getElementById("resultsTable");
                const currPageIndex = parseInt(table.getAttribute("curr-page-idx"));
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                const maxPages = parseInt(table.getAttribute("max-pages"));

                const nextPage = currPageIndex + 1;
                if (nextPage < maxPages) {{
                    fetchTableData(nextPage, rowsPerPage, (rows) => {{
                        showTablePage(nextPage, rowsPerPage, rows)
                    }});
                }}

            }}

            function prevPageClick() {{
                const table = document.getElementById("resultsTable");
                const currPageIndex = parseInt(table.getAttribute("curr-page-idx"));
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                const prevPage = currPageIndex - 1;
                if (prevPage >= 0) {{
                    fetchTableData(prevPage, rowsPerPage, (rows) => {{
                        showTablePage(prevPage, rowsPerPage, rows)
                    }});
                }}
            }}

            function setPageButton(label, navigateTo, isSelected) {{
                const table = document.getElementById("resultsTable");
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                const selected = isSelected ? "selected" : "";

                const button = `
                <button class="${{selected}}"
                        onclick="fetchTableData(${{navigateTo}}, ${{rowsPerPage}},
                        (rows) => {{
                            showTablePage(${{navigateTo}}, ${{rowsPerPage}}, rows);
                            }})"
                >
                    ${{label}}
                </button>
                `
                return button;
            }}

            function updatePaginationBar(currPage) {{
                const table = document.getElementById("resultsTable");
                const maxPages = parseInt(table.getAttribute("max-pages"));
                const maxPagesInRow = 6;
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                table.setAttribute("curr-page-idx", currPage);

                let buttonsArray = []

                let startEllipsisAdded = false
                let endEllipsisAdded = false


                // add first
                let selected = currPage === 0;
                buttonsArray.push(setPageButton("1", 0, selected));

                for (i = 1; i < maxPages - 1; i++) {{
                    const navigateTo = i;
                    const label = i + 1;
                    selected = currPage === i;
                    const inStartRange = currPage < maxPagesInRow;
                    const inEndRange = maxPages - 1 - currPage < maxPagesInRow;

                    if (inStartRange) {{
                        if (i < maxPagesInRow) {{
                            buttonsArray
                            .push(setPageButton(label, navigateTo, selected));
                        }} else {{
                        if (!startEllipsisAdded) {{
                            buttonsArray.push("...");
                            startEllipsisAdded = true;
                        }}
                        }}
                    }} else if (inEndRange) {{
                        if (maxPages - 1 - i < maxPagesInRow) {{
                            buttonsArray
                            .push(setPageButton(label, navigateTo, selected));
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
                            buttonsArray
                            .push(setPageButton(label, navigateTo, selected))
                        }}

                        if (currPage === i+2) {{
                            buttonsArray.push("...");
                        }}

                    }}
                }}

                selected = currPage === maxPages - 1 ? "selected" : "";

                buttonsArray.push(setPageButton(maxPages, maxPages - 1, selected))

                const buttonsHtml = buttonsArray.join("");
                document.querySelector("#pagesButtons").innerHTML = buttonsHtml;
            }}

            function initTable() {{
                const options = [10, 25, 50, 100];
                options_html =
                options.map(option => `<option value=${{option}}>${{option}}</option>`);

                let ths = {list(columns)}.map(col => `<th>${{col}}</th>`).join("");

                let table = `
                <div style="display: inline-flex">
                    <span style="margin-right: 5px">Show</span>
                    <select
                    onchange="handleRowsNumberOfRowsChange(this)">
                        ${{options_html}}
                    </select>
                    <span style="margin-left: 5px">entries</span>
                </div>

                <table
                    id="resultsTable"
                    style='width:100%'
                    curr-page-idx=0
                    rows-per-page={rows_per_page}
                    max-pages = {n_pages}
                    n-total={n_total}
                >
                    <thead>
                        <tr>
                            ${{ths}}
                        </tr>
                    </thead>

                    <tbody>
                    </tbody>
                </table>


                <div>
                    <button onclick="prevPageClick()">Previous</button>
                    <div id = "pagesButtons" style = "display: inline-flex">
                    </div>
                    <button onclick="nextPageClick()">Next</button>
                </div>
                `

                let tableContainer = document.querySelector("#tableContainer");
                tableContainer.innerHTML = table

                setTimeout(() => {{
                    fetchTableData(0, {rows_per_page}, (rows) => {{
                        updateTable({rows_per_page}, rows);
                        // update ths to make sure order columns
                        // are matching the data
                        if (rows.length > 0) {{
                            let row = rows[0];
                            let ths =
                            Object.keys(row).map(col => `<th>${{col}}</th>`).join("");
                            let thead = tableContainer.querySelector("thead")
                            thead.innerHTML = ths
                        }}
                    }})
                }}, 100);
            }}


            initTable()
        </script>
        """
        )
    )
