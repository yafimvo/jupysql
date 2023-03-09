from sql.ggplot import ggplot, aes, geom_boxplot, geom_histogram
from matplotlib.testing.decorators import image_comparison
import pytest
import duckdb
from pathlib import Path
from urllib.request import urlretrieve

conn = duckdb.connect(database=":memory:")


@pytest.fixture
def short_trips_data(ip, yellow_tripdata):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    ip.run_cell(
        f"""
        %%sql --save short-trips --no-execute
        select * from "{yellow_tripdata}"
        WHERE trip_distance < 6.3
        """
    )

    yield "short-trips"


@pytest.fixture
def yellow_tripdata(tmpdir):
    file_path_str = str(tmpdir.join("yellow_tripdata_2021-01.parquet"))

    if not Path(file_path_str).is_file():
        urlretrieve(
            "https://d37ci6vzurychx.cloudfront.net/trip-data/"
            "yellow_tripdata_2021-01.parquet",
            file_path_str,
        )

    yield file_path_str


@image_comparison(baseline_images=["boxplot"], extensions=["png"], remove_text=True)
def test_ggplot_geom_boxplot(ip, yellow_tripdata):
    ip.run_cell(
        """
    %sql duckdb://
    """
    )

    (ggplot(table=yellow_tripdata, conn=conn) + aes(x="trip_distance") + geom_boxplot())


@image_comparison(
    baseline_images=["histogram_default"], extensions=["png"], remove_text=True
)
def test_ggplot_geom_histogram(ip, yellow_tripdata):
    ip.run_cell(
        """
    %sql duckdb://
    """
    )

    (
        ggplot(table=yellow_tripdata, conn=conn)
        + aes(x="trip_distance")
        + geom_histogram(bins=10, edgecolor="white")
    )


@image_comparison(
    baseline_images=["histogram_with_default"], extensions=["png"], remove_text=True
)
def test_ggplot_geom_histogram_with(short_trips_data):
    (
        ggplot(table=short_trips_data, with_="short-trips", conn=conn)
        + aes(x="trip_distance")
        + geom_histogram(bins=10)
    )


# @image_comparison(
#     baseline_images=["histogram_custom_edgecolor"], extensions=["png"],
# remove_text=True
# )
# def test_ggplot_geom_histogram_edge_color(short_trips_data):
#     (
#         ggplot(table="short-trips", with_="short-trips", conn=conn)
#         + aes(x="trip_distance")
#         + geom_histogram(bins=10, edgecolor="white")
#     )


# @image_comparison(
#     baseline_images=["histogram_custom_color"], extensions=["png"], remove_text=True
# )
# def test_ggplot_geom_histogram_color(short_trips_data):
#     (
#         ggplot(table="short-trips", with_="short-trips", conn=conn)
#         + aes(x="trip_distance")
#         + geom_histogram(bins=10, color="red")
#     )


# @image_comparison(
#     baseline_images=["histogram_custom_color_and_edge"],
#     extensions=["png"],
#     remove_text=True,
# )
# def test_ggplot_geom_histogram_color_and_edge(short_trips_data):
#     (
#         ggplot(table="short-trips", with_="short-trips", conn=conn)
#         + aes(x="trip_distance")
#         + geom_histogram(bins=10, color="red", edgecolor="#fff")
#     )
