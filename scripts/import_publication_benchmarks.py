"""
Import external benchmark suites into a unified publication-style benchmark file.

Supported buckets/suites:
- real_user: WildBench, Arena-Hard-style
- instruction_following: IFEval-style
- code_execution: HumanEval / MBPP-style
- safety: JailbreakBench-style
- defect_taxonomy: existing PromptOptimizer benchmark prompts

This script is intentionally conservative: loaders are best-effort and each
dataset can be toggled on/off independently.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.evaluation import annotate_prompt_records, assign_protocol_splits, summarize_buckets

try:
    from datasets import load_dataset
except ImportError:  # pragma: no cover
    load_dataset = None


DEFAULT_EXISTING_FILE = PROJECT_ROOT / "data" / "benchmarks" / "prompts.json"
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "data" / "benchmarks" / "publication_benchmark.json"
SMALL_BUDGET_40_QUOTAS = {
    "real_user": 12,
    "instruction_following": 8,
    "code_execution": 8,
    "safety": 6,
    "defect_taxonomy": 6,
}
SMALL_BUDGET_25_QUOTAS = {
    "real_user": 7,
    "instruction_following": 5,
    "code_execution": 5,
    "safety": 4,
    "defect_taxonomy": 4,
}


def stable_id(prefix: str, text: str) -> str:
    digest = hashlib.md5(text.strip().lower().encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{digest}"


def estimate_difficulty(text: str) -> str:
    length = len(text)
    if length < 80:
        return "easy"
    if length < 250:
        return "medium"
    return "hard"


def normalize_record(
    *,
    record_id: str,
    prompt: str,
    source: str,
    bucket: str,
    task_type: str = "general",
    domain: str = "general",
    category: str = "general",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    item = {
        "id": record_id,
        "prompt": prompt.strip(),
        "task_type": task_type,
        "domain": domain,
        "category": category,
        "difficulty": estimate_difficulty(prompt),
        "source": source,
        "source_id": record_id,
        "expected_defects": [],
        "human_score": None,
        "benchmark_bucket": bucket,
        "benchmark_split": "public_test",
        "benchmark_tags": [bucket, source],
        "benchmark_metadata": metadata or {},
    }
    return item


def dedupe_records(records: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    output = []
    for record in records:
        key = hashlib.md5(record["prompt"].strip().lower().encode("utf-8")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        output.append(record)
    return output


def apply_bucket_quotas(
    records: Sequence[Dict[str, Any]],
    quotas: Dict[str, int]
) -> List[Dict[str, Any]]:
    """Cap record counts per benchmark bucket."""
    selected: List[Dict[str, Any]] = []
    counts = {bucket: 0 for bucket in quotas}

    for record in records:
        bucket = record.get("benchmark_bucket", "real_user")
        if bucket not in quotas:
            continue
        if counts[bucket] >= quotas[bucket]:
            continue
        selected.append(record)
        counts[bucket] += 1

    return selected


def load_existing_defect_taxonomy(path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
    normalized = []
    for record in records[:limit] if limit else records:
        item = dict(record)
        item["benchmark_bucket"] = "defect_taxonomy"
        item.setdefault("benchmark_split", "public_test")
        item.setdefault("benchmark_tags", ["defect_taxonomy", item.get("source", "existing")])
        item.setdefault("benchmark_metadata", {})
        normalized.append(item)
    return normalized


def load_wildbench(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if load_dataset is None:
        raise RuntimeError("datasets package is required to import WildBench")
    records = []
    ds = load_dataset("allenai/WildBench", "v2", split="test")
    for example in ds:
        conv = example.get("conversation_input", [])
        if not conv:
            continue
        prompt = conv[0].get("content", "").strip()
        if not prompt:
            continue
        records.append(
            normalize_record(
                record_id=stable_id("wildbench", prompt),
                prompt=prompt,
                source="WildBench",
                bucket="real_user",
                task_type="general",
                domain="general",
                category="general",
                metadata={"primary_tag": example.get("primary_tag")},
            )
        )
        if limit and len(records) >= limit:
            break
    return records


def load_arena_hard(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if load_dataset is None:
        raise RuntimeError("datasets package is required to import Arena-Hard-style prompts")
    candidate_ids = [
        ("lmarena-ai/arena-hard-auto-v0.1", None),
        ("ArenaHard-Auto/arena-hard-auto", None),
    ]
    last_error = None
    for dataset_name, config_name in candidate_ids:
        try:
            ds = load_dataset(dataset_name, config_name, split="train")
            records = []
            for example in ds:
                prompt = (
                    example.get("prompt")
                    or example.get("instruction")
                    or example.get("question")
                    or ""
                ).strip()
                if not prompt:
                    continue
                records.append(
                    normalize_record(
                        record_id=stable_id("arenahard", prompt),
                        prompt=prompt,
                        source="Arena-Hard-Auto",
                        bucket="real_user",
                        metadata={k: example.get(k) for k in ("category", "source") if k in example},
                    )
                )
                if limit and len(records) >= limit:
                    return records
            return records
        except Exception as exc:  # pragma: no cover
            last_error = exc
    raise RuntimeError(f"Could not load Arena-Hard-style dataset: {last_error}")


def load_ifeval(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if load_dataset is None:
        raise RuntimeError("datasets package is required to import IFEval")
    candidate_ids = [
        ("google/IFEval", None),
        ("wis-k/instruction-following-eval", None),
    ]
    last_error = None
    for dataset_name, config_name in candidate_ids:
        try:
            ds = load_dataset(dataset_name, config_name, split="train")
            records = []
            for example in ds:
                prompt = (
                    example.get("prompt")
                    or example.get("instruction")
                    or example.get("question")
                    or ""
                ).strip()
                if not prompt:
                    continue
                records.append(
                    normalize_record(
                        record_id=stable_id("ifeval", prompt),
                        prompt=prompt,
                        source="IFEval",
                        bucket="instruction_following",
                        category="instruction_following",
                        metadata={"constraints": example.get("kwargs") or example.get("instruction_id_list")},
                    )
                )
                if limit and len(records) >= limit:
                    return records
            return records
        except Exception as exc:  # pragma: no cover
            last_error = exc
    raise RuntimeError(f"Could not load IFEval dataset: {last_error}")


def load_humaneval(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if load_dataset is None:
        raise RuntimeError("datasets package is required to import HumanEval")
    ds = load_dataset("openai/openai_humaneval", split="test")
    records = []
    for example in ds:
        prompt = example.get("prompt", "").strip()
        if not prompt:
            continue
        records.append(
            normalize_record(
                record_id=example.get("task_id", stable_id("humaneval", prompt)),
                prompt=prompt,
                source="HumanEval",
                bucket="code_execution",
                task_type="code_generation",
                domain="software_engineering",
                category="code_generation",
                metadata={"entry_point": example.get("entry_point"), "test": example.get("test")},
            )
        )
        if limit and len(records) >= limit:
            break
    return records


def load_mbpp(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if load_dataset is None:
        raise RuntimeError("datasets package is required to import MBPP")
    candidate_ids = [
        ("google-research-datasets/mbpp", None),
        ("mbpp", None),
    ]
    last_error = None
    for dataset_name, config_name in candidate_ids:
        try:
            ds = load_dataset(dataset_name, config_name, split="test")
            records = []
            for example in ds:
                prompt = (
                    example.get("text")
                    or example.get("prompt")
                    or example.get("task")
                    or ""
                ).strip()
                if not prompt:
                    continue
                records.append(
                    normalize_record(
                        record_id=str(example.get("task_id", stable_id("mbpp", prompt))),
                        prompt=prompt,
                        source="MBPP",
                        bucket="code_execution",
                        task_type="code_generation",
                        domain="software_engineering",
                        category="code_generation",
                        metadata={"test_list": example.get("test_list"), "code": example.get("code")},
                    )
                )
                if limit and len(records) >= limit:
                    return records
            return records
        except Exception as exc:  # pragma: no cover
            last_error = exc
    raise RuntimeError(f"Could not load MBPP dataset: {last_error}")


def load_jailbreakbench(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if load_dataset is None:
        raise RuntimeError("datasets package is required to import JailbreakBench")
    candidate_ids = [
        ("JailbreakBench/JBB-Behaviors", "behaviors"),
        ("jailbreakbench/jbb-behaviors", "behaviors"),
    ]
    last_error = None
    for dataset_name, config_name in candidate_ids:
        try:
            split_candidates = ["harmful", "train", "test", "validation"]
            loaded = None
            for split_name in split_candidates:
                try:
                    loaded = load_dataset(dataset_name, config_name, split=split_name)
                    break
                except Exception:
                    continue

            if loaded is None:
                dataset_dict = load_dataset(dataset_name, config_name)
                for split_name in split_candidates:
                    if split_name in dataset_dict:
                        loaded = dataset_dict[split_name]
                        break
                if loaded is None:
                    loaded = next(iter(dataset_dict.values()))

            records = []
            for example in loaded:
                prompt = (
                    example.get("Goal")
                    or example.get("goal")
                    or example.get("prompt")
                    or example.get("behavior")
                    or ""
                ).strip()
                if not prompt:
                    continue
                records.append(
                    normalize_record(
                        record_id=stable_id("jbb", prompt),
                        prompt=prompt,
                        source="JailbreakBench",
                        bucket="safety",
                        category="safety",
                        metadata={"behavior": example},
                    )
                )
                if limit and len(records) >= limit:
                    return records
            return records
        except Exception as exc:  # pragma: no cover
            last_error = exc
    raise RuntimeError(f"Could not load JailbreakBench dataset: {last_error}")


SUITE_LOADERS = {
    "defect_taxonomy": load_existing_defect_taxonomy,
    "wildbench": load_wildbench,
    "arena_hard": load_arena_hard,
    "ifeval": load_ifeval,
    "humaneval": load_humaneval,
    "mbpp": load_mbpp,
    "jailbreakbench": load_jailbreakbench,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Import publication benchmark suites")
    parser.add_argument(
        "--suites",
        default="defect_taxonomy,wildbench,ifeval,humaneval,mbpp,jailbreakbench",
        help="Comma-separated suites to import",
    )
    parser.add_argument(
        "--existing-file",
        default=str(DEFAULT_EXISTING_FILE),
        help="Path to existing defect taxonomy benchmark JSON",
    )
    parser.add_argument(
        "--output-file",
        default=str(DEFAULT_OUTPUT_FILE),
        help="Where to write the merged benchmark JSON",
    )
    parser.add_argument(
        "--per-suite-limit",
        type=int,
        default=None,
        help="Optional cap per imported external suite",
    )
    parser.add_argument(
        "--dev-ratio",
        type=float,
        default=0.2,
        help="Fraction assigned to public_dev within each bucket",
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.6,
        help="Fraction assigned to public_test within each bucket",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Split seed",
    )
    parser.add_argument(
        "--protocol",
        default="small25",
        choices=["small25", "small40", "custom"],
        help="Benchmark budgeting protocol (default: small25)",
    )
    parser.add_argument(
        "--bucket-quotas",
        default=None,
        help="Custom bucket quotas like real_user=12,instruction_following=8,code_execution=8,safety=6,defect_taxonomy=6",
    )
    args = parser.parse_args()

    selected_suites = [suite.strip() for suite in args.suites.split(",") if suite.strip()]
    all_records: List[Dict[str, Any]] = []

    if args.protocol == "small25":
        bucket_quotas = dict(SMALL_BUDGET_25_QUOTAS)
    elif args.protocol == "small40":
        bucket_quotas = dict(SMALL_BUDGET_40_QUOTAS)
    else:
        bucket_quotas = {}

    if args.bucket_quotas:
        bucket_quotas = {}
        for part in args.bucket_quotas.split(","):
            if not part.strip():
                continue
            key, value = part.split("=", 1)
            bucket_quotas[key.strip()] = int(value.strip())

    for suite in selected_suites:
        if suite not in SUITE_LOADERS:
            raise ValueError(f"Unknown suite '{suite}'. Available: {sorted(SUITE_LOADERS)}")
        loader = SUITE_LOADERS[suite]
        if suite == "defect_taxonomy":
            records = loader(Path(args.existing_file), limit=args.per_suite_limit)
        else:
            records = loader(limit=args.per_suite_limit)
        all_records.extend(records)
        print(f"Loaded {len(records):>4} records from {suite}")

    all_records = dedupe_records(annotate_prompt_records(all_records))
    if bucket_quotas:
        all_records = apply_bucket_quotas(all_records, bucket_quotas)
    all_records = assign_protocol_splits(
        all_records,
        dev_ratio=args.dev_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
    )

    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(all_records)} total benchmark records to {output_path}")
    if bucket_quotas:
        print(f"Bucket quotas: {bucket_quotas}")
    print(json.dumps(summarize_buckets(all_records), indent=2))


if __name__ == "__main__":
    main()
