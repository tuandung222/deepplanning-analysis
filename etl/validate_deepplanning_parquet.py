#!/usr/bin/env python3
"""Validate standardized DeepPlanning parquet tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import pyarrow.parquet as pq

REQUIRED_TABLES = [
    "shopping_queries.parquet",
    "shopping_cases.parquet",
    "shopping_gt_products.parquet",
    "shopping_catalog.parquet",
    "shopping_user_info.parquet",
    "travel_queries.parquet",
    "travel_constraints.parquet",
    "travel_db_trains.parquet",
    "travel_db_flights.parquet",
    "travel_db_hotels.parquet",
    "travel_db_restaurants.parquet",
    "travel_db_attractions.parquet",
    "travel_db_locations.parquet",
]


def row_count(path: Path) -> int:
    return pq.ParquetFile(path).metadata.num_rows


def load_col(path: Path, col: str) -> List[str]:
    t = pq.read_table(path, columns=[col])
    return [str(x) for x in t.column(0).to_pylist()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate DeepPlanning parquet artifacts")
    parser.add_argument("--parquet-dir", type=Path, default=Path("artifacts/deepplanning_parquet"))
    args = parser.parse_args()

    if not args.parquet_dir.exists():
        raise FileNotFoundError(args.parquet_dir)

    missing = [t for t in REQUIRED_TABLES if not (args.parquet_dir / t).exists()]
    if missing:
        raise RuntimeError(f"Missing required tables: {missing}")

    report: Dict = {"tables": {}, "checks": {}}
    for t in REQUIRED_TABLES:
        path = args.parquet_dir / t
        report["tables"][t] = {"rows": row_count(path)}

    shopping_case_ids = set(load_col(args.parquet_dir / "shopping_cases.parquet", "case_id"))
    shopping_query_ids = set(load_col(args.parquet_dir / "shopping_queries.parquet", "case_id"))

    travel_query_ids = set(
        f"{lang}:{sid}"
        for lang, sid in zip(
            load_col(args.parquet_dir / "travel_queries.parquet", "language"),
            load_col(args.parquet_dir / "travel_queries.parquet", "sample_id"),
        )
    )
    travel_constraint_ids = set(
        f"{lang}:{sid}"
        for lang, sid in zip(
            load_col(args.parquet_dir / "travel_constraints.parquet", "language"),
            load_col(args.parquet_dir / "travel_constraints.parquet", "sample_id"),
        )
    )

    report["checks"]["shopping_query_case_overlap"] = {
        "ok": shopping_case_ids.issubset(shopping_query_ids),
        "shopping_cases": len(shopping_case_ids),
        "shopping_queries": len(shopping_query_ids),
        "missing_case_ids": sorted(list(shopping_case_ids - shopping_query_ids))[:20],
    }
    report["checks"]["travel_query_constraint_overlap"] = {
        "ok": travel_constraint_ids.issubset(travel_query_ids),
        "travel_constraints": len(travel_constraint_ids),
        "travel_queries": len(travel_query_ids),
        "missing_ids": sorted(list(travel_constraint_ids - travel_query_ids))[:20],
    }

    manifest_path = args.parquet_dir / "manifest.json"
    if manifest_path.exists():
        report["manifest"] = json.loads(manifest_path.read_text(encoding="utf-8"))

    out = args.parquet_dir / "validation_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "ok", "report": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
