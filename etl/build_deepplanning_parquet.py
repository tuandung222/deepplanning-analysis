#!/usr/bin/env python3
"""Build standardized DeepPlanning parquet tables from raw archives + Qwen-Agent query files."""

from __future__ import annotations

import argparse
import csv
import json
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import snapshot_download

HF_DATASET_ID = "Qwen/DeepPlanning"
RAW_FILES = [
    "database_en.zip",
    "database_zh.zip",
    "database_level1.tar.gz",
    "database_level2.tar.gz",
    "database_level3.tar.gz",
]


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_parquet(rows: List[Dict], out_path: Path) -> int:
    _ensure_dir(out_path.parent)
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, out_path, compression="zstd")
    return table.num_rows


def _extract_tar(tar_path: Path, out_dir: Path) -> Path:
    _ensure_dir(out_dir)
    with tarfile.open(tar_path, "r:gz") as tf:
        tf.extractall(out_dir)
    roots = [p for p in out_dir.iterdir() if p.is_dir() and p.name.startswith("database_level")]
    if len(roots) != 1:
        raise RuntimeError(f"Unexpected tar extraction roots under {out_dir}: {roots}")
    return roots[0]


def _extract_zip(zip_path: Path, out_dir: Path) -> Path:
    _ensure_dir(out_dir)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)
    roots = [p for p in out_dir.iterdir() if p.is_dir() and p.name.startswith("database_")]
    if len(roots) != 1:
        raise RuntimeError(f"Unexpected zip extraction roots under {out_dir}: {roots}")
    return roots[0]


