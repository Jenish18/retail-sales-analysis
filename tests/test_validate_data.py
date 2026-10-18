
import pandas as pd
import pytest

from validate_data import REQUIRED_COLUMNS, validate_data


@pytest.fixture
def valid_csv(tmp_path):
    """Create a small, valid dataset for testing."""

    df = pd.DataFrame({
        column: [
            {
                "Order ID": "ORD001",
                "Customer Name": "Arun",
                "Category": "Snacks",
                "Sub Category": "Chocolates",
                "City": "Chennai",
                "Order Date": "2018-01-01",
                "Region": "South",
                "Sales": 1000.0,
                "Discount": 0.10,
                "Profit": 200.0,
                "State": "Tamil Nadu",
            }[column]
            for _ in range(2)
        ]
        for column in REQUIRED_COLUMNS
    })

    # Make Order IDs unique for a valid dataset.
    df["Order ID"] = ["ORD001", "ORD002"]

    path = tmp_path / "valid.csv"
    df.to_csv(path, index=False)
    return path


def test_valid_dataset_passes(valid_csv):
    df = validate_data(valid_csv)

    assert len(df) == 2
    assert len(df.columns) == 11
    assert df["Sales"].sum() == 2000


def test_duplicate_order_ids_are_rejected(valid_csv):
    df = pd.read_csv(valid_csv)
    df.loc[1, "Order ID"] = df.loc[0, "Order ID"]
    df.to_csv(valid_csv, index=False)

    with pytest.raises(ValueError, match="duplicate Order IDs"):
        validate_data(valid_csv)


def test_invalid_dates_are_rejected(valid_csv):
    df = pd.read_csv(valid_csv)
    df.loc[0, "Order Date"] = "not-a-date"
    df.to_csv(valid_csv, index=False)

    with pytest.raises(ValueError, match="invalid order dates"):
        validate_data(valid_csv)


def test_negative_sales_are_rejected(valid_csv):
    df = pd.read_csv(valid_csv)
    df.loc[0, "Sales"] = -100
    df.to_csv(valid_csv, index=False)

    with pytest.raises(ValueError, match="zero or negative"):
        validate_data(valid_csv)


def test_invalid_discount_is_rejected(valid_csv):
    df = pd.read_csv(valid_csv)
    df.loc[0, "Discount"] = 1.5
    df.to_csv(valid_csv, index=False)

    with pytest.raises(ValueError, match="Discount must be between"):
        validate_data(valid_csv)
