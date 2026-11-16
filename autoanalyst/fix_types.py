import re
import pandas as pd
from .load import load_raw
from .missing import standardize_missing, handle_missing
from .duplicates import (drop_exact_duplicates, keep_first_encounter,
                        drop_id_columns, drop_constant_columns)

RANGE_PATTERN = re.compile(r"^\[(\d+)-(\d+)\)$")


def memory_mb(df):
    return round(df.memory_usage(deep=True).sum() / 1e6, 1)


def convert_ranges(df):
    """Turn range text like '[70-80)' into its middle number (75)."""
    df = df.copy()
    log = []
    for col in df.select_dtypes(include="object").columns:
        values = df[col].dropna().astype(str)
        if len(values) and values.str.match(RANGE_PATTERN).all():
            mapping = {}
            for v in values.unique():
                low, high = RANGE_PATTERN.match(v).groups()
                mapping[v] = (int(low) + int(high)) // 2
            df[col] = df[col].map(mapping)
            log.append(f"{col}: range text -> midpoint number")
    return df, log


def convert_numeric_text(df):
    """Text columns that only contain numbers become real numbers."""
    df = df.copy()
    log = []
    for col in df.select_dtypes(include="object").columns:
        try:
            df[col] = pd.to_numeric(df[col])
            log.append(f"{col}: text -> number")
        except (ValueError, TypeError):
            pass
    return df, log


def convert_code_columns(df):
    """Numbers that are really labels (names ending in '_id') become categories."""
    df = df.copy()
    log = []
    for col in df.columns:
        if col.endswith("_id") and df[col].dtype.kind in "iu":
            df[col] = df[col].astype(str).astype("category")
            log.append(f"{col}: number codes -> category")
    return df, log


def convert_text_to_category(df):
    """Remaining text columns become the category type."""
    df = df.copy()
    cols = df.select_dtypes(include="object").columns.tolist()
    for col in cols:
        df[col] = df[col].astype("category")
    return df, [f"{len(cols)} text columns -> category"]


if __name__ == "__main__":
    # Steps 4 and 5 first
    df = standardize_missing(load_raw())
    df, log = handle_missing(df)
    for step in (drop_exact_duplicates, keep_first_encounter,
                 drop_id_columns, drop_constant_columns):
        df, new_log = step(df)
        log += new_log

    print("Shape before step 6:", df.shape)
    print("Memory before (MB):", memory_mb(df))

    # Step 6
    step6_log = []
    for step in (convert_ranges, convert_numeric_text,
                 convert_code_columns, convert_text_to_category):
        df, new_log = step(df)
        step6_log += new_log

    print("\n=== ACTIONS TAKEN (step 6) ===")
    for line in step6_log:
        print("-", line)

    print("\nShape after step 6:", df.shape)
    print("Memory after (MB):", memory_mb(df))
    print("\n=== COLUMN TYPES AFTER ===")
    print(df.dtypes.value_counts())
    print("\n=== AGE VALUES ===")
    print(sorted(df["age"].unique()))