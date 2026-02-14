---
language:
- en
- zh
license: apache-2.0
task_categories:
- text-generation
tags:
- planning
- llm-benchmark
- reasoning
- autonomous-agents
- parquet
pretty_name: DeepPlanning Parquet Standardized
size_categories:
- 1k<n<10k
viewer: true
---

# DeepPlanning Parquet Standardized

This dataset is a **Parquet-standardized release** of DeepPlanning benchmark assets, built for analytics, reproducibility, and easier programmatic usage.

## Source And Provenance

- Raw dataset: [Qwen/DeepPlanning](https://huggingface.co/datasets/Qwen/DeepPlanning)
- Benchmark code: [QwenLM/Qwen-Agent/benchmark/deepplanning](https://github.com/QwenLM/Qwen-Agent/tree/main/benchmark/deepplanning)
- Paper: [DeepPlanning: Benchmarking Long-Horizon Agentic Planning with Verifiable Constraints](https://arxiv.org/abs/2601.18137)
- Maintainer: `tuandunghcmut`

Important note:
- The raw HF dataset contains environment archives (`database_*.zip`, `database_level*.tar.gz`).
- Query files (`travelplanning_query_*.json`, `level_*_query_meta.json`) are sourced from the benchmark code repository and tracked in `manifest.json`.

## What This Dataset Contains

### Shopping tables

- `shopping_queries.parquet`: benchmark input prompts by level/case.
- `shopping_cases.parquet`: per-case metadata + summary of ground truth.
- `shopping_gt_products.parquet`: exploded ground-truth product list.
- `shopping_gt_coupons.parquet`: exploded ground-truth coupon map.
- `shopping_catalog.parquet`: product candidate catalog (from `products.jsonl`).
- `shopping_user_info.parquet`: user profile per case.
- `shopping_initial_cart.parquet`: initial cart state before inference.

Primary keys:
- (`domain`, `level`, `case_id`)

### Travel tables

- `travel_queries.parquet`: input prompt and constraint-augmented prompt.
- `travel_constraints.parquet`: flattened `meta_info` and `hard_constraints`.
- `travel_db_trains.parquet`: train options per sample.
- `travel_db_flights.parquet`: flight options per sample.
- `travel_db_hotels.parquet`: hotel table per sample.
- `travel_db_restaurants.parquet`: restaurant table per sample.
- `travel_db_attractions.parquet`: attractions table per sample.
- `travel_db_locations.parquet`: POI geolocation table per sample.
- `travel_db_transportation.parquet` (optional build): distance matrix.

Primary keys:
- (`domain`, `language`, `sample_id`)

## Input And Ground Truth Format

### Shopping benchmark

Input:
- Query from `level_{1,2,3}_query_meta.json` (`id`, `query`).

Ground truth:
- `validation_cases.json` with `ground_truth_products` and optional `ground_truth_coupons`.
- Level 3 usually includes coupon constraints, level 1/2 often have empty coupon ground truth.

Environment:
- `products.jsonl`, `user_info.json`, initial `cart.json`.

### Travel benchmark

Input:
- `travelplanning_query_{en,zh}.json` entries with fields:
- `id`, `query`, `query_with_constraints`, `meta_info`.

Ground truth constraints:
- `meta_info` + `hard_constraints` in query file.
- Per-sample environment database under `database_{en,zh}/id_{k}/...`.

## Metrics (From Reference Code)

### Shopping metrics

Reference: `shoppingplanning/evaluation/evaluation_pipeline.py`, `score_statistics.py`.

Per-case:

```text
matched_count = |cart_products ∩ gt_products| + matched_coupons
expected_count = |gt_products| + |gt_coupons|
score = matched_count / expected_count
case_score = 1 if matched_count == expected_count else 0
```

Aggregate:

```text
match_rate = sum(matched_count_case) / sum(expected_count_case)
weighted_average_case_score = weighted mean of level average_case_score by case count
valid = (incomplete_rate <= 0.1)
```

### Travel metrics

Reference: `travelplanning/evaluation/eval_converted.py`, `constraints_commonsense.py`, `constraints_hard.py`.

Per-case:

```text
commonsense_score = Σ(weight_dim * dim_pass), dim_pass ∈ {0,1}
personalized_score = 1 if all hard constraints pass else 0
composite_score = (commonsense_score + personalized_score) / 2
case_acc = 1 if (commonsense_score == 1 and personalized_score == 1) else 0
```

Aggregate:

```text
delivery_rate = num_plan_files / total_test_samples
commonsense_avg = avg(commonsense_score)
personalized_avg = avg(personalized_score)
composite_avg = avg(composite_score)
case_acc_avg = avg(case_acc)
```

## How To Use

### Python (`datasets`)

```python
from datasets import load_dataset

ds = load_dataset("tuandunghcmut/deepplanning-parquet", data_files={
    "shopping_cases": "shopping_cases.parquet",
    "travel_queries": "travel_queries.parquet",
})

print(ds["shopping_cases"][0])
```

### Pandas/Polars/Arrow

```python
import pandas as pd
shopping = pd.read_parquet("hf://datasets/tuandunghcmut/deepplanning-parquet/shopping_cases.parquet")
travel = pd.read_parquet("hf://datasets/tuandunghcmut/deepplanning-parquet/travel_queries.parquet")
```

### Join example

```python
joined = shopping.merge(
    pd.read_parquet("hf://datasets/tuandunghcmut/deepplanning-parquet/shopping_gt_products.parquet"),
    on=["domain", "level", "case_id"],
    how="left",
)
```

## Reproducibility Artifacts

- `manifest.json`: source references + table row counts.
- `validation_report.json`: structural consistency checks.

## Limitations

- Query files are sourced from benchmark code repo, not bundled in raw HF archive.
- Any metric computation should follow reference code behavior to avoid subtle drift.
- Some nested semantic fields are retained as JSON strings for lossless traceability.

## Citation

```bibtex
@article{deepplanning,
  title={DeepPlanning: Benchmarking Long-Horizon Agentic Planning with Verifiable Constraints},
  author={
    Yinger Zhang and Shutong Jiang and Renhao Li and Jianhong Tu and Yang Su and
    Lianghao Deng and Xudong Guo and Chenxu Lv and Junyang Lin
  },
  journal={arXiv preprint arXiv:2601.18137},
  year={2026}
}
```
