"""
Benchmark Runner - Evaluate PromptOptimizer Pro across strategies

Runs the benchmark dataset through analyze -> optimize pipeline
for each strategy and reports comparative results.

Usage:
    python scripts/run_benchmark.py
    python scripts/run_benchmark.py --strategies standard,shdt
    python scripts/run_benchmark.py --limit 10
"""

import asyncio
import json
import os
import sys
import time
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.agent_orchestrator import get_orchestrator
from backend.services.optimizer_service import get_optimizer
from backend.services.db_service import save_benchmark_result, get_benchmark_summary


BENCHMARK_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "benchmarks", "prompts.json"
)


def load_benchmarks(limit=None):
    """Load benchmark prompts from JSON file"""
    with open(BENCHMARK_FILE, "r") as f:
        prompts = json.load(f)
    if limit:
        prompts = prompts[:limit]
    return prompts


async def run_single_benchmark(prompt_data, strategy="standard"):
    """Run a single benchmark prompt through the optimization pipeline"""
    orchestrator = get_orchestrator()
    optimizer = get_optimizer()

    context = {
        "task_type": prompt_data.get("task_type", "general"),
        "domain": prompt_data.get("domain", "general")
    }

    result = {
        "benchmark_id": prompt_data["id"],
        "prompt": prompt_data["prompt"][:100],
        "strategy": strategy,
        "category": prompt_data.get("category", "general"),
        "human_score": prompt_data.get("human_score", 5.0)
    }

    start_time = time.time()

    try:
        # Step 1: Analyze
        analysis = await orchestrator.analyze_with_agents(
            prompt_data["prompt"], context
        )
        result["score_before"] = analysis["overall_score"]
        result["defects_found"] = len(analysis.get("defects", []))

        # Step 2: Optimize based on strategy
        if strategy == "standard":
            opt_result = await optimizer.optimize(
                prompt=prompt_data["prompt"],
                context=context,
                optimization_level="balanced",
                analysis=analysis
            )
            result["score_after"] = opt_result["after_analysis"]["overall_score"]
            result["optimized_prompt"] = opt_result["optimized_prompt"][:100]
            defects_after = len(opt_result["after_analysis"].get("defects", []))

        elif strategy == "shdt":
            # Use SHDT iterative optimization (will be available after Phase B)
            if hasattr(optimizer, "optimize_with_trajectory"):
                opt_result = await optimizer.optimize_with_trajectory(
                    prompt=prompt_data["prompt"],
                    context=context,
                    analysis=analysis
                )
                result["score_after"] = opt_result.get("final_score", analysis["overall_score"])
                result["optimized_prompt"] = opt_result.get("final_prompt", prompt_data["prompt"])[:100]
                defects_after = len(opt_result.get("defects_after", []))
            else:
                # Fallback to standard if SHDT not yet implemented
                opt_result = await optimizer.optimize(
                    prompt=prompt_data["prompt"], context=context,
                    optimization_level="balanced", analysis=analysis
                )
                result["score_after"] = opt_result["after_analysis"]["overall_score"]
                defects_after = len(opt_result["after_analysis"].get("defects", []))

        elif strategy == "cdraf":
            # Use CDRAF refinement (will be available after Phase B)
            if hasattr(optimizer, "refine_with_agents"):
                opt_result = await optimizer.optimize(
                    prompt=prompt_data["prompt"], context=context,
                    optimization_level="balanced", analysis=analysis
                )
                refined = await optimizer.refine_with_agents(
                    optimized_prompt=opt_result["optimized_prompt"],
                    context=context
                )
                result["score_after"] = refined.get("final_score", opt_result["after_analysis"]["overall_score"])
                defects_after = len(refined.get("defects_after", []))
            else:
                opt_result = await optimizer.optimize(
                    prompt=prompt_data["prompt"], context=context,
                    optimization_level="balanced", analysis=analysis
                )
                result["score_after"] = opt_result["after_analysis"]["overall_score"]
                defects_after = len(opt_result["after_analysis"].get("defects", []))

        elif strategy == "dgeo":
            # Use DGEO evolutionary optimization (will be available after Phase B)
            try:
                from backend.services.dgeo_optimizer import DGEOOptimizer
                dgeo = DGEOOptimizer()
                opt_result = await dgeo.optimize(
                    prompt=prompt_data["prompt"],
                    context=context,
                    analysis=analysis
                )
                result["score_after"] = opt_result.get("best_score", analysis["overall_score"])
                defects_after = len(opt_result.get("defects_after", []))
            except ImportError:
                opt_result = await optimizer.optimize(
                    prompt=prompt_data["prompt"], context=context,
                    optimization_level="balanced", analysis=analysis
                )
                result["score_after"] = opt_result["after_analysis"]["overall_score"]
                defects_after = len(opt_result["after_analysis"].get("defects", []))
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        elapsed_ms = int((time.time() - start_time) * 1000)
        result["improvement"] = round(result["score_after"] - result["score_before"], 2)
        result["defects_fixed"] = max(0, result["defects_found"] - defects_after)
        result["processing_time_ms"] = elapsed_ms
        result["status"] = "success"

        # Save to database
        save_benchmark_result(
            benchmark_id=prompt_data["id"],
            strategy=strategy,
            score_before=result["score_before"],
            score_after=result["score_after"],
            defects_fixed=result["defects_fixed"],
            processing_time_ms=elapsed_ms
        )

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        result["status"] = "error"
        result["error"] = str(e)
        result["processing_time_ms"] = elapsed_ms
        result["score_before"] = 0
        result["score_after"] = 0
        result["improvement"] = 0
        result["defects_fixed"] = 0

    return result


