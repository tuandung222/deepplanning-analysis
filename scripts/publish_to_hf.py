#!/usr/bin/env python3
"""Create/update HF dataset repo and upload parquet folder."""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import HfApi


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish DeepPlanning parquet dataset to Hugging Face Hub")
    parser.add_argument("--username", default="tuandunghcmut", help="HF username")
    parser.add_argument("--dataset-name", default="deepplanning-parquet", help="HF dataset repo name")
    parser.add_argument("--source-dir", type=Path, default=Path("hf_publish"), help="Folder to upload")
    parser.add_argument("--private", action="store_true", help="Create private dataset repo")
    parser.add_argument("--commit-message", default="Upload DeepPlanning parquet standardized dataset")
    args = parser.parse_args()

    if not args.source_dir.exists():
        raise FileNotFoundError(args.source_dir)

    repo_id = f"{args.username}/{args.dataset_name}"
    api = HfApi()
    api.create_repo(repo_id=repo_id, repo_type="dataset", private=args.private, exist_ok=True)

    api.upload_folder(
        repo_id=repo_id,
        repo_type="dataset",
        folder_path=str(args.source_dir),
        commit_message=args.commit_message,
    )

    print(f"Uploaded dataset to: https://huggingface.co/datasets/{repo_id}")


if __name__ == "__main__":
    main()
