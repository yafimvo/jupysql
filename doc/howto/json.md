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
myst:
  html_meta:
    description lang=en: Use JupySQL and DuckDB to query JSON files with SQL
    keywords: jupyter, sql, jupysql, json, duckdb
    property=og:locale: en_US
---

# Run SQL on JSON files

In this tutorial, we'll show you how to query JSON with JupySQL and DuckDB.


First, let's install the required dependencies:

```{code-cell} ipython3
:tags: [remove-cell]

# this cell won't be visible in the docs
from pathlib import Path

paths = ["people.jsonl", "people.csv"]

for path in paths:
    path = Path(path)

    if path.exists():
        print(f"Deleting {path}")
        path.unlink()
```

```{code-cell} ipython3
:tags: [hide-output]

%pip install jupysql duckdb duckdb-engine rich --quiet
```

Now, let's generate some data. Note that DuckDB expects your data to contain *one JSON object per line*; this format is called [JSON Lines](https://jsonlines.org/), and it often comes with the `.json`, `.jsonl.gz`, or `.jsonl.bz2` extension.

Our sample data contains four rows:

```{code-cell} ipython3
from pathlib import Path
import json

data = [
    {
        "name": "John",
        "age": 25,
        "friends": ["Jake", "Kelly"],
        "likes": {"pizza": True, "tacos": True},
    },
    {
        "name": "Jake",
        "age": 20,
        "friends": ["John"],
        "likes": {"pizza": False, "tacos": True},
    },
    {
        "name": "Kelly",
        "age": 21,
        "friends": ["John", "Sam"],
        "likes": {"pizza": True, "tacos": True},
    },
    {
        "name": "Sam",
        "age": 22,
        "friends": ["Kelly"],
        "likes": {"pizza": False, "tacos": True},
    },
]

lines = ""

for d in data:
    lines += json.dumps(d) + "\n"

_ = Path("people.jsonl").write_text(lines)
```

```{code-cell} ipython3
print(lines)
```

## Query

```{note}
Documentation for DuckDB's JSON capabilities is available [here](https://duckdb.org/docs/extensions/json.html).
```

Load the extension and start a DuckDB in-memory database:

```{code-cell} ipython3
%load_ext sql
%sql duckdb://
```

Read the JSON data:

```{code-cell} ipython3
%%sql
SELECT *
FROM read_json_objects('people.jsonl')
```

## Extract fields

Extract fields from each JSON record:

```{code-cell} ipython3
%%sql
SELECT
    json ->> '$.name' AS name,
    json ->> '$.friends[0]' AS first_friend,
    json ->> '$.likes.pizza' AS likes_pizza,
    json ->> '$.likes.tacos' AS likes_tacos,
FROM read_json_objects('people.jsonl')
```

Looks like everybody likes tacos!

+++

## Extract schema

Infer the JSON schema:

```{code-cell} ipython3
%%sql
SELECT
    json_structure(json),
    json_structure(json ->> '$.likes'),
FROM read_json_objects('people.jsonl')
```

```{code-cell} ipython3
%%sql schema <<
SELECT
    json_structure(json) AS schema_all,
    json_structure(json ->> '$.likes') AS schema_likes,
FROM read_json_objects('people.jsonl')
```

Pretty print the inferred schema:

```{code-cell} ipython3
from rich import print_json

row = schema.DataFrame().iloc[0]

print("Schema:")
print_json(row.schema_all)

print("\n\nSchema (likes):")
print_json(row.schema_likes)
```

## Store snippets

You can use JupySQL's `--save` feature to store a SQL snippet so you can keep your queries succint:

```{code-cell} ipython3
%%sql --save clean_data
SELECT
    json ->> '$.name' AS name,
    json ->> '$.friends[0]' AS first_friend,
    json ->> '$.likes.pizza' AS likes_pizza,
    json ->> '$.likes.tacos' AS likes_tacos,
FROM read_json_objects('people.jsonl')
```

```{code-cell} ipython3
%%sql --with clean_data
SELECT * FROM clean_data
```

## Export to CSV

```{note}
Using `--with` isn't supported when exporting to CSV.
```

To export to CSV:

```{code-cell} ipython3
%%sql
COPY (
    SELECT
    json ->> '$.name' AS name,
    json ->> '$.friends[0]' AS first_friend,
    json ->> '$.likes.pizza' AS likes_pizza,
    json ->> '$.likes.tacos' AS likes_tacos,
    FROM read_json_objects('people.jsonl')
)

TO 'people.csv' (HEADER, DELIMITER ',');
```

```{code-cell} ipython3
%%sql
SELECT * FROM 'people.csv'
```
