
import logging
from pathlib import Path

import pandas as pd


# 1. Configuration
CSV_PATH = Path("data/processed/supermart_clean.csv")

REQUIRED_COLUMNS = [
    "Order ID",
    "Customer Name",
    "Category",
    "Sub Category",
    "City",
    "Order Date",
    "Region",
    "Sales",
    "Discount",
    "Profit",
    "State",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def validate_data(csv_path: Path) -> pd.DataFrame:
    """Validate the cleaned supermarket dataset before loading."""

    # Check whether the source file exists.
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Read the cleaned dataset.
    df = pd.read_csv(csv_path)

    logger.info("Loaded source file: %s", csv_path)
    logger.info("Rows: %s | Columns: %s", *df.shape)

    # Check the expected schema.
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    unexpected_columns = set(df.columns) - set(REQUIRED_COLUMNS)

    if missing_columns or unexpected_columns:
        raise ValueError(
            f"Schema mismatch. Missing: {sorted(missing_columns)}; "
            f"Unexpected: {sorted(unexpected_columns)}"
        )

    # Check critical fields.
    critical_columns = [
        "Order ID",
        "Order Date",
        "Sales",
        "Profit",
    ]

    null_counts = df[critical_columns].isnull().sum()
    if null_counts.any():
        raise ValueError(
            f"Null values in critical columns:\n{null_counts}"
        )

    # Every order ID must be unique for this dataset.
    duplicate_count = int(df["Order ID"].duplicated().sum())
    if duplicate_count:
        raise ValueError(
            f"Found {duplicate_count} duplicate Order IDs."
        )

    parsed_dates = pd.to_datetime(
    df["Order Date"],
    format="%Y-%m-%d",
    errors="coerce",
)

    invalid_dates = int(parsed_dates.isnull().sum())
    if invalid_dates:
        raise ValueError(f"Found {invalid_dates} invalid order dates.")

    # Validate numeric values.
    for column in ["Sales", "Profit", "Discount"]:
        df[column] = pd.to_numeric(df[column], errors="raise")

    if (df["Sales"] <= 0).any():
        raise ValueError("Sales contains zero or negative values.")

    if not df["Discount"].between(0, 1).all():
        raise ValueError("Discount must be between 0 and 1.")

    logger.info("Duplicate Order IDs: %s", duplicate_count)
    logger.info("Invalid dates: %s", invalid_dates)
    logger.info("Data-quality validation PASSED.")

    return df


if __name__ == "__main__":
    validated_df = validate_data(CSV_PATH)

    print("\nValidation summary")
    print("------------------")
    print("Rows validated:", len(validated_df))
    print("Columns:", len(validated_df.columns))
    print("Total sales:", round(validated_df["Sales"].sum(), 2))
    print("Total profit:", round(validated_df["Profit"].sum(), 2))
    print("Date range:",
          validated_df["Order Date"].min(),
          "to",
          validated_df["Order Date"].max())
