# Benchmark, Metric, Và Mapping Mã Nguồn

## Tổng quan benchmark

DeepPlanning gồm 2 benchmark con:
- `travelplanning`: 120 task tiếng Trung + 120 task tiếng Anh.
- `shoppingplanning`: 120 task tiếng Anh chia level 1/2/3.

Nguồn xác nhận: `qwen-agent-docs/website/content/en/benchmarks/deepplanning/index.mdx` trong repo `Qwen-Agent`.

## 1) Shopping Planning

### Input / Output

- Input: `shoppingplanning/data/level_{1|2|3}_query_meta.json`
- DB runtime: `shoppingplanning/database_level{1|2|3}` (từ file nén dataset)
- Output inference: `shoppingplanning/database_infered/database_{model}_level{level}_{timestamp}`
- Output evaluation: `shoppingplanning/result_report/...`

### Metric chính

1. `match_rate`
- Công thức: `total_matched_products_sum / total_expected_products_sum`
- File: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/shoppingplanning/evaluation/score_statistics.py:154`

2. `weighted_average_case_score`
- Công thức: trung bình có trọng số theo số lượng case mỗi level.
- File: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/shoppingplanning/evaluation/score_statistics.py:142`

3. `valid`
- Từ từng level: invalid nếu tỷ lệ case chưa hoàn thành cao (`incomplete_rate` quá ngưỡng).
- Logic level: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/shoppingplanning/evaluation/evaluation_pipeline.py`
- Tổng hợp all-level: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/shoppingplanning/evaluation/score_statistics.py:160`

## 2) Travel Planning

### Input / Output

- Input query: `travelplanning/data/travelplanning_query_{zh|en}.json`
- DB runtime: `travelplanning/database/database_{zh|en}`
- Output inference: `results/{model}_{lang}/reports` và `trajectories`
- Output conversion: `results/{model}_{lang}/converted_plans`
- Output evaluation: `results/{model}_{lang}/evaluation/evaluation_summary.json`

### Metric chính

1. `commonsense_score`
- Tính từ 8 nhóm dimension, mỗi nhóm trọng số 0.125.
- One-vote-veto theo từng dimension.
- File cấu hình dimension: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/travelplanning/evaluation/constraints_commonsense.py`
- Hàm tính weighted: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/travelplanning/evaluation/eval_converted.py`

2. `personalized_score`
- Kiểm tra hard constraints (0 hoặc 1 theo one-vote-veto).
- File: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/travelplanning/evaluation/eval_converted.py`

3. `composite_score`
- Công thức: `(commonsense_score + personalized_score) / 2`
- File: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/travelplanning/evaluation/eval_converted.py:194`

4. `case_acc`
- Công thức: `1` chỉ khi cả `commonsense_score == 1.0` và `personalized_score == 1.0`, ngược lại `0`.
- File: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/travelplanning/evaluation/eval_converted.py:197`

5. `delivery_rate`
- Tỷ lệ sample có output plan được nộp để đánh giá.
- File: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/travelplanning/evaluation/eval_converted.py`

## 3) Cross-domain aggregation

File điều phối tổng hợp: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/aggregate_results.py`

### Trường tổng hợp quan trọng

- Shopping giữ `match_rate`, `weighted_average_case_score`.
- Travel lấy trung bình theo ngôn ngữ cho `composite_score`, `case_acc`, `commonsense_score`, `personalized_score`.
- Cross-domain metric: `avg_acc = (shopping_weighted_average_case_score + travel_case_acc) / 2`.

## Lưu ý kỹ thuật quan trọng

Trong `aggregate_results.py`, hàm `aggregate_model_results(..., travel_output_dir)` hiện gọi `load_travel_statistics(...)` mà chưa truyền `travel_output_dir`, nên có thể không đọc đúng thư mục custom output khi bạn set `TRAVEL_OUTPUT_DIR`.
