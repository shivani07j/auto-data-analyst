import pandas as pd
from load import load_raw
from missing import standardize_missing, handle_missing
from duplicates import (drop_exact_duplicates, keep_first_encounter,
                        drop_id_columns, drop_constant_columns)
from fix_types import (convert_ranges, convert_numeric_text,
                       convert_code_columns, convert_text_to_category)
from outliers import drop_impossible_values, cap_extreme_values

# Several different codes that all mean "unknown" (see IDS_mapping.csv)
UNKNOWN_CODES = {
    "admission_type_id": ["5", "6", "8"],
    "discharge_disposition_id": ["18", "25", "26"],
    "admission_source_id": ["9", "15", "17", "20", "21"],
}

DIAG_COLS = ["diag_1", "diag_2", "diag_3"]

# Labels below this share of rows are merged, but only in columns
# that have more than MAX_LEVELS different labels
RARE_SHARE = 0.01
MAX_LEVELS = 10

# Labels we created on purpose, never merge these as "rare"
PROTECTED = {"Unknown", "Not tested"}
KEEP_RARE_COLS = ["discharge_disposition_id"]

def category_columns(df):
    return df.select_dtypes(include="category").columns.tolist()


def fix_text_variants(df):
    """Merge labels that differ only by capital letters (e.g. 'yes' and 'Yes')."""
    df = df.copy()
    log = []
    for col in category_columns(df):
        s = df[col].astype(str)
        groups = {}
        for label in s.value_counts().index:      # most frequent first
            groups.setdefault(label.strip().lower(), []).append(label)
        mapping = {}
        for labels in groups.values():
            for other in labels[1:]:
                mapping[other] = labels[0]
        if mapping:
            df[col] = s.replace(mapping).astype("category")
            log.append(f"{col}: merged {len(mapping)} spelling variants")
    if not log:
        log.append("spelling variants: none found")
    return df, log


def merge_unknown_codes(df):
    """Merge the different codes that all mean 'unknown' into one label."""
    df = df.copy()
    log = []
    for col, codes in UNKNOWN_CODES.items():
        if col in df.columns:
            s = df[col].astype(str)
            n = int(s.isin(codes).sum())
            df[col] = s.where(~s.isin(codes), "Unknown").astype("category")
            log.append(f"{col}: {n} rows with codes {', '.join(codes)} -> 'Unknown'")
    return df, log


def icd9_group(code):
    """Map a detailed diagnosis code to a broad disease group."""
    if code == "Unknown":
        return "Unknown"
    if code.startswith(("V", "E")):
        return "Other"
    try:
        n = float(code)
    except ValueError:
        return "Other"
    if 250 <= n < 251:
        return "Diabetes"
    if 390 <= n <= 459 or n == 785:
        return "Circulatory"
    if 460 <= n <= 519 or n == 786:
        return "Respiratory"
    if 520 <= n <= 579 or n == 787:
        return "Digestive"
    if 580 <= n <= 629 or n == 788:
        return "Genitourinary"
    if 140 <= n <= 239:
        return "Neoplasms"
    if 710 <= n <= 739:
        return "Musculoskeletal"
    if 800 <= n <= 999:
        return "Injury"
    return "Other"


def group_diagnoses(df):
    """Replace detailed diagnosis codes with broad groups."""
    df = df.copy()
    log = []
    for col in DIAG_COLS:
        if col in df.columns:
            before = df[col].nunique()
            s = df[col].astype(str)
            mapping = {c: icd9_group(c) for c in s.unique()}
            df[col] = s.map(mapping).astype("category")
            log.append(f"{col}: {before} codes -> {df[col].nunique()} groups")
    return df, log


def merge_rare_categories(df, share=RARE_SHARE, max_levels=MAX_LEVELS):
    """In columns with many labels, merge very rare ones into 'Other_rare'."""
    df = df.copy()
    log = []
    for col in category_columns(df):
        if col in KEEP_RARE_COLS or df[col].nunique() <= max_levels:
            continue
        s = df[col].astype(str)
        freq = s.value_counts(normalize=True)
        rare = [v for v, f in freq.items() if f < share and v not in PROTECTED]
        if len(rare) > 1:    # merging a single label would change nothing
            df[col] = s.where(~s.isin(rare), "Other_rare").astype("category")
            log.append(f"{col}: {len(rare)} rare labels (under {share:.0%} each) -> 'Other_rare'")
    if not log:
        log.append("rare labels: none merged")
    return df, log


if __name__ == "__main__":
    # Steps 4 to 7 first
    df = standardize_missing(load_raw())
    df, log = handle_missing(df)
    for step in (drop_exact_duplicates, keep_first_encounter,
                 drop_id_columns, drop_constant_columns,
                 convert_ranges, convert_numeric_text,
                 convert_code_columns, convert_text_to_category,
                 drop_impossible_values, cap_extreme_values):
        df, new_log = step(df)
        log += new_log

    print("Shape before step 8:", df.shape)
    print("\n=== LABELS PER COLUMN BEFORE (top 8) ===")
    print(df.select_dtypes("category").nunique().sort_values(ascending=False).head(8))

    # Step 8
    step8_log = []
    for step in (fix_text_variants, merge_unknown_codes,
                 group_diagnoses, merge_rare_categories):
        df, new_log = step(df)
        step8_log += new_log

    print("\n=== ACTIONS TAKEN (step 8) ===")
    for line in step8_log:
        print("-", line)

    print("\n=== LABELS PER COLUMN AFTER (top 8) ===")
    print(df.select_dtypes("category").nunique().sort_values(ascending=False).head(8))
    print("\nShape after step 8:", df.shape)