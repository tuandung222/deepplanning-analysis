#!/usr/bin/env bash
set -euo pipefail

PARQUET_DIR="${1:-artifacts/deepplanning_parquet}"
PUBLISH_DIR="${2:-hf_publish}"
CARD_FILE="${3:-hf/README.dataset_card.md}"

mkdir -p "$PUBLISH_DIR"
cp -f "$CARD_FILE" "$PUBLISH_DIR/README.md"
cp -f "$PARQUET_DIR"/*.parquet "$PUBLISH_DIR/"
cp -f "$PARQUET_DIR"/manifest.json "$PUBLISH_DIR/" || true
cp -f "$PARQUET_DIR"/validation_report.json "$PUBLISH_DIR/" || true

cat > "$PUBLISH_DIR/.gitattributes" <<'EOF'
*.parquet filter=lfs diff=lfs merge=lfs -text
*.json filter=lfs diff=lfs merge=lfs -text
EOF

echo "Prepared HF publish dir: $PUBLISH_DIR"
