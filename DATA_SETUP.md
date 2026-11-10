# Data setup and reproducibility

This project uses the **dunnhumby Complete Journey** dataset. Source or sampled transactions are not included in the public portfolio package. Use a locally obtained, authorized copy with `transaction_data.csv` and `product.csv`.

## Generate the five local input CSVs

From the repository root, run:

```powershell
py -3.11 prepare_data.py "C:\path\to\datasets.zip"
```

The script reconstructs the complete-basket sample and writes:

```text
data/transactions_sample_part1a.csv
data/transactions_sample_part1b.csv
data/transactions_sample_part2.csv
data/product.csv
data/date_dimension.csv
```

Sampling uses `random.Random(74010).sample(...)` over basket IDs in source-file encounter order. An unchanged source ZIP and Python implementation give the same output.

### Reconstructed source counts (verified)

| Dataset/step | Count |
| --- | ---: |
| Source transaction rows | 2,595,732 |
| Source distinct baskets | 276,484 |
| Sampled complete baskets | 20,000 |
| Sample transaction rows | 186,862 |
| Products | 92,353 |
| Date dimension day/week pairs | 706 |

The **original course report** listed 190,161 sampled transaction rows and 708 date rows, but its exact sampling script is unavailable. Do not claim that these samples are identical.

## Run notebooks

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyter lab
```

Run `notebooks/01_data_preparation.ipynb` followed by `notebooks/02_data_mining_models.ipynb`. The first creates `data/complete_journey.sqlite`, including analysis tables required by the second. Both were executed successfully by the user on November 10, 2026 with the reconstructed sample; the repository notebooks have cleared outputs, while the README reports the results observed in that completed run.

## Publishing safely

- The `.gitignore` excludes all `data/` files except `data/.gitkeep`, as well as SQLite databases, caches, and virtual environments.
- Figures are derived from notebook execution. Attribute shared coursework to the group and confirm permission before public distribution.
- Do not publish raw/sampled transaction data, the generated SQLite file, or private course materials without authorization.
