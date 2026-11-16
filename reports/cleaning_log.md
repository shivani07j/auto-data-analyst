# Cleaning log

- Raw data: 101766 rows, 50 columns
- Clean data: 71506 rows, 44 columns

## Missing values
Shape after this stage: 101742 rows, 49 columns

- 192852 hidden missing cells (like '?') turned into blanks
- max_glu_serum: 96420 blanks -> 'Not tested'
- A1Cresult: 84748 blanks -> 'Not tested'
- weight: dropped column (96.9% missing)
- gender: dropped 3 rows with missing value
- diag_1: dropped 21 rows with missing value
- race: 2269 missing -> 'Unknown'
- payer_code: 40244 missing -> 'Unknown'
- medical_specialty: 49939 missing -> 'Unknown'
- diag_2: 357 missing -> 'Unknown'
- diag_3: 1422 missing -> 'Unknown'

## Duplicates and ID columns
Shape after this stage: 71506 rows, 44 columns

- exact duplicates: dropped 0 rows
- repeat patients: 71506 unique patients, kept first row of each, dropped 30236 rows
- encounter_id: dropped identifier column
- patient_nbr: dropped identifier column
- examide: dropped constant column
- citoglipton: dropped constant column
- glimepiride-pioglitazone: dropped constant column

## Data types
Shape after this stage: 71506 rows, 44 columns

- age: range text -> midpoint number
- admission_type_id: number codes -> category
- discharge_disposition_id: number codes -> category
- admission_source_id: number codes -> category
- 32 text columns -> category

## Outliers and impossible values
Shape after this stage: 71506 rows, 44 columns

- impossible values: none found
- num_lab_procedures: capped 69 values above 98
- num_medications: capped 68 values above 61
- number_outpatient: capped 69 values above 12
- number_emergency: capped 60 values above 5
- number_inpatient: capped 49 values above 6
- number_diagnoses: capped 66 values above 10

## Inconsistent categories
Shape after this stage: 71506 rows, 44 columns

- spelling variants: none found
- admission_type_id: 8052 rows with codes 5, 6, 8 -> 'Unknown'
- discharge_disposition_id: 3251 rows with codes 18, 25, 26 -> 'Unknown'
- admission_source_id: 5199 rows with codes 9, 15, 17, 20, 21 -> 'Unknown'
- diag_1: 696 codes -> 9 groups
- diag_2: 726 codes -> 10 groups
- diag_3: 759 codes -> 10 groups
- admission_source_id: 9 rare labels (under 1% each) -> 'Other_rare'
- payer_code: 9 rare labels (under 1% each) -> 'Other_rare'
- medical_specialty: 61 rare labels (under 1% each) -> 'Other_rare'

## Final columns

| Column | Type | Unique values |
|---|---|---|
| race | category | 6 |
| gender | category | 2 |
| age | int64 | 10 |
| admission_type_id | category | 6 |
| discharge_disposition_id | category | 25 |
| admission_source_id | category | 7 |
| time_in_hospital | int64 | 14 |
| payer_code | category | 10 |
| medical_specialty | category | 11 |
| num_lab_procedures | int64 | 98 |
| num_procedures | int64 | 7 |
| num_medications | int64 | 61 |
| number_outpatient | int64 | 13 |
| number_emergency | int64 | 6 |
| number_inpatient | int64 | 7 |
| diag_1 | category | 9 |
| diag_2 | category | 10 |
| diag_3 | category | 10 |
| number_diagnoses | int64 | 10 |
| max_glu_serum | category | 4 |
| A1Cresult | category | 4 |
| metformin | category | 4 |
| repaglinide | category | 4 |
| nateglinide | category | 4 |
| chlorpropamide | category | 4 |
| glimepiride | category | 4 |
| acetohexamide | category | 2 |
| glipizide | category | 4 |
| glyburide | category | 4 |
| tolbutamide | category | 2 |
| pioglitazone | category | 4 |
| rosiglitazone | category | 4 |
| acarbose | category | 3 |
| miglitol | category | 4 |
| troglitazone | category | 2 |
| tolazamide | category | 2 |
| insulin | category | 4 |
| glyburide-metformin | category | 4 |
| glipizide-metformin | category | 2 |
| metformin-rosiglitazone | category | 2 |
| metformin-pioglitazone | category | 2 |
| change | category | 2 |
| diabetesMed | category | 2 |
| readmitted | category | 3 |
