# Pipeline Inference Và Evaluation

## Luồng tổng thể

1. Chạy benchmark theo domain/model.
2. Sinh output inference.
3. (Travel) convert report text sang JSON plan chuẩn.
4. Chạy evaluation để tính metric.
5. Tổng hợp kết quả theo domain và cross-domain.

Điểm vào full pipeline: `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning/run_all.sh`

## Shopping pipeline chi tiết

1. `shoppingplanning/run.sh`
- Tạo DB isolated cho từng run (`database_run_{model}_level{level}_{runid}`)
- Chạy `python run.py`
- Đưa DB infered vào `database_infered/`
- Chạy `evaluation/evaluation_pipeline.py`
- Chạy `evaluation/score_statistics.py`

2. `shoppingplanning/run.py`
- Load task theo level.
- Chạy multi-worker inference qua agent.

3. `shoppingplanning/evaluation/evaluation_pipeline.py`
- So cart cuối với ground truth product + coupon.
- Sinh report từng case và `summary_report.json`.

4. `shoppingplanning/evaluation/score_statistics.py`
- Lấy report mới nhất mỗi level, tổng hợp ra `{model}_statistics.json`.

## Travel pipeline chi tiết

1. `travelplanning/run.sh`
- Có pre-check cache để skip/resume.
- Có thể chạy đồng thời nhiều model.
- Mỗi model gọi `python run.py`.

2. `travelplanning/run.py`
- `start-from=inference`: chạy cả 3 stage.
- `start-from=conversion`: bỏ inference, parse report -> JSON.
- `start-from=evaluation`: chỉ chấm điểm từ converted plans.

3. `travelplanning/evaluation/convert_report.py`
- Parse report text bằng LLM (mặc định `qwen-plus`) thành JSON chuẩn.
- Output: `converted_plans/id_{k}_converted.json`

4. `travelplanning/evaluation/eval_converted.py`
- Chấm commonsense + hard constraints.
- Ghi `evaluation_summary.json` và per-case score.

## Kết quả và thư mục

- Shopping:
- `shoppingplanning/result_report/{model}_statistics.json`
- Travel:
- `travelplanning/results/{model}_{lang}/evaluation/evaluation_summary.json`
- Tổng hợp:
- `benchmark/deepplanning/aggregated_results/{model}_aggregated.json`
