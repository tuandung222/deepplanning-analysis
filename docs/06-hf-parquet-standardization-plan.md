# Kế Hoạch Chuẩn Hóa DeepPlanning Và Publish Lên Hugging Face Hub

## Mục tiêu

Chuẩn hóa dataset DeepPlanning thành định dạng bảng Parquet, giữ tương thích logic benchmark gốc, và publish lên HF Hub để:
- Tải/chọn subset nhanh hơn.
- Phân tích/đánh giá reproducible hơn.
- Dễ tích hợp với `datasets`, Spark, DuckDB, Polars, Arrow.

## Phạm vi dữ liệu

1. Nguồn gốc raw
- HF raw dataset: `Qwen/DeepPlanning`
- Code + query benchmark: `QwenLM/Qwen-Agent/benchmark/deepplanning`

2. Domain
- Travel: query + constraints + database per sample (`id_0..id_119` cho `en`/`zh`)
- Shopping: query level 1/2/3 + case database + ground-truth validation

## Thiết kế bảng chuẩn hóa

1. Shopping
- `shopping_queries.parquet`
- `shopping_cases.parquet`
- `shopping_gt_products.parquet`
- `shopping_gt_coupons.parquet`
- `shopping_catalog.parquet`
- `shopping_user_info.parquet`
- `shopping_initial_cart.parquet`

2. Travel
- `travel_queries.parquet`
- `travel_constraints.parquet`
- `travel_db_trains.parquet`
- `travel_db_flights.parquet`
- `travel_db_hotels.parquet`
- `travel_db_restaurants.parquet`
- `travel_db_attractions.parquet`
- `travel_db_locations.parquet`
- `travel_db_transportation.parquet` (tùy chọn vì lớn)

3. Key join
- Shopping: `domain`, `level`, `case_id`
- Travel: `domain`, `language`, `sample_id`

## Quy trình triển khai

### Phase 1: Ingest raw

1. Tải 5 archive từ HF:
- `database_en.zip`, `database_zh.zip`
- `database_level1.tar.gz`, `database_level2.tar.gz`, `database_level3.tar.gz`
2. Đọc query file từ Qwen-Agent local:
- `travelplanning/data/travelplanning_query_{en,zh}.json`
- `shoppingplanning/data/level_{1,2,3}_query_meta.json`

### Phase 2: Transform chuẩn hóa

1. Parse JSON/JSONL/CSV.
2. Flatten trường nested quan trọng, đồng thời giữ `*_json` raw để audit.
3. Chuẩn hóa cột định danh và domain-level-language metadata.
4. Ghi Parquet nén `zstd`.

### Phase 3: Validation

1. Kiểm tra đủ bảng required.
2. Kiểm tra key-overlap:
- shopping: `shopping_cases.case_id ⊆ shopping_queries.case_id`
- travel: `travel_constraints (lang,id) ⊆ travel_queries (lang,id)`
3. Sinh `validation_report.json`.

### Phase 4: Packaging HF

1. Gom các file parquet + `manifest.json` + `validation_report.json` vào thư mục publish.
2. Thêm `.gitattributes` dùng LFS cho parquet/json lớn.
3. Tạo dataset repo `tuandunghcmut/deepplanning-parquet`.
4. Upload bằng `huggingface_hub`.

### Phase 5: Release governance

1. Gắn version build (ví dụ `v1.0.0`).
2. Lưu nguồn tham chiếu:
- HF raw SHA
- Qwen-Agent commit
- build timestamp
3. Đảm bảo README có pseudo-code metric + công thức + caveat.

## Tiêu chí hoàn thành

- Có đủ bảng parquet theo thiết kế.
- Có `manifest.json` và `validation_report.json`.
- Có dataset card đầy đủ format/metric/reference/usage.
- Có thể load bằng `datasets` không lỗi.
- Có thể truy cập công khai trên HF Hub.

## Rủi ro và giảm thiểu

1. Query file không nằm trong HF raw
- Giải pháp: lấy query từ code Qwen-Agent và ghi rõ provenance trong manifest/README.

2. Dung lượng lớn (distance matrix)
- Giải pháp: build mặc định không gồm `travel_db_transportation`; bật bằng cờ `--include-distance-matrix` khi cần.

3. Drift schema tương lai
- Giải pháp: giữ `*_json` raw và thêm validation schema snapshot mỗi release.