def _iter_csv_rows(path: Path) -> Iterable[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield dict(row)


def build_shopping_tables(
    shopping_root: Path,
    extracted_root: Path,
    parquet_root: Path,
) -> Dict[str, int]:
    queries_by_level: Dict[int, Dict[str, str]] = {}
    shopping_query_rows: List[Dict] = []

    for level in (1, 2, 3):
        qpath = shopping_root / "data" / f"level_{level}_query_meta.json"
        data = _read_json(qpath)
        qmap: Dict[str, str] = {}
        for sample in data:
            sid = str(sample["id"])
            query = sample.get("query", "")
            qmap[sid] = query
            shopping_query_rows.append(
                {
                    "domain": "shopping",
                    "level": level,
                    "case_id": sid,
                    "query": query,
                    "source_query_file": str(qpath),
                }
            )
        queries_by_level[level] = qmap

    shopping_case_rows: List[Dict] = []
    shopping_gt_product_rows: List[Dict] = []
    shopping_gt_coupon_rows: List[Dict] = []
    shopping_product_catalog_rows: List[Dict] = []
    shopping_user_info_rows: List[Dict] = []
    shopping_initial_cart_rows: List[Dict] = []

    for level in (1, 2, 3):
        level_dir = extracted_root / f"database_level{level}"
        case_dirs = sorted(
            [p for p in level_dir.glob("case_*") if p.is_dir()],
            key=lambda p: int(p.name.split("_")[1]),
        )

        for cdir in case_dirs:
            case_id = str(int(cdir.name.split("_")[1]))
            validation = _read_json(cdir / "validation_cases.json")
            user_info = _read_json(cdir / "user_info.json")
            cart = _read_json(cdir / "cart.json")

            gt_products = validation.get("ground_truth_products", [])
            gt_coupons = validation.get("ground_truth_coupons", {})

            shopping_case_rows.append(
                {
                    "domain": "shopping",
                    "level": level,
                    "case_id": case_id,
                    "query": queries_by_level[level].get(case_id, validation.get("query", "")),
                    "validation_query": validation.get("query", ""),
                    "meta_info_json": json.dumps(validation.get("meta_info", {}), ensure_ascii=False),
                    "ground_truth_products_count": len(gt_products),
                    "ground_truth_coupons_count": len(gt_coupons),
                }
            )

            for idx, p in enumerate(gt_products):
                shopping_gt_product_rows.append(
                    {
                        "domain": "shopping",
                        "level": level,
                        "case_id": case_id,
                        "gt_index": idx,
                        "product_id": str(p.get("product_id", "")),
                        "name": str(p.get("name", "")),
                        "price": p.get("price"),
                        "brand": str(p.get("brand", "")),
                        "size": str(p.get("size", "")),
                        "color": str(p.get("color", "")),
                        "product_json": json.dumps(p, ensure_ascii=False),
                    }
                )

            for coupon_name, qty in gt_coupons.items():
                shopping_gt_coupon_rows.append(
                    {
                        "domain": "shopping",
                        "level": level,
                        "case_id": case_id,
                        "coupon_name": str(coupon_name),
                        "quantity": int(qty),
                    }
                )

            shopping_user_info_rows.append(
                {
                    "domain": "shopping",
                    "level": level,
                    "case_id": case_id,
                    "user_id": str(user_info.get("user_id", "")),
                    "username": str(user_info.get("username", "")),
                    "is_vip": bool(user_info.get("is_vip", False)),
                    "user_info_json": json.dumps(user_info, ensure_ascii=False),
                }
            )

            shopping_initial_cart_rows.append(
                {
                    "domain": "shopping",
                    "level": level,
                    "case_id": case_id,
                    "user_id": str(cart.get("user_id", "")),
                    "items_count": len(cart.get("items", [])),
                    "used_coupons_count": len(cart.get("used_coupons", [])),
                    "cart_json": json.dumps(cart, ensure_ascii=False),
                }
            )

            products_path = cdir / "products.jsonl"
            with products_path.open("r", encoding="utf-8") as f:
                for row_idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    p = json.loads(line)
                    shopping_product_catalog_rows.append(
                        {
                            "domain": "shopping",
                            "level": level,
                            "case_id": case_id,
                            "row_id": row_idx,
                            "product_id": str(p.get("product_id", "")),
                            "name": str(p.get("name", "")),
                            "brand": str(p.get("brand", "")),
                            "color": str(p.get("color", "")),
                            "size": str(p.get("size", "")),
                            "price": p.get("price"),
                            "stock_quantity": p.get("stock_quantity"),
                            "rating": p.get("rating"),
                            "sales_volume": p.get("sales_volume"),
                            "shipping_info_json": json.dumps(p.get("shipping_info", {}), ensure_ascii=False),
                            "product_json": json.dumps(p, ensure_ascii=False),
                        }
                    )

    counts = {
        "shopping_queries": _write_parquet(shopping_query_rows, parquet_root / "shopping_queries.parquet"),
        "shopping_cases": _write_parquet(shopping_case_rows, parquet_root / "shopping_cases.parquet"),
        "shopping_gt_products": _write_parquet(shopping_gt_product_rows, parquet_root / "shopping_gt_products.parquet"),
        "shopping_gt_coupons": _write_parquet(shopping_gt_coupon_rows, parquet_root / "shopping_gt_coupons.parquet"),
        "shopping_catalog": _write_parquet(shopping_product_catalog_rows, parquet_root / "shopping_catalog.parquet"),
        "shopping_user_info": _write_parquet(shopping_user_info_rows, parquet_root / "shopping_user_info.parquet"),
        "shopping_initial_cart": _write_parquet(shopping_initial_cart_rows, parquet_root / "shopping_initial_cart.parquet"),
    }
    return counts


def build_travel_tables(
    travel_root: Path,
    extracted_root: Path,
    parquet_root: Path,
    include_distance_matrix: bool,
) -> Dict[str, int]:
    travel_query_rows: List[Dict] = []
    travel_constraints_rows: List[Dict] = []

    for lang in ("en", "zh"):
        qpath = travel_root / "data" / f"travelplanning_query_{lang}.json"
        data = _read_json(qpath)
        for sample in data:
            sample_id = str(sample.get("id"))
            meta = sample.get("meta_info", {})
            travel_query_rows.append(
                {
                    "domain": "travel",
                    "language": lang,
                    "sample_id": sample_id,
                    "query": sample.get("query", ""),
                    "query_with_constraints": sample.get("query_with_constraints", ""),
                    "source_query_file": str(qpath),
                }
            )
            travel_constraints_rows.append(
                {
                    "domain": "travel",
                    "language": lang,
                    "sample_id": sample_id,
                    "org": str(meta.get("org", "")),
                    "dest_json": json.dumps(meta.get("dest", []), ensure_ascii=False),
                    "days": meta.get("days"),
                    "depart_date": str(meta.get("depart_date", "")),
                    "return_date": str(meta.get("return_date", "")),
                    "people_number": meta.get("people_number"),
                    "room_number": meta.get("room_number"),
                    "depart_weekday": meta.get("depart_weekday"),
                    "hard_constraints_json": json.dumps(meta.get("hard_constraints", {}), ensure_ascii=False),
                    "meta_info_json": json.dumps(meta, ensure_ascii=False),
                }
            )

    table_to_rows: Dict[str, List[Dict]] = {
        "travel_db_trains": [],
        "travel_db_flights": [],
        "travel_db_hotels": [],
        "travel_db_restaurants": [],
        "travel_db_attractions": [],
        "travel_db_locations": [],
    }
    if include_distance_matrix:
        table_to_rows["travel_db_transportation"] = []

    for lang in ("en", "zh"):
        db_root = extracted_root / f"database_{lang}"
        id_dirs = sorted([p for p in db_root.glob("id_*") if p.is_dir()], key=lambda p: int(p.name.split("_")[1]))

        for id_dir in id_dirs:
            sample_id = str(int(id_dir.name.split("_")[1]))
            file_map: List[Tuple[str, Path]] = [
                ("travel_db_trains", id_dir / "trains" / "trains.csv"),
                ("travel_db_flights", id_dir / "flights" / "flights.csv"),
                ("travel_db_hotels", id_dir / "hotels" / "hotels.csv"),
                ("travel_db_restaurants", id_dir / "restaurants" / "restaurants.csv"),
                ("travel_db_attractions", id_dir / "attractions" / "attractions.csv"),
                ("travel_db_locations", id_dir / "locations" / "locations_coords.csv"),
            ]
            if include_distance_matrix:
                file_map.append(("travel_db_transportation", id_dir / "transportation" / "distance_matrix.csv"))

            for table_name, csv_path in file_map:
                for row in _iter_csv_rows(csv_path):
                    row["domain"] = "travel"
                    row["language"] = lang
                    row["sample_id"] = sample_id
                    table_to_rows[table_name].append(row)

    counts = {
        "travel_queries": _write_parquet(travel_query_rows, parquet_root / "travel_queries.parquet"),
        "travel_constraints": _write_parquet(travel_constraints_rows, parquet_root / "travel_constraints.parquet"),
    }
    for table_name, rows in table_to_rows.items():
        counts[table_name] = _write_parquet(rows, parquet_root / f"{table_name}.parquet")
    return counts


def build_manifest(out_path: Path, counts: Dict[str, int], include_distance_matrix: bool, source_qwen_agent_root: Path) -> None:
    manifest = {
        "dataset": "DeepPlanning-parquet",
        "source_dataset": HF_DATASET_ID,
        "source_qwen_agent_root": str(source_qwen_agent_root),
        "include_distance_matrix": include_distance_matrix,
        "tables": counts,
    }
    out_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build parquet tables from DeepPlanning raw data")
    parser.add_argument(
        "--qwen-agent-root",
        type=Path,
        default=Path("/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning"),
        help="Path to Qwen-Agent benchmark/deepplanning directory",
    )
    parser.add_argument(
        "--raw-cache-dir",
        type=Path,
        default=Path("artifacts/raw_hf"),
        help="Directory for downloaded raw archives",
    )
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path("artifacts/work"),
        help="Temporary extraction working directory",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("artifacts/deepplanning_parquet"),
        help="Output parquet directory",
    )
    parser.add_argument(
        "--include-distance-matrix",
        action="store_true",
        help="Include travel distance matrix table (largest table)",
    )
    args = parser.parse_args()

    _ensure_dir(args.raw_cache_dir)
    _ensure_dir(args.work_dir)
    _ensure_dir(args.out_dir)

    snapshot_download(
        repo_id=HF_DATASET_ID,
        repo_type="dataset",
        allow_patterns=RAW_FILES,
        local_dir=str(args.raw_cache_dir),
        local_dir_use_symlinks=False,
    )

    shopping_root = args.qwen_agent_root / "shoppingplanning"
    travel_root = args.qwen_agent_root / "travelplanning"

    if not shopping_root.exists() or not travel_root.exists():
        raise FileNotFoundError(f"Invalid qwen-agent root: {args.qwen_agent_root}")

    shopping_extracted = args.work_dir / "shopping"
    travel_en_extracted = args.work_dir / "travel_en"
    travel_zh_extracted = args.work_dir / "travel_zh"

    level1_root = _extract_tar(args.raw_cache_dir / "database_level1.tar.gz", shopping_extracted / "level1")
    _extract_tar(args.raw_cache_dir / "database_level2.tar.gz", shopping_extracted / "level2")
    _extract_tar(args.raw_cache_dir / "database_level3.tar.gz", shopping_extracted / "level3")

    # Consolidate shopping extracted roots into one directory for easier iteration.
    consolidated_shopping = args.work_dir / "shopping_consolidated"
    _ensure_dir(consolidated_shopping)
    for level, src in [(1, shopping_extracted / "level1" / "database_level1"), (2, shopping_extracted / "level2" / "database_level2"), (3, shopping_extracted / "level3" / "database_level3")]:
        dst = consolidated_shopping / f"database_level{level}"
        if not dst.exists():
            dst.symlink_to(src)

    _extract_zip(args.raw_cache_dir / "database_en.zip", travel_en_extracted)
    _extract_zip(args.raw_cache_dir / "database_zh.zip", travel_zh_extracted)

    consolidated_travel = args.work_dir / "travel_consolidated"
    _ensure_dir(consolidated_travel)
    for lang, src in [("en", travel_en_extracted / "database_en"), ("zh", travel_zh_extracted / "database_zh")]:
        dst = consolidated_travel / f"database_{lang}"
        if not dst.exists():
            dst.symlink_to(src)

    counts: Dict[str, int] = {}
    counts.update(build_shopping_tables(shopping_root, consolidated_shopping, args.out_dir))
    counts.update(build_travel_tables(travel_root, consolidated_travel, args.out_dir, args.include_distance_matrix))

    build_manifest(args.out_dir / "manifest.json", counts, args.include_distance_matrix, args.qwen_agent_root)
    print(json.dumps({"status": "ok", "out_dir": str(args.out_dir), "tables": counts}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
