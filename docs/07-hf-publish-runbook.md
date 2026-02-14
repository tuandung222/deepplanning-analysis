# Runbook: Build Và Publish DeepPlanning Parquet Lên HF Hub

## 1) Cài dependency

```bash
cd /Users/admin/TuanDung/repos/deepplanning-analysis
python -m pip install -r etl/requirements.txt
```

## 2) Build parquet

```bash
cd /Users/admin/TuanDung/repos/deepplanning-analysis
./etl/build_deepplanning_parquet.py \
  --qwen-agent-root /Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning \
  --out-dir artifacts/deepplanning_parquet
```

Nếu cần bảng lớn `distance_matrix`:

```bash
./etl/build_deepplanning_parquet.py \
  --qwen-agent-root /Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning \
  --out-dir artifacts/deepplanning_parquet \
  --include-distance-matrix
```

## 3) Validate

```bash
./etl/validate_deepplanning_parquet.py --parquet-dir artifacts/deepplanning_parquet
```

## 4) Chuẩn bị thư mục upload

```bash
./scripts/prepare_hf_publish_dir.sh artifacts/deepplanning_parquet hf_publish hf/README.dataset_card.md
```

## 5) Publish lên HF (username: tuandunghcmut)

```bash
./scripts/publish_to_hf.py \
  --username tuandunghcmut \
  --dataset-name deepplanning-parquet \
  --source-dir hf_publish
```

Sau khi xong, URL dự kiến:
- `https://huggingface.co/datasets/tuandunghcmut/deepplanning-parquet`

## 6) Checklist sau publish

- Kiểm tra tab Files có đủ `.parquet`, `README.md`, `manifest.json`, `validation_report.json`.
- Kiểm tra snippet `datasets.load_dataset` chạy được.
- Gắn tag/release note trong repo phân tích nếu cần.
