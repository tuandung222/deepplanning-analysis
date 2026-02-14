# DeepPlanning Analysis (Qwen/Alibaba)

Repo này tổng hợp tài liệu phân tích chi tiết benchmark **DeepPlanning** của Qwen Team (Alibaba):
- Paper: https://arxiv.org/abs/2601.18137
- Dataset: https://huggingface.co/datasets/Qwen/DeepPlanning
- Code: https://github.com/QwenLM/Qwen-Agent/tree/main/benchmark/deepplanning

## Mục tiêu

1. Review paper: contribution, điểm mới, ý nghĩa.
2. Giải thích benchmark, metric và mapping chính xác sang file mã nguồn.
3. Hướng dẫn chạy inference benchmark trên dataset để tái tạo kết quả.
4. Phân tích cấu trúc codebase và backend phục vụ inference/evaluation.
5. Hướng dẫn chạy các thí nghiệm benchmark theo nhiều cấu hình.

## Cấu trúc tài liệu

- `docs/01-paper-review.md`: Review paper và contribution.
- `docs/02-benchmark-metrics-map.md`: Benchmark design, metric, công thức và mapping file.
- `docs/03-codebase-architecture.md`: Kiến trúc mã nguồn DeepPlanning.
- `docs/04-inference-eval-pipeline.md`: Luồng inference -> conversion -> evaluation -> aggregation.
- `docs/05-experiment-guide.md`: Playbook chạy thí nghiệm và tái lập kết quả.

## Nguồn phân tích

Phân tích trong repo này dựa trên:
- Mã nguồn local đã cập nhật từ `QwenLM/Qwen-Agent` (nhánh `main`, commit `0460a18` ngày 2026-02-14 local sync).
- Tài liệu benchmark trong chính repo Qwen-Agent.
- Paper arXiv và dataset Hugging Face chính thức.

## Trạng thái

- [x] Clone/cập nhật mã nguồn DeepPlanning vào `/Users/admin/TuanDung/repos/Qwen-Agent`.
- [x] Tạo repo phân tích GitHub.
- [x] Viết bộ tài liệu phân tích cốt lõi.

## Bộ Khung Chuẩn Hóa HF

Đã thêm bộ khung chuẩn hóa và publish lên Hugging Face Hub:

- ETL build parquet: `/Users/admin/TuanDung/repos/deepplanning-analysis/etl/build_deepplanning_parquet.py`
- Validation parquet: `/Users/admin/TuanDung/repos/deepplanning-analysis/etl/validate_deepplanning_parquet.py`
- Dataset card mẫu HF: `/Users/admin/TuanDung/repos/deepplanning-analysis/hf/README.dataset_card.md`
- Script prepare publish dir: `/Users/admin/TuanDung/repos/deepplanning-analysis/scripts/prepare_hf_publish_dir.sh`
- Script publish HF: `/Users/admin/TuanDung/repos/deepplanning-analysis/scripts/publish_to_hf.py`
- Runbook end-to-end: `/Users/admin/TuanDung/repos/deepplanning-analysis/docs/07-hf-publish-runbook.md`
