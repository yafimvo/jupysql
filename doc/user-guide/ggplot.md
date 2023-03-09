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

The `ggplot` API is structured around the principles of the grammar of graphics, and it comprises three primary components:
1. Data - a reference to our SQL tables
2. Aesthetic - A mapping of one or more variables to one or more visual elements on the graph, e.g: map `x` and `y` to the x-axis and the y-axis.
3. Geometric - The type or shape of the visual elements on the graph, e.g: `geom_boxplot` and `geom_histogram`


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
:tags: [hide-output]

%load_ext sql
%sql duckdb://
```

## Import
```{code-cell} ipython3
from sql.ggplot import ggplot, aes, geom_boxplot, geom_histogram
```

## Example : Boxplot

```{code-cell} ipython3
(
    ggplot(table="yellow_tripdata_2021-01.parquet")
    + aes(x="trip_distance") # noqa
    + geom_boxplot() # noqa
)
```

## Example : Histogram

To make it more interesting, let's create a query that filters by the 90th percentile. Note that we're using the `--save`, and `--no-execute` functions. This tells JupySQL to store the query, but *skips execution*. We'll reference it in our next plotting call.

```{code-cell} ipython3
%%sql --save short-trips --no-execute
select * from "yellow_tripdata_2021-01.parquet"
WHERE trip_distance < 6.3
```

```{code-cell} ipython3
(
    ggplot(table="short-trips", with_="short-trips")
    + aes(x="trip_distance")
    + geom_histogram(bins=10)
)
```

## Example : Custom Style

By modifying the `color` and `edgecolor` attributes, we can apply our custom style

```{code-cell} ipython3
(
    ggplot(table="short-trips", with_="short-trips")
    + aes(x="trip_distance")
    + geom_histogram(bins=10, color="#69f0ae", edgecolor="#fff")
)
```