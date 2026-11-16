# Auto Data Analyst

An automated data analysis tool, built in phases. Phase 1 is a manual cleaning of a messy health dataset. It becomes the blueprint for a tool that cleans, analyses and models any tabular CSV file.

## Data

Diabetes 130-US Hospitals (1999-2008), from the UCI Machine Learning Repository. Download it and place `diabetic_data.csv` and `IDS_mapping.csv` in `data/raw/`. The data files are not stored in this repo.

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/pipeline.py
```

This writes the clean data to `data/clean/` and the cleaning log to `reports/cleaning_log.md`.

## Progress

### Phase 1: Manual data cleaning (complete)
- [x] Step 1: Project structure
- [x] Step 2: Download and load raw data
- [x] Step 3: First look at the data
- [x] Step 4: Missing values
- [x] Step 5: Duplicates and ID columns
- [x] Step 6: Data types
- [x] Step 7: Outliers and impossible values
- [x] Step 8: Inconsistent categories
- [x] Step 9: Pipeline, clean data and cleaning log

Result: 101,766 rows and 50 columns cleaned down to 71,506 rows and 44 columns, with every change recorded in [reports/cleaning_log.md](reports/cleaning_log.md).

### Phase 2: Turn the pipeline into a tool for any CSV (next)
- [ ] Step 1: Package structure and command-line entry point
- [ ] Step 2: Automatic column type detection
- [ ] Step 3: Settings file for dataset-specific rules
- [ ] Step 4: Generic cleaning engine with a cleaning log
- [ ] Step 5: Automatic profiling (distributions, correlations, imbalance, plots)
- [ ] Step 6: Target and task detection (classification or regression, leakage checks)
- [ ] Step 7: Preprocessing inside a modelling pipeline (no test-data leakage)
- [ ] Step 8: Model comparison with cross-validation
- [ ] Step 9: Explainability (feature importance and a plain-language summary)
- [ ] Step 10: Combined report, tests and usage docs

### Phase 3: Prove it works on unseen data
- [ ] Run the tool on 3 or 4 new datasets, including a medical one
- [ ] Log what broke and fix it
- [ ] Results table and final release

## Decisions and limitations

- Hidden missing values ("?") were turned into real blanks. A blank in the glucose and A1C test columns means the test was not done, so it became "Not tested" instead of being imputed.
- Only the first row of each patient was kept, to avoid the same person appearing many times. The dataset has no date column, so "first" means first in the file, not necessarily the earliest visit.
- Extreme values in the count columns were capped at the 99.9th percentile instead of removing the rows.
- The 700+ diagnosis codes were grouped into broad disease groups, which loses detail.
- Rare labels (under 1% of rows) were merged into "Other_rare", except in the discharge column, where rare codes such as death and hospice must stay separate.
- Capping limits were calculated on the full dataset. Phase 2 fixes this by learning them from training data only.