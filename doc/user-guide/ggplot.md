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
    + aes(x="trip_distance")
    + geom_boxplot()
)
```

## Example : Histogram

To make it more interesting, let's create a query that filters by the 90th percentile. Note that we're using the `--save`, and `--no-execute` functions. This tells JupySQL to store the query, but *skips execution*. We'll reference it in our next plotting call.

```{code-cell} ipython3
%%sql --save short-trips --no-execute
select * from 'yellow_tripdata_2021-01.parquet'
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

By modifying the `fill` and `color` attributes, we can apply our custom style

```{code-cell} ipython3
(
    ggplot(table="short-trips", with_="short-trips")
    + aes(x="trip_distance")
    + geom_histogram(bins=10, fill="#69f0ae", color="#fff")
)
```

When using multiple columns we can apply color on each column

```{code-cell} ipython3
(
    ggplot(table="short-trips", with_="short-trips")
    + aes(x=["PULocationID", "DOLocationID"])
    + geom_histogram(bins=10, fill=["#d500f9", "#fb8c00"], color="white")
)
```

## Example : Categorical histogram

To make it easier to demonstrate, let's use `ggplot2` diamonds dataset.

```{code-cell} ipython3
from pathlib import Path
from urllib.request import urlretrieve

if not Path("diamonds.csv").is_file():
    urlretrieve(
        "https://raw.githubusercontent.com/tidyverse/ggplot2/main/data-raw/diamonds.csv", # noqa
        "diamonds.csv",
    )
```

```{code-cell} ipython3
%%sql
CREATE TABLE diamonds AS SELECT * FROM diamonds.csv
```

Now, let's create a histogram of the different cuts of the diamonds by setting `x='cut'`.
Please note, since the values of `cut` are strings, we don't need the `bins` attribute here.

```{code-cell} ipython3
(ggplot(table="diamonds") + aes(x="cut") + geom_histogram())
```

We can show a histogram of multiple columns by setting `x=['cut', 'color']`

```{code-cell} ipython3
(ggplot(table="diamonds") + aes(x=["cut", "color"]) + geom_histogram())
```

Apply a custom color with `color` and `fill`

```{code-cell} ipython3
(
    ggplot(table="diamonds")
    + aes(x="price", fill="cut")
    + geom_histogram(bins=10, fill="green", color="white")
)
```

If we map the `fill` aesthetic to a different variable such as `payment_type`, the bars will stack automatically. Each colored rectangle on the stacked bars will represent a unique combination of `price` and `cut`.

```{code-cell} ipython3
(ggplot(table="diamonds") + aes(x="price", fill="cut") + geom_histogram(bins=10))
```

We can apply a different coloring using `cmap`

```{code-cell} ipython3
(
    ggplot(table="diamonds")
    + aes(x="price", fill="cut", cmap="plasma")
    + geom_histogram(bins=10)
)
```
