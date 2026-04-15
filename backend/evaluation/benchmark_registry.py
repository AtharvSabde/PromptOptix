"""
Benchmark registry helpers for publication-oriented evaluation.

Adds explicit benchmark buckets/splits on top of the flat prompt dataset.
"""

from __future__ import annotations

import json
from pathlib import Path
import random
from typing import Any, Dict, List, Optional, Sequence


BENCHMARK_BUCKETS = {
    "real_user": "Real-user prompts such as WildBench / Arena-Hard style tasks",
    "instruction_following": "Verifiable instruction-following tasks such as IFEval-style prompts",
    "code_execution": "Executable coding tasks such as HumanEval / MBPP / LiveCodeBench style prompts",
    "safety": "Safety / jailbreak / prompt-injection tasks such as JailbreakBench / AILuminate-style hazards",
    "defect_taxonomy": "PromptOptimizer-specific defect-taxonomy prompts and analyses",
}

BENCHMARK_SPLITS = {"public_dev", "public_test", "holdout"}


def infer_bucket(prompt_record: Dict[str, Any]) -> str:
    """Infer a benchmark bucket when not explicitly provided."""
    if prompt_record.get("benchmark_bucket"):
        return prompt_record["benchmark_bucket"]

    source = str(prompt_record.get("source", "")).lower()
    category = str(prompt_record.get("category", "")).lower()
    task_type = str(prompt_record.get("task_type", "")).lower()

    if "jailbreak" in source or "ailuminate" in source or category == "safety":
        return "safety"
    if any(name in source for name in ["humaneval", "mbpp", "livecodebench"]):
        return "code_execution"
    if "ifeval" in source or "instruction" in category:
        return "instruction_following"
    if prompt_record.get("expected_defects"):
        return "defect_taxonomy"
    if any(name in source for name in ["wildbench", "arena", "chat-1m", "lmsys"]):
        return "real_user"
    if task_type == "code_generation":
        return "code_execution"
    return "real_user"


def infer_split(prompt_record: Dict[str, Any]) -> str:
    """Infer a split when not explicitly provided."""
    if prompt_record.get("benchmark_split"):
        split = prompt_record["benchmark_split"]
        return split if split in BENCHMARK_SPLITS else "public_test"
    return "public_test"


def annotate_prompt_record(prompt_record: Dict[str, Any]) -> Dict[str, Any]:
    """Return a normalized benchmark record with bucket/split metadata."""
    normalized = dict(prompt_record)
    normalized["benchmark_bucket"] = infer_bucket(prompt_record)
    normalized["benchmark_split"] = infer_split(prompt_record)
    normalized.setdefault("benchmark_tags", [])
    return normalized


def annotate_prompt_records(prompt_records: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [annotate_prompt_record(record) for record in prompt_records]


def filter_prompt_records(
    prompt_records: Sequence[Dict[str, Any]],
    buckets: Optional[Sequence[str]] = None,
    split: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Filter normalized prompts by bucket and split."""
    records = annotate_prompt_records(prompt_records)

    if buckets:
        allowed = set(buckets)
        records = [record for record in records if record.get("benchmark_bucket") in allowed]

    if split:
        records = [record for record in records if record.get("benchmark_split") == split]

    return records


def summarize_buckets(prompt_records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize benchmark counts by bucket and split."""
    bucket_counts: Dict[str, int] = {}
    split_counts: Dict[str, int] = {}

    for record in annotate_prompt_records(prompt_records):
        bucket = record.get("benchmark_bucket", "unknown")
        split = record.get("benchmark_split", "unknown")
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
        split_counts[split] = split_counts.get(split, 0) + 1

    return {
        "bucket_distribution": bucket_counts,
        "split_distribution": split_counts,
    }


def assign_protocol_splits(
    prompt_records: Sequence[Dict[str, Any]],
    dev_ratio: float = 0.2,
    test_ratio: float = 0.6,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """Assign protocol splits stratified by benchmark bucket."""
    rng = random.Random(seed)
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for record in annotate_prompt_records(prompt_records):
        grouped.setdefault(record["benchmark_bucket"], []).append(dict(record))

    assigned: List[Dict[str, Any]] = []
    for bucket, records in grouped.items():
        rng.shuffle(records)
        n = len(records)
        n_dev = int(round(n * dev_ratio))
        n_test = int(round(n * test_ratio))
        if n_dev + n_test > n:
            n_test = max(0, n - n_dev)

        for idx, record in enumerate(records):
            if idx < n_dev:
                record["benchmark_split"] = "public_dev"
            elif idx < n_dev + n_test:
                record["benchmark_split"] = "public_test"
            else:
                record["benchmark_split"] = "holdout"
            assigned.append(record)

    return assigned


def load_protocol_template(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


__all__ = [
    "BENCHMARK_BUCKETS",
    "BENCHMARK_SPLITS",
    "infer_bucket",
    "infer_split",
    "annotate_prompt_record",
    "annotate_prompt_records",
    "filter_prompt_records",
    "summarize_buckets",
    "assign_protocol_splits",
    "load_protocol_template",
]
