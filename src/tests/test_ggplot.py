from sql.ggplot import ggplot, aes, geom_boxplot, geom_histogram
from matplotlib.testing.decorators import image_comparison, cleanup
import pytest
from pathlib import Path
from urllib.request import urlretrieve


@pytest.fixture
def short_trips_data(ip, yellow_trip_data):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    ip.run_cell(
        f"""
        %%sql --save short-trips --no-execute
        select * from "{yellow_trip_data}"
        WHERE trip_distance < 6.3
        """
    ).result


@pytest.fixture
def yellow_trip_data(tmpdir):
    file_path_str = str(tmpdir.join("yellow_tripdata_2021-01.parquet"))

    if not Path(file_path_str).is_file():
        urlretrieve(
            "https://d37ci6vzurychx.cloudfront.net/trip-data/"
            "yellow_tripdata_2021-01.parquet",
            file_path_str,
        )

    yield file_path_str


@pytest.fixture
def diamonds_data(tmpdir):
    file_path_str = str(tmpdir.join("diamonds.csv"))

    if not Path(file_path_str).is_file():
        urlretrieve(
            "https://raw.githubusercontent.com/tidyverse/ggplot2/"
            + "main/data-raw/diamonds.csv",
            file_path_str,
        )

    yield file_path_str


@cleanup
@image_comparison(baseline_images=["boxplot"], extensions=["png"], remove_text=True)
def test_ggplot_geom_boxplot(ip, yellow_trip_data):
    ip.run_cell(
        """
    %sql duckdb://
    """
    )
    (ggplot(table=yellow_trip_data) + aes(x="trip_distance") + geom_boxplot())


@cleanup
@image_comparison(
    baseline_images=["histogram_default"], extensions=["png"], remove_text=True
)
def test_ggplot_geom_histogram(ip, yellow_trip_data):
    ip.run_cell(
        """
    %sql duckdb://
    """
    )

    (
        ggplot(table=yellow_trip_data)
        + aes(x="trip_distance")
        + geom_histogram(bins=10, color="white")
    )


@cleanup
@image_comparison(
    baseline_images=["histogram_with_default"], extensions=["png"], remove_text=True
)
def test_ggplot_geom_histogram_with(short_trips_data):
    (
        ggplot(table="short-trips", with_="short-trips")
        + aes(x="trip_distance")
        + geom_histogram(bins=10)
    )


@cleanup
@image_comparison(
    baseline_images=["histogram_custom_color"], extensions=["png"], remove_text=True
)
def test_ggplot_geom_histogram_edge_color(short_trips_data):
    (
        ggplot(table="short-trips", with_="short-trips")
        + aes(x="trip_distance")
        + geom_histogram(bins=10, color="white")
    )


@cleanup
@image_comparison(
    baseline_images=["histogram_custom_fill"], extensions=["png"], remove_text=True
)
def test_ggplot_geom_histogram_fill(short_trips_data):
    (
        ggplot(table="short-trips", with_="short-trips")
        + aes(x="trip_distance")
        + geom_histogram(bins=10, fill="red")
    )


@cleanup
@image_comparison(
    baseline_images=["histogram_custom_fill_and_color"],
    extensions=["png"],
    remove_text=True,
)
def test_ggplot_geom_histogram_fill_and_color(short_trips_data):
    (
        ggplot(table="short-trips", with_="short-trips")
        + aes(x="trip_distance")
        + geom_histogram(bins=10, fill="red", color="#fff")
    )


@pytest.mark.parametrize(
    "x",
    [
        "price",
        ["price"],
    ],
)
@cleanup
@image_comparison(
    baseline_images=["histogram_stacked_default"],
    extensions=["png"],
    remove_text=True,
)
def test_example_histogram_stacked_default(ip, diamonds_data, x):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    (ggplot(table=diamonds_data) + aes(x=x, fill="cut") + geom_histogram(bins=10))


@cleanup
@image_comparison(
    baseline_images=["histogram_stacked_custom_cmap"],
    extensions=["png"],
    remove_text=True,
)
def test_example_histogram_stacked_custom_cmap(ip, diamonds_data):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    (
        ggplot(table=diamonds_data)
        + aes(x="price", fill="cut", cmap="plasma")
        + geom_histogram(bins=10)
    )


@cleanup
@image_comparison(
    baseline_images=["histogram_stacked_custom_color"],
    extensions=["png"],
    remove_text=True,
)
def test_example_histogram_stacked_custom_color(ip, diamonds_data):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    (
        ggplot(table=diamonds_data)
        + aes(x="price", cmap="plasma", fill="cut")
        + geom_histogram(bins=10, color="k")
    )


