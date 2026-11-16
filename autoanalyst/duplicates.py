import pandas as pd
from .load import load_raw
from .missing import standardize_missing, handle_missing

# Column that identifies a patient (set to None if your data has no such column)
PATIENT_COL = "patient_nbr"


def drop_exact_duplicates(df):
    """Remove rows that are identical in every column."""
    n = int(df.duplicated().sum())
    df = df.drop_duplicates()
    return df, [f"exact duplicates: dropped {n} rows"]


def keep_first_encounter(df, patient_col=PATIENT_COL):
    """Keep one row per patient, so the same person is not counted many times."""
    before = len(df)
    n_patients = df[patient_col].nunique()
    df = df.drop_duplicates(subset=patient_col, keep="first")
    return df, [
        f"repeat patients: {n_patients} unique patients, "
        f"kept first row of each, dropped {before - len(df)} rows"
    ]


def find_id_columns(df):
    """A column whose values are all different is an identifier, not a feature."""
    ids = []
    for col in df.columns:
        if df[col].dtype.kind in "iO" and df[col].nunique() == len(df):
            ids.append(col)
    return ids


def drop_id_columns(df):
    ids = find_id_columns(df)
    df = df.drop(columns=ids)
    return df, [f"{c}: dropped identifier column" for c in ids]


def drop_constant_columns(df):
    """A column with a single value carries no information."""
    const = [c for c in df.columns if df[c].nunique() <= 1]
    df = df.drop(columns=const)
    return df, [f"{c}: dropped constant column" for c in const]


if __name__ == "__main__":
    # Steps 3 and 4 first, so the data arrives already handled for missing values
    df = standardize_missing(load_raw())
    df, log = handle_missing(df)
    print("Shape before step 5:", df.shape)

    # Step 5
    for step in (drop_exact_duplicates, keep_first_encounter,
                 drop_id_columns, drop_constant_columns):
        df, new_log = step(df)
        log += new_log

    print("\n=== ACTIONS TAKEN (steps 4 and 5) ===")
    for line in log:
        print("-", line)

    print("\nShape after step 5:", df.shape)