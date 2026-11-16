import pandas as pd

RAW_PATH = "data/raw/diabetic_data.csv"

def load_raw(path=RAW_PATH):
    """Load the raw CSV exactly as it is, with no cleaning."""
    return pd.read_csv(path, low_memory=False)

if __name__ == "__main__":
    df = load_raw()
    print(df.shape)
    print(df.head())