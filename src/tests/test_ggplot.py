from sql.ggplot import ggplot, aes, geom_boxplot, geom_histogram
from matplotlib.testing.decorators import image_comparison
import pytest
import duckdb

conn = duckdb.connect(database=":memory:")


@pytest.fixture
def short_trips_data(ip):
    ip.run_cell(
        """
        %%sql --save short-trips --no-execute
        select * from "yellow_tripdata_2021-01.parquet"
        WHERE trip_distance < 6.3
        """
    )


@pytest.fixture
def yellow_tripdata(tmp_empty):
    from pathlib import Path
    from urllib.request import urlretrieve

    url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet"

    if not Path("yellow_tripdata_2021-01.parquet").is_file():
        urlretrieve(url, "yellow_tripdata_2021-01.parquet")


@image_comparison(baseline_images=["boxplot"])
def test_ggplot_geom_boxplot(yellow_tripdata):
    ggplot(table="yellow_tripdata_2021-01.parquet", conn=conn) + \
        aes(x="trip_distance") + geom_boxplot()


@image_comparison(baseline_images=["histogram_default"], extensions=["png"])
def test_ggplot_geom_histogram(yellow_tripdata):
    ggplot(table="yellow_tripdata_2021-01.parquet", conn=conn) + \
        aes(x="trip_distance") + geom_histogram(bins=10, edgecolor="white")


@image_comparison(baseline_images=["histogram_with_default"])
def test_ggplot_geom_histogram_with(short_trips_data):
    ggplot(table="short-trips", with_="short-trips", conn=conn) + \
        aes(x="trip_distance") + geom_histogram(bins=10)


@image_comparison(baseline_images=["histogram_custom_edgecolor"], extensions=["png"])
def test_ggplot_geom_histogram_edge_color(short_trips_data):
    ggplot(table="short-trips", with_="short-trips", conn=conn) + \
        aes(x="trip_distance") + geom_histogram(bins=10, edgecolor="white")


@image_comparison(baseline_images=["histogram_custom_color"])
def test_ggplot_geom_histogram_color(short_trips_data):
    ggplot(table="short-trips", with_="short-trips", conn=conn) + \
        aes(x="trip_distance") + geom_histogram(bins=10, color="red")


@image_comparison(baseline_images=["histogram_custom_color_and_edge"])
def test_ggplot_geom_histogram_color_and_edge(short_trips_data):
    ggplot(table="short-trips", with_="short-trips", conn=conn) + \
        aes(x="trip_distance") + geom_histogram(bins=10, color="red", edgecolor="#fff")
