import pandas as pd
from .load import load_raw
from .missing import standardize_missing, handle_missing
from .duplicates import (drop_exact_duplicates, keep_first_encounter,
                        drop_id_columns, drop_constant_columns)
from .fix_types import (convert_ranges, convert_numeric_text,
                       convert_code_columns, convert_text_to_category)

pd.set_option("display.width", 200)

# Known valid ranges (min, max). A value outside is impossible, not just unusual.
VALID_RANGES = {
    "age": (0, 120),
    "time_in_hospital": (1, 14),
}

# Values above this percentile get capped
CAP_PERCENTILE = 0.999


def numeric_columns(df):
    return df.select_dtypes(include="number").columns.tolist()


def outlier_report(df):
    """Summary of how spread out each numeric column is."""
    rows = []
    for col in numeric_columns(df):
        s = df[col]
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        flagged = ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).mean() * 100
        rows.append({
            "column": col,
            "min": s.min(),
            "median": s.median(),
            "p99": s.quantile(0.99),
            "p99.9": s.quantile(0.999),
            "max": s.max(),
            "iqr_flagged_%": round(flagged, 1),
        })
    return pd.DataFrame(rows).set_index("column")


def valid_range(col):
    """Return (min, max) limits for a column, or None if unknown."""
    if col in VALID_RANGES:
        return VALID_RANGES[col]
    if col.startswith("num"):      # num_... and number_... are counts
        return (0, None)
    return None


def drop_impossible_values(df):
    """Drop rows whose values break a known rule (e.g. a negative count)."""
    df = df.copy()
    log = []
    for col in numeric_columns(df):
        limits = valid_range(col)
        if limits is None:
            continue
        low, high = limits
        bad = pd.Series(False, index=df.index)
        if low is not None:
            bad |= df[col] < low
        if high is not None:
            bad |= df[col] > high
        n = int(bad.sum())
        if n:
            df = df[~bad]
            log.append(f"{col}: dropped {n} rows with impossible values")
    if not log:
        log.append("impossible values: none found")
    return df, log


def cap_extreme_values(df, percentile=CAP_PERCENTILE):
    """Pull extreme values down to the cap. Rows are kept."""
    df = df.copy()
    log = []
    for col in numeric_columns(df):
        cap = df[col].quantile(percentile)
        if df[col].dtype.kind == "i":
            cap = int(cap)
        n = int((df[col] > cap).sum())
        if n:
            df[col] = df[col].clip(upper=cap)
            log.append(f"{col}: capped {n} values above {cap:g}")
    if not log:
        log.append("extreme values: none capped")
    return df, log


if __name__ == "__main__":
    # Steps 4 to 6 first
    df = standardize_missing(load_raw())
    df, log = handle_missing(df)
    for step in (drop_exact_duplicates, keep_first_encounter,
                 drop_id_columns, drop_constant_columns,
                 convert_ranges, convert_numeric_text,
                 convert_code_columns, convert_text_to_category):
        df, new_log = step(df)
        log += new_log

    print("Shape before step 7:", df.shape)
    print("\n=== OUTLIER REPORT BEFORE ===")
    print(outlier_report(df))

    # Step 7
    step7_log = []
    for step in (drop_impossible_values, cap_extreme_values):
        df, new_log = step(df)
        step7_log += new_log

    print("\n=== ACTIONS TAKEN (step 7) ===")
    for line in step7_log:
        print("-", line)

    print("\n=== OUTLIER REPORT AFTER ===")
    print(outlier_report(df))
    print("\nShape after step 7:", df.shape)