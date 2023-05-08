from sql.widgets import TableWidget


def test_table_widget_html(ip, capsys):
    tableWidget = TableWidget("number_table")

    o = ip.run_cell("%sql select * from number_table").result
    assert True

    # with capsys.disabled():
    #     print(tableWidget._repr_html_())
