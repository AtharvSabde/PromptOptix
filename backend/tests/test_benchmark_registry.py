from backend.evaluation.benchmark_registry import (
    annotate_prompt_records,
    assign_protocol_splits,
    filter_prompt_records,
    summarize_buckets,
)
from scripts.import_publication_benchmarks import apply_bucket_quotas


def test_annotate_prompt_records_infers_bucket_and_split():
    records = annotate_prompt_records([
        {
            "id": "X1",
            "prompt": "Write python code to reverse a list",
            "task_type": "code_generation",
            "category": "code_generation",
            "source": "HumanEval",
        },
        {
            "id": "X2",
            "prompt": "Summarize this article",
            "task_type": "summarization",
            "category": "summarization",
            "source": "WildBench",
            "expected_defects": ["D001"],
        },
    ])

    assert records[0]["benchmark_bucket"] == "code_execution"
    assert records[0]["benchmark_split"] == "public_test"
    assert records[1]["benchmark_bucket"] == "defect_taxonomy"


def test_filter_prompt_records_by_bucket_and_split():
    records = [
        {"id": "A", "benchmark_bucket": "real_user", "benchmark_split": "public_dev"},
        {"id": "B", "benchmark_bucket": "safety", "benchmark_split": "public_test"},
        {"id": "C", "benchmark_bucket": "real_user", "benchmark_split": "public_test"},
    ]

    filtered = filter_prompt_records(records, buckets=["real_user"], split="public_test")
    assert [r["id"] for r in filtered] == ["C"]


def test_summarize_buckets_counts_distribution():
    summary = summarize_buckets([
        {"benchmark_bucket": "real_user", "benchmark_split": "public_dev"},
        {"benchmark_bucket": "real_user", "benchmark_split": "public_test"},
        {"benchmark_bucket": "safety", "benchmark_split": "public_test"},
    ])

    assert summary["bucket_distribution"]["real_user"] == 2
    assert summary["split_distribution"]["public_test"] == 2


def test_assign_protocol_splits_assigns_all_three_splits():
    records = [
        {"id": f"R{i}", "benchmark_bucket": "real_user", "prompt": f"prompt {i}"}
        for i in range(10)
    ]
    assigned = assign_protocol_splits(records, dev_ratio=0.2, test_ratio=0.6, seed=7)
    split_counts = summarize_buckets(assigned)["split_distribution"]

    assert split_counts["public_dev"] == 2
    assert split_counts["public_test"] == 6
    assert split_counts["holdout"] == 2


def test_apply_bucket_quotas_caps_each_bucket():
    records = [
        {"id": "1", "benchmark_bucket": "real_user", "prompt": "a"},
        {"id": "2", "benchmark_bucket": "real_user", "prompt": "b"},
        {"id": "3", "benchmark_bucket": "real_user", "prompt": "c"},
        {"id": "4", "benchmark_bucket": "safety", "prompt": "d"},
        {"id": "5", "benchmark_bucket": "safety", "prompt": "e"},
    ]

    selected = apply_bucket_quotas(records, {"real_user": 2, "safety": 1})
    summary = summarize_buckets(selected)

    assert summary["bucket_distribution"]["real_user"] == 2
    assert summary["bucket_distribution"]["safety"] == 1
