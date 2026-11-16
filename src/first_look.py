import pandas as pd
from load import load_raw

pd.set_option("display.max_rows", None)
pd.set_option("display.width", 200)


def first_look(df):
    """Print a basic overview of a dataframe."""
    print("\n=== SHAPE ===")
    print(df.shape)

    print("\n=== MEMORY (MB) ===")
    print(round(df.memory_usage(deep=True).sum() / 1e6, 1))

    print("\n=== COLUMN TYPES ===")
    print(df.dtypes)

    print("\n=== NULL COUNT PER COLUMN (real NaN only) ===")
    print(df.isnull().sum())

    print("\n=== UNIQUE VALUES PER COLUMN ===")
    print(df.nunique().sort_values())

    print("\n=== NUMERIC SUMMARY ===")
    print(df.describe().T)

    print("\n=== CATEGORICAL SUMMARY ===")
    print(df.describe(include="object").T)


if __name__ == "__main__":
    first_look(load_raw())