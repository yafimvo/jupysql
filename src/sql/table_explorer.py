from sql.connection import Connection
from IPython.display import display, HTML
from IPython import get_ipython
import math
import sqlalchemy
import time
from sql.util import (
    fetch_sql_with_pagination,
    parse_sql_results_to_json,
    is_table_exists,
)
import json
import os


def init_table(table) -> None:
    """
    Display an HTML table connected to a SQL engine

    Parameters
    ----------
    table str
        SQL Table name
    """

    is_table_exists(table)

    rows, columns = fetch_sql_with_pagination(table, 0, 10)
    rows_json = parse_sql_results_to_json(rows, columns)

    query = f"SELECT count(*) FROM {table}"
    n_total = Connection.current.session.execute(sqlalchemy.sql.text(query)).fetchone()[
        0
    ]
    table_name = table.strip('"').strip("'")

    rows_per_page = 10
    n_pages = math.ceil(n_total / rows_per_page)

    def front_listener(comm, open_msg):
        @comm.on_msg
        def _recv(msg):
            data = msg["content"]["data"]
            n_rows = data["nRows"]
            page = data["page"]

            sort_column = None
            sort_order = None
            table_name = data["table"]

            if "sort" in data:
                sort = data["sort"]
                sort_column = sort["column"]
                sort_order = sort["order"]

            offset = page * n_rows

            rows, columns = fetch_sql_with_pagination(
                table_name,
                offset,
                n_rows,
                sort_column=sort_column,
                sort_order=sort_order,
            )
            rows_json = parse_sql_results_to_json(rows, columns)

            comm.send({"rows": rows_json})

    # register kernel listener
    get_ipython().kernel.comm_manager.register_target("comm_target", front_listener)

    # output container
    unique_id = str(int(time.time()))
    table_container_id = f"tableContainer_{unique_id}"

    display(
        HTML(
            f"""
        <div id="{table_container_id}" class="table-container"></div>
        """
        )
    )

    # inject css
    display(
        HTML(
            """
        <style>
            .sort-button {
                background: none;
                border: none;
            }

            .sort-button.selected {
                background: #efefef;
                border: 1px solid #767676;
            }

            .pages-buttons button.selected {
                background: #efefef;
                border: 1px solid #767676;
                border-radius: 2px;
            }
            .pages-buttons button {
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
            function getTable(element) {{
                let table;
                if (element) {{
                    const tableContainer = element.closest(".table-container");
                    table = tableContainer.querySelector("table");
                }} else {{
                    table = document.querySelector(".code_cell.selected table");
                }}

                return table;
            }}

            function getSortDetails() {{
                let sort = undefined;

                const table = getTable();
                if (table) {{
                    const column = table.getAttribute("sort-by-column");
                    const order = table.getAttribute("sort-by-order");

                    if (column && order) {{
                        sort = {{
                            "column" : column,
                            "order" : order
                        }}
                    }}
                }}

                return sort;
            }}

            function sortColumnClick(element, column, order, callback) {{
                // fetch data with sort logic
                const table = getTable(element);
                table.setAttribute("sort-by-column", column);
                table.setAttribute("sort-by-order", order);
                const rowsPerPage = table.getAttribute("rows-per-page");
                const currrPage = table.getAttribute("curr-page-idx");

                const sort = {{
                    'column' : column,
                    'order' : order
                }}

                const fetchParameters = {{
                    rowsPerPage : parseInt(rowsPerPage),
                    page : parseInt(currrPage),
                    sort : sort,
                    table : table.getAttribute("table-name")
                }}

                fetchTableData(fetchParameters, callback)
            }}

            function fetchTableData(fetchParameters, callback) {{
                const comm =
                Jupyter.notebook.kernel.comm_manager.new_comm('comm_target', {{}})

                sendObject = {{
                    'nRows' : fetchParameters.rowsPerPage,
                    'page': fetchParameters.page,
                    'table' : fetchParameters.table
                }}

                if (fetchParameters.sort) {{
                    sendObject.sort = fetchParameters.sort
                }}

                comm.send(sendObject)

                comm.on_msg(function(msg) {{
                    const rows = JSON.parse(msg.content.data['rows']);
                    console.log("rows : ", rows)
                    if (callback) {{
                        callback(rows)
                    }}
                }});
            }}

            function handleRowsNumberOfRowsChange(e) {{
                const rows = {rows_json};
                const rowsPerPage = parseInt(e.value);
                let table = getTable();
                table.setAttribute('rows-per-page', rowsPerPage);

                const nTotal = table.getAttribute('n-total');

                const maxPages = Math.ceil(nTotal / rowsPerPage)
                table.setAttribute('max-pages', maxPages);

                const fetchParameters = {{
                    rowsPerPage : rowsPerPage,
                    page : 0,
                    sort : getSortDetails(),
                    table : table.getAttribute("table-name")
                }}

                setTimeout(() => {{
                    fetchTableData(fetchParameters, (rows) => {{
                        updateTable(rowsPerPage, rows);
                    }})
                }}, 100);
            }}

            function updateTable(rowsPerPage, rows, currPage, tableToUpdate) {{
                const table = tableToUpdate || getTable();
                const trs = table.querySelectorAll("tbody tr");
                const tbody = table.querySelector("tbody");
                tbody.innerHTML = "";

                const _html = rows.map(row => {{
                    const tds =
                    Object.keys(row).map(key => `<td>${{row[key]}}</td>`).join("");
                    return `<tr>${{tds}}</tr>`;
                }}).join("");

                tbody.innerHTML = _html

                setTimeout(() => {{
                    updatePaginationBar(table, currPage || 0)
                }}, 100)
            }}

            function showTablePage(page, rowsPerPage, data) {{
                const table = getTable();
                const trs = table.querySelectorAll("tbody tr");
                const tbody = table.querySelector("tbody");
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
                updatePaginationBar(table, page);
            }}

            function nextPageClick(element) {{
                const table = getTable(element);
                const currPageIndex = parseInt(table.getAttribute("curr-page-idx"));
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                const maxPages = parseInt(table.getAttribute("max-pages"));

                const nextPage = currPageIndex + 1;
                if (nextPage < maxPages) {{
                    const fetchParameters = {{
                        rowsPerPage : rowsPerPage,
                        page : nextPage,
                        sort : getSortDetails(),
                        table : table.getAttribute("table-name")
                    }}

                    fetchTableData(fetchParameters, (rows) => {{
                        showTablePage(nextPage, rowsPerPage, rows)
                    }});
                }}

            }}

            function prevPageClick() {{
                const table = getTable();
                const currPageIndex = parseInt(table.getAttribute("curr-page-idx"));
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                const prevPage = currPageIndex - 1;
                if (prevPage >= 0) {{
                    const fetchParameters = {{
                        rowsPerPage : rowsPerPage,
                        page : prevPage,
                        sort : getSortDetails(),
                        table : table.getAttribute("table-name")
                    }}

                    fetchTableData(fetchParameters, (rows) => {{
                        showTablePage(prevPage, rowsPerPage, rows)
                    }});
                }}
            }}

            function setPageButton(table, label, navigateTo, isSelected) {{
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                const selected = isSelected ? "selected" : "";

                const button = `
                <button class="${{selected}}"
                        onclick="
                        fetchTableData({{
                            rowsPerPage : ${{rowsPerPage}},
                            page : ${{navigateTo}},
                            sort : getSortDetails(),
                            table : getTable(this).getAttribute('table-name')
                        }},
                        (rows) => {{
                            showTablePage(${{navigateTo}}, ${{rowsPerPage}}, rows);
                            }})"
                >
                    ${{label}}
                </button>
                `
                return button;
            }}

            function updatePaginationBar(table, currPage) {{
                const maxPages = parseInt(table.getAttribute("max-pages"));
                const maxPagesInRow = 6;
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                table.setAttribute("curr-page-idx", currPage);

                let buttonsArray = []

                let startEllipsisAdded = false
                let endEllipsisAdded = false


                // add first
                let selected = currPage === 0;
                buttonsArray.push(setPageButton(table, "1", 0, selected));

                for (i = 1; i < maxPages - 1; i++) {{
                    const navigateTo = i;
                    const label = i + 1;
                    selected = currPage === i;
                    const inStartRange = currPage < maxPagesInRow;
                    const inEndRange = maxPages - 1 - currPage < maxPagesInRow;

                    if (inStartRange) {{
                        if (i < maxPagesInRow) {{
                            buttonsArray
                            .push(setPageButton(table, label, navigateTo, selected));
                        }} else {{
                        if (!startEllipsisAdded) {{
                            buttonsArray.push("...");
                            startEllipsisAdded = true;
                        }}
                        }}
                    }} else if (inEndRange) {{
                        if (maxPages - 1 - i < maxPagesInRow) {{
                            buttonsArray
                            .push(setPageButton(table, label, navigateTo, selected));
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
                            .push(setPageButton(table, label, navigateTo, selected))
                        }}

                        if (currPage === i+2) {{
                            buttonsArray.push("...");
                        }}

                    }}
                }}

                selected = currPage === maxPages - 1 ? "selected" : "";

                buttonsArray.
                push(setPageButton(table, maxPages, maxPages - 1, selected))

                const buttonsHtml = buttonsArray.join("");
                table.parentNode
                .querySelector(".pages-buttons").innerHTML = buttonsHtml;
            }}

            function removeSelectionFromAllSortButtons() {{
                document.querySelectorAll(".sort-button")
                .forEach(el => el.classList.remove("selected"))
            }}

            function initTable() {{
                const options = [10, 25, 50, 100];
                options_html =
                options.map(option => `<option value=${{option}}>${{option}}</option>`);

                let ths = {list(columns)}.map(col => `<th>${{col}}</th>`).join("");

                let table = `
                <div>
                    <span style="margin-right: 5px">Show</span>
                    <select
                    onchange="handleRowsNumberOfRowsChange(this)">
                        ${{options_html}}
                    </select>
                    <span style="margin-left: 5px">entries</span>
                </div>

                <table
                    id="resultsTable"
                    class="explore-table"
                    style='width:100%'
                    curr-page-idx=0
                    rows-per-page={rows_per_page}
                    max-pages = {n_pages}
                    n-total={n_total}
                    table-name={table_name}
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
                    <button onclick="prevPageClick(this)">Previous</button>
                    <div
                        id = "pagesButtons"
                        class = "pages-buttons"
                        style = "display: inline-flex">
                    </div>
                    <button onclick="nextPageClick(this)">Next</button>
                </div>
                `

                let tableContainer = document.querySelector("#{table_container_id}");
                tableContainer.innerHTML = table
                setTimeout(() => {{
                    const fetchParameters = {{
                        rowsPerPage : {rows_per_page},
                        page : 0,
                        sort : getSortDetails(),
                        table : "{table_name}"
                    }}

                    fetchTableData(fetchParameters, (rows) => {{
                        updateTable({rows_per_page}, rows, 0,
                                    tableContainer.querySelector("table"));
                        // update ths to make sure order columns
                        // are matching the data
                        if (rows.length > 0) {{
                            let row = rows[0];
                            let ths =
                            Object.keys(row).map(col =>
                            `<th>
                                <div style="display: inline-flex; height: 30px">
                                    <span style="line-height: 40px">${{col}}</span>
                                    <span style="width: 40px;">
                                        <button
                                            class = "sort-button"
                                            onclick='sortColumnClick(this,
                                            "${{col}}", "ASC",
                                            (rows) => {{
                                                const table = getTable(this);
                                                const currPage =
                                                parseInt(table.getAttribute("curr-page-idx"));
                                                updateTable({rows_per_page},
                                                            rows, currPage);
                                                removeSelectionFromAllSortButtons()
                                                this.className += " selected"
                                                }}
                                            )'
                                            title="Sort"
                                            >▴
                                        </button>
                                        <button
                                            class = "sort-button"
                                            onclick='sortColumnClick(this,
                                            "${{col}}", "DESC",
                                            (rows) => {{
                                                const table = getTable(this);
                                                const currPage = parseInt(
                                                    table.getAttribute("curr-page-idx"));
                                                updateTable({rows_per_page},
                                                            rows, currPage);
                                                removeSelectionFromAllSortButtons()
                                                this.className += " selected"
                                                }}
                                            )'
                                            title="Sort"
                                            >▾
                                        </button>
                                    </span>
                                </div>

                                </th>`).join("");
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


def init_websocket_test(table):
    import threading
    import asyncio
    import websockets

    async def websocket_handler(websocket, path):
        # WebSocket handler code goes here
        data = await websocket.recv()

        data = json.loads(data)
        n_rows = data["nRows"]
        page = data["page"]

        sort_column = None
        sort_order = None
        table_name = data["table"]

        if "sort" in data:
            sort = data["sort"]
            sort_column = sort["column"]
            sort_order = sort["order"]

        offset = page * n_rows

        rows, columns = fetch_sql_with_pagination(
            table_name,
            offset,
            n_rows,
            sort_column=sort_column,
            sort_order=sort_order,
        )
        rows_json = parse_sql_results_to_json(rows, columns)

        await websocket.send(rows_json)

    def start_websocket_server():
        asyncio.set_event_loop(asyncio.new_event_loop())
        base_url = _get_base_url()
        start_server = websockets.serve(websocket_handler, base_url, 0)
        asyncio.get_event_loop().run_until_complete(start_server)
        running_port = start_server.ws_server.sockets[0].getsockname()[1]
        _display_ui(running_port, table)
        asyncio.get_event_loop().run_forever()

    # Create a new thread and start the WebSocket server in that thread
    websocket_thread = threading.Thread(target=start_websocket_server)
    websocket_thread.start()


def _display_ui(port, table):
    ip = _get_connection_ip()

    rows, columns = fetch_sql_with_pagination(table, 0, 10)
    rows_json = parse_sql_results_to_json(rows, columns)

    query = f"SELECT count(*) FROM {table}"
    n_total = Connection.current.session.execute(sqlalchemy.sql.text(query)).fetchone()[
        0
    ]
    table_name = table.strip('"').strip("'")

    rows_per_page = 10
    n_pages = math.ceil(n_total / rows_per_page)

    # output container
    unique_id = str(int(time.time()))
    table_container_id = f"tableContainer_{unique_id}"

    display(
        HTML(
            f"""
        <div id="{table_container_id}" class="table-container"></div>
        """
        )
    )

    # inject css
    display(
        HTML(
            """
        <style>
            .sort-button {
                background: none;
                border: none;
            }

            .sort-button.selected {
                background: #efefef;
                border: 1px solid #767676;
            }

            .pages-buttons button.selected {
                background: #efefef;
                border: 1px solid #767676;
                border-radius: 2px;
            }
            .pages-buttons button {
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
            function getTable(element) {{
                let table;
                if (element) {{
                    const tableContainer = element.closest(".table-container");
                    table = tableContainer.querySelector("table");
                }} else {{
                    // table = document.querySelector(".code_cell.selected table");
                    table = document.querySelector(".table-container table")
                }}

                return table;
            }}

            function getSortDetails() {{
                let sort = undefined;

                const table = getTable();
                if (table) {{
                    const column = table.getAttribute("sort-by-column");
                    const order = table.getAttribute("sort-by-order");

                    if (column && order) {{
                        sort = {{
                            "column" : column,
                            "order" : order
                        }}
                    }}
                }}

                return sort;
            }}

            function sortColumnClick(element, column, order, callback) {{
                // fetch data with sort logic
                const table = getTable(element);
                table.setAttribute("sort-by-column", column);
                table.setAttribute("sort-by-order", order);
                const rowsPerPage = table.getAttribute("rows-per-page");
                const currrPage = table.getAttribute("curr-page-idx");

                const sort = {{
                    'column' : column,
                    'order' : order
                }}

                const fetchParameters = {{
                    rowsPerPage : parseInt(rowsPerPage),
                    page : parseInt(currrPage),
                    sort : sort,
                    table : table.getAttribute("table-name")
                }}

                fetchTableData(fetchParameters, callback)
            }}

            function fetchTableData(fetchParameters, callback) {{
                
                var socket = new WebSocket(`wss://{ip}:{port}`);
    
                socket.addEventListener('open', function (event) {{
                    sendObject = {{
                        'nRows' : fetchParameters.rowsPerPage,
                        'page': fetchParameters.page,
                        'table' : fetchParameters.table
                    }}

                    if (fetchParameters.sort) {{
                        sendObject.sort = fetchParameters.sort
                    }}

                    socket.send(JSON.stringify(sendObject))
                
                }});
                
                socket.addEventListener('message', function (event) {{
                    const rows = JSON.parse(event.data);
                    console.log("rows : ", rows)
                    if (callback) {{
                        callback(rows)
                    }}

                }});
            }}

            function handleRowsNumberOfRowsChange(e) {{
                const rows = {rows_json};
                const rowsPerPage = parseInt(e.value);
                let table = getTable();
                table.setAttribute('rows-per-page', rowsPerPage);

                const nTotal = table.getAttribute('n-total');

                const maxPages = Math.ceil(nTotal / rowsPerPage)
                table.setAttribute('max-pages', maxPages);

                const fetchParameters = {{
                    rowsPerPage : rowsPerPage,
                    page : 0,
                    sort : getSortDetails(),
                    table : table.getAttribute("table-name")
                }}

                setTimeout(() => {{
                    fetchTableData(fetchParameters, (rows) => {{
                        updateTable(rowsPerPage, rows);
                    }})
                }}, 100);
            }}

            function updateTable(rowsPerPage, rows, currPage, tableToUpdate) {{
                const table = tableToUpdate || getTable();
                const trs = table.querySelectorAll("tbody tr");
                const tbody = table.querySelector("tbody");
                tbody.innerHTML = "";

                const _html = rows.map(row => {{
                    const tds =
                    Object.keys(row).map(key => `<td>${{row[key]}}</td>`).join("");
                    return `<tr>${{tds}}</tr>`;
                }}).join("");

                tbody.innerHTML = _html

                setTimeout(() => {{
                    updatePaginationBar(table, currPage || 0)
                }}, 100)
            }}

            function showTablePage(page, rowsPerPage, data) {{
                const table = getTable();
                const trs = table.querySelectorAll("tbody tr");
                const tbody = table.querySelector("tbody");
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
                updatePaginationBar(table, page);
            }}

            function nextPageClick(element) {{
                const table = getTable(element);
                const currPageIndex = parseInt(table.getAttribute("curr-page-idx"));
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                const maxPages = parseInt(table.getAttribute("max-pages"));

                const nextPage = currPageIndex + 1;
                if (nextPage < maxPages) {{
                    const fetchParameters = {{
                        rowsPerPage : rowsPerPage,
                        page : nextPage,
                        sort : getSortDetails(),
                        table : table.getAttribute("table-name")
                    }}

                    fetchTableData(fetchParameters, (rows) => {{
                        showTablePage(nextPage, rowsPerPage, rows)
                    }});
                }}

            }}

            function prevPageClick() {{
                const table = getTable();
                const currPageIndex = parseInt(table.getAttribute("curr-page-idx"));
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                const prevPage = currPageIndex - 1;
                if (prevPage >= 0) {{
                    const fetchParameters = {{
                        rowsPerPage : rowsPerPage,
                        page : prevPage,
                        sort : getSortDetails(),
                        table : table.getAttribute("table-name")
                    }}

                    fetchTableData(fetchParameters, (rows) => {{
                        showTablePage(prevPage, rowsPerPage, rows)
                    }});
                }}
            }}

            function setPageButton(table, label, navigateTo, isSelected) {{
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                const selected = isSelected ? "selected" : "";

                const button = `
                <button class="${{selected}}"
                        onclick="
                        fetchTableData({{
                            rowsPerPage : ${{rowsPerPage}},
                            page : ${{navigateTo}},
                            sort : getSortDetails(),
                            table : getTable(this).getAttribute('table-name')
                        }},
                        (rows) => {{
                            showTablePage(${{navigateTo}}, ${{rowsPerPage}}, rows);
                            }})"
                >
                    ${{label}}
                </button>
                `
                return button;
            }}

            function updatePaginationBar(table, currPage) {{
                const maxPages = parseInt(table.getAttribute("max-pages"));
                const maxPagesInRow = 6;
                const rowsPerPage = parseInt(table.getAttribute("rows-per-page"));
                table.setAttribute("curr-page-idx", currPage);

                let buttonsArray = []

                let startEllipsisAdded = false
                let endEllipsisAdded = false


                // add first
                let selected = currPage === 0;
                buttonsArray.push(setPageButton(table, "1", 0, selected));

                for (i = 1; i < maxPages - 1; i++) {{
                    const navigateTo = i;
                    const label = i + 1;
                    selected = currPage === i;
                    const inStartRange = currPage < maxPagesInRow;
                    const inEndRange = maxPages - 1 - currPage < maxPagesInRow;

                    if (inStartRange) {{
                        if (i < maxPagesInRow) {{
                            buttonsArray
                            .push(setPageButton(table, label, navigateTo, selected));
                        }} else {{
                        if (!startEllipsisAdded) {{
                            buttonsArray.push("...");
                            startEllipsisAdded = true;
                        }}
                        }}
                    }} else if (inEndRange) {{
                        if (maxPages - 1 - i < maxPagesInRow) {{
                            buttonsArray
                            .push(setPageButton(table, label, navigateTo, selected));
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
                            .push(setPageButton(table, label, navigateTo, selected))
                        }}

                        if (currPage === i+2) {{
                            buttonsArray.push("...");
                        }}

                    }}
                }}

                selected = currPage === maxPages - 1 ? "selected" : "";

                buttonsArray.
                push(setPageButton(table, maxPages, maxPages - 1, selected))

                const buttonsHtml = buttonsArray.join("");
                table.parentNode
                .querySelector(".pages-buttons").innerHTML = buttonsHtml;
            }}

            function removeSelectionFromAllSortButtons() {{
                document.querySelectorAll(".sort-button")
                .forEach(el => el.classList.remove("selected"))
            }}

            function initTable() {{
                const options = [10, 25, 50, 100];
                options_html =
                options.map(option => `<option value=${{option}}>${{option}}</option>`);

                let ths = {list(columns)}.map(col => `<th>${{col}}</th>`).join("");

                let table = `
                <div>
                    <span style="margin-right: 5px">Show</span>
                    <select
                    onchange="handleRowsNumberOfRowsChange(this)">
                        ${{options_html}}
                    </select>
                    <span style="margin-left: 5px">entries</span>
                </div>

                <table
                    id="resultsTable"
                    class="explore-table"
                    style='width:100%'
                    curr-page-idx=0
                    rows-per-page={rows_per_page}
                    max-pages = {n_pages}
                    n-total={n_total}
                    table-name={table_name}
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
                    <button onclick="prevPageClick(this)">Previous</button>
                    <div
                        id = "pagesButtons"
                        class = "pages-buttons"
                        style = "display: inline-flex">
                    </div>
                    <button onclick="nextPageClick(this)">Next</button>
                </div>
                `

                let tableContainer = document.querySelector("#{table_container_id}");
                tableContainer.innerHTML = table
                setTimeout(() => {{
                    const fetchParameters = {{
                        rowsPerPage : {rows_per_page},
                        page : 0,
                        sort : getSortDetails(),
                        table : "{table_name}"
                    }}

                    fetchTableData(fetchParameters, (rows) => {{
                        updateTable({rows_per_page}, rows, 0,
                                    tableContainer.querySelector("table"));
                        // update ths to make sure order columns
                        // are matching the data
                        if (rows.length > 0) {{
                            let row = rows[0];
                            let ths =
                            Object.keys(row).map(col =>
                            `<th>
                                <div style="display: inline-flex; height: 30px">
                                    <span style="line-height: 40px">${{col}}</span>
                                    <span style="width: 40px;">
                                        <button
                                            class = "sort-button"
                                            onclick='sortColumnClick(this,
                                            "${{col}}", "ASC",
                                            (rows) => {{
                                                const table = getTable(this);
                                                const currPage =
                                                parseInt(table.getAttribute("curr-page-idx"));
                                                updateTable({rows_per_page},
                                                            rows, currPage);
                                                removeSelectionFromAllSortButtons()
                                                this.className += " selected"
                                                }}
                                            )'
                                            title="Sort"
                                            >▴
                                        </button>
                                        <button
                                            class = "sort-button"
                                            onclick='sortColumnClick(this,
                                            "${{col}}", "DESC",
                                            (rows) => {{
                                                const table = getTable(this);
                                                const currPage = parseInt(
                                                    table.getAttribute("curr-page-idx"));
                                                updateTable({rows_per_page},
                                                            rows, currPage);
                                                removeSelectionFromAllSortButtons()
                                                this.className += " selected"
                                                }}
                                            )'
                                            title="Sort"
                                            >▾
                                        </button>
                                    </span>
                                </div>

                                </th>`).join("");
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


def _get_connection_ip():
    from ipykernel.connect import get_connection_info

    connection_info = get_connection_info()
    connection_info = json.loads(connection_info)
    return connection_info["ip"]


# utils
def _get_base_url():
    if _is_binder():
        base_url = _get_binder_hub_url()
    else:
        base_url = _get_connection_ip()

    return base_url


def _is_binder():
    return 'JUPYTERHUB_SERVICE_PREFIX' in os


def _get_binder_hub_url():
    service_prefix = os['JUPYTERHUB_SERVICE_PREFIX']
    binder_launch_host = os['BINDER_LAUNCH_HOST']
    binder_launch_host = binder_launch_host.replace("https://", "https://hub.")
    binder_hub_url = f"{binder_launch_host}{service_prefix}"
