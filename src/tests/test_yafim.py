def test_connection(ip, capsys):
    # import urllib

    # urllib.request.urlretrieve(
    #     "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv",  # noqa breaks the check-for-broken-links
    #     "penguins.csv",
    # )
    ip.run_cell(
        """
        import duckdb
        conn = duckdb.connect()
        %sql conn
        """
    )

    ip.run_cell(
        """
        %sql select * from 'https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv' limit 3
        """
    )

    # ip.run_cell(
    #     """
    #     %sql duckdb://
    #     """
    # )

    # ip.run_cell('%sql --connection_arguments {\"timeout\":10} sqlite:///:memory:')

    with capsys.disabled():
        o, e = capsys.readouterr()
        print(o)