@cleanup
@image_comparison(
    baseline_images=["histogram_stacked_custom_color_and_fill"],
    extensions=["png"],
    remove_text=True,
)
def test_example_histogram_stacked_custom_color_and_fill(ip, diamonds_data):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    (
        ggplot(table=diamonds_data)
        + aes(x="price", cmap="plasma", fill="cut")
        + geom_histogram(bins=10, color="white", fill="red")
    )


@cleanup
@image_comparison(
    baseline_images=["histogram_stacked_custom_color_and_fill"], extensions=["png"], remove_text=True
)
def test_ggplot_geom_histogram_fill_with_multi_color_warning(ip, diamonds_data):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    with pytest.warns(UserWarning):
        (
            ggplot(table=diamonds_data)
            + aes(x="price", cmap="plasma", fill="cut")
            + geom_histogram(bins=10, color="white", fill=["red", "blue"])
        )


@cleanup
@image_comparison(
    baseline_images=["histogram_stacked_large_bins"],
    extensions=["png"],
    remove_text=True,
)
def test_example_histogram_stacked_with_large_bins(ip, diamonds_data):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    (
        ggplot(table=diamonds_data)
        + aes(x="price", fill="cut")
        + geom_histogram(bins=400)
    )


@cleanup
@image_comparison(
    baseline_images=["histogram_categorical"],
    extensions=["png"],
    remove_text=True,
)
def test_categorical_histogram(ip, diamonds_data):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    (ggplot(table=diamonds_data) + aes(x=["cut"]) + geom_histogram())


@cleanup
@image_comparison(
    baseline_images=["histogram_categorical_combined"],
    extensions=["png"],
    remove_text=True,
)
def test_categorical_histogram_combined(ip, diamonds_data):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    (ggplot(table=diamonds_data) + aes(x=["color", "carat"]) + geom_histogram(bins=10))


@cleanup
@image_comparison(
    baseline_images=["histogram_numeric_categorical_combined"],
    extensions=["png"],
    remove_text=True,
)
def test_categorical_and_numeric_histogram_combined(ip, diamonds_data):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    (ggplot(table=diamonds_data) + aes(x=["color", "carat"]) + geom_histogram(bins=20))


@cleanup
@image_comparison(
    baseline_images=["histogram_numeric_categorical_combined_custom_fill"],
    extensions=["png"],
    remove_text=True,
)
def test_categorical_and_numeric_histogram_combined_custom_fill(ip, diamonds_data):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    (
        ggplot(table=diamonds_data)
        + aes(x=["color", "carat"])
        + geom_histogram(bins=20, fill="red")
    )


@cleanup
@image_comparison(
    baseline_images=["histogram_numeric_categorical_combined_custom_multi_fill"],
    extensions=["png"],
    remove_text=True,
)
def test_categorical_and_numeric_histogram_combined_custom_multi_fill(
    ip, diamonds_data
):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    (
        ggplot(table=diamonds_data)
        + aes(x=["color", "carat"])
        + geom_histogram(bins=20, fill=["red", "blue"])
    )


@cleanup
@image_comparison(
    baseline_images=["histogram_numeric_categorical_combined_custom_multi_color"],
    extensions=["png"],
    remove_text=True,
)
def test_categorical_and_numeric_histogram_combined_custom_multi_color(
    ip, diamonds_data
):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    (
        ggplot(table=diamonds_data)
        + aes(x=["color", "carat"])
        + geom_histogram(bins=20, color=["green", "magenta"])
    )


@pytest.mark.parametrize(
    "x, expected_error, expected_error_message",
    [
        ([], ValueError, "Column name has not been specified"),
        ([""], ValueError, "Column name has not been specified"),
        (None, ValueError, "Column name has not been specified"),
        ("", ValueError, "Column name has not been specified"),
        ([None, None], ValueError, "please ensure that you specify only one column"),
        (
            ["price", "table"],
            ValueError,
            "please ensure that you specify only one column",
        ),
        (
            ["price", "table", "color"],
            ValueError,
            "please ensure that you specify only one column",
        ),
        ([None], TypeError, "expected str instance, NoneType found"),
    ],
)
def test_example_histogram_stacked_input_error(
    ip, diamonds_data, x, expected_error, expected_error_message
):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    with pytest.raises(expected_error) as error:
        (ggplot(table=diamonds_data) + aes(x=x, fill="cut") + geom_histogram(bins=500))

    assert expected_error_message in str(error.value)


def test_histogram_no_bins_error(ip, diamonds_data):
    ip.run_cell(
        """
        %sql duckdb://
        """
    )

    with pytest.raises(ValueError) as error:
        (ggplot(table=diamonds_data) + aes(x=["price"]) + geom_histogram())

    assert "Please specify a valid number of bins." in str(error.value)
