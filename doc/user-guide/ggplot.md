---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
myst:
  html_meta:
    description lang=en: Templatize SQL queries in Jupyter via JupySQL
    keywords: jupyter, sql, jupysql, jinja
    property=og:locale: en_US
---

# ggplot

Use our Grammar of Graphics API to visualize your data.

## Download the data

```{code-cell} ipython3
from pathlib import Path
from urllib.request import urlretrieve

url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet"

if not Path("yellow_tripdata_2021-01.parquet").is_file():
    urlretrieve(url, "yellow_tripdata_2021-01.parquet")
```
## Setup

```{code-cell} ipython3
%load_ext sql
%sql duckdb://
```

```{code-cell} ipython3
from sql.ggplot import ggplot, aes, geom_boxplot, geom_histogram
```

## Boxplot

```{code-cell} ipython3
ggplot(table="yellow_tripdata_2021-01.parquet") + aes(x="trip_distance") + geom_boxplot()
```

## Histogram

To make it more interesting, let's create a query that filters by the 90th percentile. Note that we're using the `--save`, and `--no-execute` functions. This tells JupySQL to store the query, but *skips execution*. We'll reference it in our next plotting call.

```{code-cell} ipython3
%%sql --save short-trips --no-execute
select * from "yellow_tripdata_2021-01.parquet"
WHERE trip_distance < 6.3
```

```{code-cell} ipython3
ggplot(table="short-trips", with_="short-trips")
+ aes(x="trip_distance")
+ geom_histogram(bins=10)
```

## Custom Style

We can set a custom style by setting the `color` and `edgecolor` attributes on `geom_histogram`

```{code-cell} ipython3
ggplot(table="short-trips", with_="short-trips")
+ aes(x="trip_distance")
+ geom_histogram(bins=10, color="#69f0ae", edgecolor="#fff")
```