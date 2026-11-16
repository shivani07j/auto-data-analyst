import pandas as pd
from .load import load_raw

pd.set_option("display.max_rows", None)

# Text values that really mean "missing"
MISSING_TOKENS = ["?", "Unknown/Invalid", ""]

# Blank here means "test not done", not an error
NOT_TESTED_COLS = ["max_glu_serum", "A1Cresult"]

# Essential fields: a row without them is not useful
ROW_DROP_COLS = ["gender", "diag_1"]

# Drop a column if more than this share of it is missing
DROP_COLUMN_THRESHOLD = 0.60


def standardize_missing(df):
    """Turn hidden missing values (like '?') into real NaN."""
    df = df.copy()
    for col in df.select_dtypes(include="object").columns:
        cleaned = df[col].str.strip()
        df[col] = cleaned.mask(cleaned.isin(MISSING_TOKENS))
    return df


def missing_report(df):
    """Count and percentage of missing values, only for affected columns."""
    counts = df.isnull().sum()
    report = pd.DataFrame({
        "missing": counts,
        "percent": (counts / len(df) * 100).round(1),
    })
    return report[report["missing"] > 0].sort_values("percent", ascending=False)


def handle_missing(df):
    """Apply a rule to each missing-value case. Returns (df, log)."""
    df = df.copy()
    log = []

    # Rule 1: blank means "not tested"
    for col in NOT_TESTED_COLS:
        n = int(df[col].isnull().sum())
        df[col] = df[col].fillna("Not tested")
        log.append(f"{col}: {n} blanks -> 'Not tested'")

    # Rule 2: drop columns that are mostly empty
    share = df.isnull().mean()
    too_empty = share[share > DROP_COLUMN_THRESHOLD].index.tolist()
    df = df.drop(columns=too_empty)
    for col in too_empty:
        log.append(f"{col}: dropped column ({share[col] * 100:.1f}% missing)")

    # Rule 3: drop rows missing an essential field
    for col in ROW_DROP_COLS:
        if col in df.columns:
            n = int(df[col].isnull().sum())
            df = df.dropna(subset=[col])
            log.append(f"{col}: dropped {n} rows with missing value")

    # Rule 4: everything left is a text column, so label it "Unknown"
    for col in df.columns[df.isnull().any()]:
        n = int(df[col].isnull().sum())
        df[col] = df[col].fillna("Unknown")
        log.append(f"{col}: {n} missing -> 'Unknown'")

    return df, log


if __name__ == "__main__":
    df = standardize_missing(load_raw())

    print("=== MISSING BEFORE ===")
    print(missing_report(df))

    df, log = handle_missing(df)

    print("\n=== ACTIONS TAKEN ===")
    for line in log:
        print("-", line)

    print("\n=== MISSING AFTER ===")
    print(missing_report(df))
    print("\nShape after:", df.shape)