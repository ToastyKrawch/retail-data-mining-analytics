"""Create reproducible 20,000-basket inputs from a locally supplied dunnhumby ZIP.

This is a new deterministic sampler, not a recovery of the original coursework sample.
The ZIP must contain transaction_data.csv and product.csv.
No source data is uploaded or downloaded by this script.
"""

from __future__ import annotations

import argparse
import csv
import io
import random
import shutil
import zipfile
from collections import Counter
from pathlib import Path


BASKET_COUNT = 20_000
SEED = 74010


def rows_from_zip(archive: zipfile.ZipFile, member: str):
    with archive.open(member) as stream:
        wrapper = io.TextIOWrapper(stream, encoding="utf-8-sig", newline="")
        yield from csv.DictReader(wrapper)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_zip", type=Path, help="ZIP containing product.csv and transaction_data.csv")
    parser.add_argument("--output", type=Path, default=Path("data"), help="Output data directory")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(args.source_zip) as z:
        members = set(z.namelist())
        needed = {"product.csv", "transaction_data.csv"}
        if not needed <= members:
            raise SystemExit(f"Missing required ZIP members: {sorted(needed - members)}")

        # Reading in source order makes the basket sampling order deterministic.
        counts = Counter()
        for record in rows_from_zip(z, "transaction_data.csv"):
            counts[record["BASKET_ID"]] += 1
        if len(counts) < BASKET_COUNT:
            raise SystemExit(f"Only {len(counts)} distinct baskets in source data")
        chosen = set(random.Random(SEED).sample(list(counts), BASKET_COUNT))

        names = ["transactions_sample_part1a.csv", "transactions_sample_part1b.csv", "transactions_sample_part2.csv"]
        paths = [args.output / name for name in names]
        handles = [p.open("w", encoding="utf-8", newline="") for p in paths]
        try:
            writers = None
            day_week_pairs = set()
            written = 0
            with z.open("transaction_data.csv") as stream:
                rows = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
                writers = [csv.DictWriter(h, fieldnames=rows.fieldnames) for h in handles]
                for writer in writers:
                    writer.writeheader()
                for row in rows:
                    if row["BASKET_ID"] in chosen:
                        writers[min(written // 65_000, 2)].writerow(row)
                        day_week_pairs.add((int(row["DAY"]), int(row["WEEK_NO"])))
                        written += 1
        finally:
            for handle in handles:
                handle.close()
        with (args.output / "date_dimension.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["DAY", "WEEK_NO"])
            writer.writerows(sorted(day_week_pairs))
        with z.open("product.csv") as source, (args.output / "product.csv").open("wb") as dest:
            shutil.copyfileobj(source, dest)

    print(f"Source baskets: {len(counts):,}")
    print(f"Selected baskets: {len(chosen):,} (seed {SEED})")
    print(f"Selected transaction lines: {written:,}")
    print(f"Distinct selected day/week pairs: {len(day_week_pairs):,}")
    print("NOTE: Original coursework reported 190,161 lines. This is a newly reproducible sample, not the same one.")
    print(f"Files written to: {args.output.resolve()}")


if __name__ == "__main__":
    main()
