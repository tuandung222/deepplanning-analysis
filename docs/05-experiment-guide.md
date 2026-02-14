# Hướng Dẫn Chạy Thí Nghiệm Benchmark

## 0) Chuẩn bị

### Clone mã nguồn benchmark

```bash
cd /Users/admin/TuanDung/repos
git clone https://github.com/QwenLM/Qwen-Agent.git
cd Qwen-Agent
```

Nếu đã clone sẵn:

```bash
cd /Users/admin/TuanDung/repos/Qwen-Agent
git pull --ff-only
```

### Tạo môi trường

```bash
cd /Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning
conda create -n deepplanning python=3.10 -y
conda activate deepplanning
pip install -r requirements.txt
```

### Tải dataset

Từ: https://huggingface.co/datasets/Qwen/DeepPlanning

Copy file vào đúng chỗ:
- `shoppingplanning/database_zip/database_level1.tar.gz`
- `shoppingplanning/database_zip/database_level2.tar.gz`
- `shoppingplanning/database_zip/database_level3.tar.gz`
- `travelplanning/database/database_zh.zip`
- `travelplanning/database/database_en.zip`

Giải nén:

```bash
# shopping
cd shoppingplanning/database_zip
tar -xzf database_level1.tar.gz -C ..
tar -xzf database_level2.tar.gz -C ..
tar -xzf database_level3.tar.gz -C ..
cd ../..

# travel
cd travelplanning/database
unzip database_zh.zip
unzip database_en.zip
cd ../..
```

### Cấu hình model/backend

Tạo `models_config.json` và `.env` tại `benchmark/deepplanning`.

Ví dụ env:

```bash
cp env.example .env
# sửa .env
# DASHSCOPE_API_KEY=...
# OPENAI_API_KEY=...
```

## 1) Chạy full benchmark (khuyên dùng)

```bash
cd /Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning
bash run_all.sh
```

Sửa nhanh biến trong `run_all.sh`:
- `DOMAINS="travel shopping"`
- `BENCHMARK_MODEL="qwen-plus"`
- `SHOPPING_LEVELS="1 2 3"`
- `TRAVEL_LANGUAGE=""` (rỗng = chạy cả `zh` + `en`)
- `*_WORKERS`, `*_MAX_LLM_CALLS`

## 2) Chạy riêng Shopping

```bash
cd /Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/shoppingplanning
SHOPPING_AGENT_MODEL="qwen-plus" \
SHOPPING_LEVELS="1 2 3" \
SHOPPING_WORKERS=50 \
SHOPPING_MAX_LLM_CALLS=400 \
bash run.sh
```

Kết quả chính:
- `result_report/{model}_statistics.json`

## 3) Chạy riêng Travel

```bash
cd /Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/travelplanning
BENCHMARK_MODEL="qwen-plus" \
BENCHMARK_LANGUAGE="" \
BENCHMARK_WORKERS=10 \
BENCHMARK_MAX_LLM_CALLS=400 \
BENCHMARK_START_FROM="inference" \
bash run.sh
```

Resume nhanh:
- đặt `BENCHMARK_START_FROM="conversion"` hoặc `"evaluation"`.

## 4) Tổng hợp cross-domain

```bash
cd /Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning
python aggregate_results.py --model_name qwen-plus
cat aggregated_results/qwen-plus_aggregated.json
```

## 5) Gợi ý thiết kế thí nghiệm

1. Single-model baseline:
- 1 model, chạy full `travel+shopping`, lưu metric chuẩn.

2. Ablation max calls:
- giữ model cố định, quét `MAX_LLM_CALLS` (100/200/400).

3. Ablation workers:
- giữ model cố định, quét workers (10/20/50), theo dõi lỗi timeout/chất lượng.

4. Cross-model comparison:
- giữ config cố định, thay model list trong `BENCHMARK_MODEL`.

5. Resume stress test:
- dừng giữa chừng, chạy lại để kiểm tra khả năng khôi phục tiến trình.

## 6) Checklist tái lập kết quả

- Dùng cùng commit mã nguồn.
- Dùng cùng phiên bản dataset file nén.
- Nêu rõ model phiên bản/date endpoint.
- Log đầy đủ env (`workers`, `max_llm_calls`, `language`, `start-from`).
- Lưu toàn bộ artifacts: report, converted plans, evaluation summary, aggregated results.
