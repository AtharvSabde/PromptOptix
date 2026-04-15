from backend.evaluation import get_comparison_engine, get_quality_scorer
from backend.utils.response_parser import safe_json_parse


def test_trial_summary_aggregates_repeated_runs():
    engine = get_comparison_engine(seed=123)
    summary = engine.summarize_trials(
        [
            {"status": "success", "score_after": 7.0, "defects_after": 3, "high_severity_after": 1, "processing_time_ms": 1000, "cost_after": 0.01},
            {"status": "success", "score_after": 8.0, "defects_after": 2, "high_severity_after": 1, "processing_time_ms": 1200, "cost_after": 0.02},
            {"status": "error", "error": "transient"},
        ],
        baseline_score=5.0,
    )

    assert summary["status"] == "success"
    assert summary["num_trials"] == 3
    assert summary["successful_trials"] == 2
    assert summary["score_after"] == 7.5
    assert summary["improvement_mean"] == 2.5
    assert summary["trial_success_rate"] == 0.667


def test_pairwise_strategy_comparison_builds_corrected_pvalues():
    engine = get_comparison_engine(seed=123)
    results = [
        {
            "baseline": {"score": 5.0},
            "strategies": {
                "a": {"status": "success", "improvement_mean": 2.0},
                "b": {"status": "success", "improvement_mean": 1.0},
                "c": {"status": "success", "improvement_mean": 0.5},
            },
        },
        {
            "baseline": {"score": 4.0},
            "strategies": {
                "a": {"status": "success", "improvement_mean": 1.5},
                "b": {"status": "success", "improvement_mean": 1.0},
                "c": {"status": "success", "improvement_mean": 0.0},
            },
        },
    ]

    pairwise = engine.pairwise_strategy_comparisons(results, ["a", "b", "c"])
    assert len(pairwise) == 3
    assert all(item.p_value_corrected is not None for item in pairwise)


def test_quality_scorer_alignment_summary():
    scorer = get_quality_scorer()
    summary = scorer.summarize_alignment(
        [
            {
                "expected_defects": ["D001", "D002"],
                "baseline": {"detected_defect_ids": ["D001", "D003"]},
            },
            {
                "expected_defects": ["D004"],
                "baseline": {"detected_defect_ids": ["D004"]},
            },
        ]
    )

    assert summary["macro_precision"] >= 0
    assert summary["macro_recall"] >= 0
    assert summary["micro_f1"] >= 0


def test_safe_json_parse_unwraps_escaped_json_string():
    text = r'"\n{\n  \"function_name\": \"demo\",\n  \"language\": \"Ruby\",\n  \"code_block\": \"puts 1\"\n}\n"'
    parsed = safe_json_parse(text)

    assert parsed["function_name"] == "demo"
    assert parsed["language"] == "Ruby"


def test_safe_json_parse_removes_stray_scalar_between_fields():
    text = """{
      "defects": [
        {
          "id": "D002",
          "confidence": 0.9,
          "evidence": "The function must accept one argument: an array.",2222
          "explanation": "The prompt is underspecified."
        }
      ],
      "overall_score": 5.0
    }"""
    parsed = safe_json_parse(text)

    assert parsed["defects"][0]["id"] == "D002"
    assert parsed["overall_score"] == 5.0
