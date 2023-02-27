---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Explore tables

When dealing with a new dataset, it's crucial for practitioners to have a comprehensive understanding of the data in a timely manner. This involves exploring and summarizing the dataset efficiently to extract valuable insights. However, this can be a time-consuming process. Fortunately, `%sqlcmd profile` offers an easy way to generate statistics and descriptive information, enabling practitioners to quickly gain a deeper understanding of the dataset.

Availble statistics:

* The count of non empty values
* The number of unique values
* The top (most frequent) value
* The frequency of your top value
* The mean, standard deviation, min and max values
* The percentiles of your data: 25%, 50% and 75%.


## Examples

### Simple example with SQLite

```{code-cell} ipython3
:tags: [hide-output]

%load_ext sql
%sql sqlite://
```

Let's create our table

```{code-cell} ipython3
:tags: [hide-output]

%%sql sqlite://
CREATE TABLE example_table (rating, price, number, symbol);
INSERT INTO example_table VALUES (14.44, 2.48, 82, 'a');
INSERT INTO example_table VALUES (13.13, 1.50, 93, 'b');
INSERT INTO example_table VALUES (12.59, 0.20, 98, 'a');
INSERT INTO example_table VALUES (11.54, 0.41, 89, 'a');
INSERT INTO example_table VALUES (10.532, 0.1, 88, 'c');
INSERT INTO example_table VALUES (11.5, 0.2, 84, 'b');
INSERT INTO example_table VALUES (11.1, 0.3, 90, 'a');
INSERT INTO example_table VALUES (12.9, 0.31, 86, '');
INSERT INTO example_table VALUES (12.9, 0.31, 86, '    ');
```

```{code-cell} ipython3
%sqlcmd profile -t example_table
```

### Large datasets

We can easily explore large SQlite database using DuckDB.

```{code-cell} ipython3
:tags: [hide-output]

import urllib.request
from pathlib import Path

if not Path("example.db").is_file():
    url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"  # noqa
    urllib.request.urlretrieve(url, "example.db")
```


```{code-cell} ipython3
:tags: [hide-output]

%%sql duckdb:///
INSTALL 'sqlite_scanner';
LOAD 'sqlite_scanner';
CALL sqlite_attach('example.db');
```

```{code-cell} ipython3
%sqlcmd profile -t track
```