async def run_benchmarks(strategies=None, limit=None):
    """Run full benchmark suite"""
    if strategies is None:
        strategies = ["standard"]

    benchmarks = load_benchmarks(limit)
    print(f"\n{'='*70}")
    print(f"  PromptOptimizer Pro - Benchmark Suite")
    print(f"  {len(benchmarks)} prompts x {len(strategies)} strategies = {len(benchmarks) * len(strategies)} runs")
    print(f"  Strategies: {', '.join(strategies)}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    all_results = {}
    for strategy in strategies:
        print(f"\n--- Strategy: {strategy.upper()} ---\n")
        results = []

        for i, prompt_data in enumerate(benchmarks):
            print(f"  [{i+1}/{len(benchmarks)}] {prompt_data['id']}: {prompt_data['prompt'][:50]}...", end=" ")
            sys.stdout.flush()

            result = await run_single_benchmark(prompt_data, strategy)
            results.append(result)

            if result["status"] == "success":
                print(f"-> {result['score_before']:.1f} -> {result['score_after']:.1f} "
                      f"(+{result['improvement']:.1f}) [{result['processing_time_ms']}ms]")
            else:
                print(f"-> ERROR: {result.get('error', 'Unknown')[:50]}")

        all_results[strategy] = results

    # Print summary
    print(f"\n{'='*70}")
    print(f"  BENCHMARK RESULTS SUMMARY")
    print(f"{'='*70}\n")

    for strategy, results in all_results.items():
        successful = [r for r in results if r["status"] == "success"]
        if not successful:
            print(f"  {strategy.upper()}: All failed")
            continue

        avg_improvement = sum(r["improvement"] for r in successful) / len(successful)
        avg_score_after = sum(r["score_after"] for r in successful) / len(successful)
        avg_time = sum(r["processing_time_ms"] for r in successful) / len(successful)
        total_defects_fixed = sum(r["defects_fixed"] for r in successful)

        print(f"  {strategy.upper()}:")
        print(f"    Successful:        {len(successful)}/{len(results)}")
        print(f"    Avg Improvement:   +{avg_improvement:.2f}")
        print(f"    Avg Final Score:   {avg_score_after:.2f}")
        print(f"    Total Defects Fixed: {total_defects_fixed}")
        print(f"    Avg Time:          {avg_time:.0f}ms")
        print()

    # By category breakdown
    print(f"  BY CATEGORY (standard strategy):")
    if "standard" in all_results:
        categories = {}
        for r in all_results["standard"]:
            if r["status"] == "success":
                cat = r.get("category", "general")
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(r["improvement"])

        for cat, improvements in sorted(categories.items()):
            avg = sum(improvements) / len(improvements)
            print(f"    {cat:25s}: avg +{avg:.2f} ({len(improvements)} prompts)")

    # Save results to file
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "benchmarks", "results.json"
    )
    with open(output_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "strategies": strategies,
            "num_prompts": len(benchmarks),
            "results": all_results,
            "summary": get_benchmark_summary()
        }, f, indent=2)

    print(f"\n  Results saved to: {output_path}")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Run PromptOptimizer Pro benchmarks")
    parser.add_argument(
        "--strategies",
        default="standard",
        help="Comma-separated list of strategies: standard,shdt,cdraf,dgeo"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of benchmark prompts to run"
    )
    args = parser.parse_args()

    strategies = [s.strip() for s in args.strategies.split(",")]
    asyncio.run(run_benchmarks(strategies=strategies, limit=args.limit))


if __name__ == "__main__":
    main()
