import os
import pandas as pd
from load import load_raw
from missing import standardize_missing, handle_missing
from duplicates import (drop_exact_duplicates, keep_first_encounter,
                        drop_id_columns, drop_constant_columns)
from fix_types import (convert_ranges, convert_numeric_text,
                       convert_code_columns, convert_text_to_category)
from outliers import drop_impossible_values, cap_extreme_values
from categories import (fix_text_variants, merge_unknown_codes,
                        group_diagnoses, merge_rare_categories)

CLEAN_CSV = "data/clean/diabetic_data_clean.csv"
CLEAN_PARQUET = "data/clean/diabetic_data_clean.parquet"
LOG_PATH = "reports/cleaning_log.md"


def standardize_step(df):
    """Turn hidden missing values (like '?') into real blanks, and count them."""
    before = int(df.isnull().sum().sum())
    df = standardize_missing(df)
    n = int(df.isnull().sum().sum()) - before
    return df, [f"{n} hidden missing cells (like '?') turned into blanks"]


# Each stage is a name plus the cleaning functions it runs, in order
STAGES = [
    ("Missing values", [standardize_step, handle_missing]),
    ("Duplicates and ID columns", [drop_exact_duplicates, keep_first_encounter,
                                   drop_id_columns, drop_constant_columns]),
    ("Data types", [convert_ranges, convert_numeric_text,
                    convert_code_columns, convert_text_to_category]),
    ("Outliers and impossible values", [drop_impossible_values, cap_extreme_values]),
    ("Inconsistent categories", [fix_text_variants, merge_unknown_codes,
                                 group_diagnoses, merge_rare_categories]),
]


def run_pipeline(raw):
    """Run every cleaning step. Returns the clean data and a log of what happened."""
    df = raw
    log = []
    for name, steps in STAGES:
        lines = []
        for step in steps:
            df, new_lines = step(df)
            lines += new_lines
        log.append((name, df.shape, lines))
    return df, log


def save_clean(df):
    """Save the clean data as CSV, and as parquet too if it is available."""
    os.makedirs("data/clean", exist_ok=True)
    df.to_csv(CLEAN_CSV, index=False)
    saved = [CLEAN_CSV]
    try:
        df.to_parquet(CLEAN_PARQUET, index=False)
        saved.append(CLEAN_PARQUET)
    except ImportError:
        print("Parquet skipped (pip install pyarrow to also keep column types)")
    return saved


def write_log(raw, clean, log, path=LOG_PATH):
    """Write everything that happened to the data into a readable report."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out = [
        "# Cleaning log", "",
        f"- Raw data: {raw.shape[0]} rows, {raw.shape[1]} columns",
        f"- Clean data: {clean.shape[0]} rows, {clean.shape[1]} columns", "",
    ]
    for name, shape, lines in log:
        out.append(f"## {name}")
        out.append(f"Shape after this stage: {shape[0]} rows, {shape[1]} columns")
        out.append("")
        out += [f"- {line}" for line in lines]
        out.append("")
    out += ["## Final columns", "",
            "| Column | Type | Unique values |", "|---|---|---|"]
    for col in clean.columns:
        out.append(f"| {col} | {clean[col].dtype} | {clean[col].nunique()} |")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    raw = load_raw()
    clean, log = run_pipeline(raw)
    saved = save_clean(clean)
    write_log(raw, clean, log)

    print("Raw shape:  ", raw.shape)
    print("Clean shape:", clean.shape)
    print("Saved:", ", ".join(saved))
    print("Log written to", LOG_PATH)

    # Check that the saved CSV loads back correctly
    check = pd.read_csv(CLEAN_CSV)
    print("Reloaded CSV shape:", check.shape)
    print("Missing values left:", int(check.isnull().sum().sum()))