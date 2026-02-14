# Kiến Trúc Mã Nguồn DeepPlanning

## Vị trí mã nguồn

DeepPlanning nằm trong mono-repo Qwen-Agent:
- `/Users/admin/TuanDung/repos/Qwen-Agent/benchmark/deepplanning`

## Cấu trúc thư mục

- `run_all.sh`: orchestrator chạy toàn benchmark.
- `models_config.json`: khai báo model/backend OpenAI-compatible.
- `requirements.txt`: dependencies cho cả travel + shopping.
- `aggregate_results.py`: tổng hợp điểm liên domain.
- `shoppingplanning/`: toàn bộ pipeline shopping.
- `travelplanning/`: toàn bộ pipeline travel.

## TravelPlanning backend

### Agent & Tooling

- Agent loop: `travelplanning/agent/tools_fn_agent.py`
- Model call abstraction: `travelplanning/agent/call_llm.py`
- Prompt templates: `travelplanning/agent/prompts.py`
- Tool implementations: `travelplanning/tools/*.py`
- Tool schema: `travelplanning/tools/tool_schema_{zh|en}.json`

### Data + Evaluation

- Query data: `travelplanning/data/travelplanning_query_{zh|en}.json`
- Conversion (text -> structured JSON): `travelplanning/evaluation/convert_report.py`
- Scoring: `travelplanning/evaluation/eval_converted.py`
- Constraint defs:
- Commonsense: `travelplanning/evaluation/constraints_commonsense.py`
- Hard/personalized: `travelplanning/evaluation/constraints_hard.py`

## ShoppingPlanning backend

### Agent & Tooling

- Agent loop: `shoppingplanning/agent/shopping_agent.py`
- Model call abstraction: `shoppingplanning/agent/call_llm.py`
- Prompt templates: `shoppingplanning/agent/prompts.py`
- Tool implementations: `shoppingplanning/tools/*.py`
- Tool schema: `shoppingplanning/tools/shopping_tool_schema.json`

### Data + Evaluation

- Query data: `shoppingplanning/data/level_{1|2|3}_query_meta.json`
- Inference entry: `shoppingplanning/run.py`
- Evaluation per run: `shoppingplanning/evaluation/evaluation_pipeline.py`
- Statistics across levels: `shoppingplanning/evaluation/score_statistics.py`

## Backend model abstraction

Cả 2 domain dùng cấu hình model từ `models_config.json` (ở root `benchmark/deepplanning`), theo kiểu OpenAI-compatible:
- `base_url`
- `api_key_env`
- `model_name`

Nhờ vậy bạn có thể thay backend giữa DashScope, OpenAI, hoặc endpoint compatible khác mà không cần đổi core benchmark logic.
