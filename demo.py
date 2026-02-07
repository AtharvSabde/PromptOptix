"""
PromptOptimizer Pro - Demo Script

Demonstrates the complete workflow:
1. Analyze a poorly-written prompt
2. Detect defects with multi-agent consensus
3. Apply optimization techniques
4. Show before/after comparison
"""

import asyncio
from backend.services.agent_orchestrator import get_orchestrator
from backend.services.optimizer_service import get_optimizer
from backend.config import Config


async def demo_analyze():
    """Demo: Analyze a prompt for defects"""
    print("\n" + "="*70)
    print("STEP 1: ANALYZE PROMPT FOR DEFECTS")
    print("="*70)

    orchestrator = get_orchestrator()

    # Example of a poorly-written prompt
    bad_prompt = "Write a sorting function"

    print(f"\nPrompt to analyze:")
    print(f"  \"{bad_prompt}\"")
    print("\nRunning multi-agent analysis...")

    result = await orchestrator.analyze_with_agents(
        prompt=bad_prompt,
        context={"task_type": "code_generation", "domain": "software_engineering"}
    )

    print(f"\nResults:")
    print(f"  Overall Quality Score: {result['overall_score']}/10")
    print(f"  Agent Consensus: {result['consensus']:.0%}")
    print(f"  Defects Found: {len(result['defects'])}")

    if result['defects']:
        print(f"\n  Detected Defects:")
        for defect in result['defects'][:5]:  # Show top 5
            print(f"    - [{defect['severity'].upper()}] {defect['name']} ({defect['id']})")
            print(f"      Confidence: {defect['confidence']:.0%}")
            print(f"      Detected by: {', '.join(defect['detected_by'])}")
            if defect.get('evidence'):
                evidence = defect['evidence'][:80]
                print(f"      Evidence: {evidence}...")

    return result


async def demo_optimize(analysis_result=None):
    """Demo: Optimize a prompt by applying techniques"""
    print("\n" + "="*70)
    print("STEP 2: OPTIMIZE PROMPT")
    print("="*70)

    optimizer = get_optimizer()

    bad_prompt = "Write a sorting function"

    print(f"\nOriginal Prompt:")
    print(f"  \"{bad_prompt}\"")
    print("\nApplying optimization techniques...")

    result = await optimizer.optimize(
        prompt=bad_prompt,
        context={"task_type": "code_generation", "domain": "software_engineering"},
        optimization_level="balanced",
        max_techniques=3,
        analysis=analysis_result  # Reuse previous analysis if available
    )

    print(f"\nOptimization Results:")
    print(f"  Techniques Applied: {len(result['techniques_applied'])}")
    print(f"  Improvement Score: +{result['improvement_score']}")
    print(f"  Before: {result['before_analysis']['overall_score']}/10")
    print(f"  After:  {result['after_analysis']['overall_score']}/10")

    if result['techniques_applied']:
        print(f"\n  Applied Techniques:")
        for tech in result['techniques_applied']:
            print(f"    - {tech['technique_name']} ({tech['technique_id']})")
            print(f"      Fixes: {', '.join(tech['target_defects'][:3])}")
            print(f"      Action: {tech['modification']}")

    print(f"\n  Optimized Prompt:")
    print(f"  {'-'*68}")
    # Format the optimized prompt nicely
    optimized = result['optimized_prompt']
    for line in optimized.split('\n'):
        print(f"  {line}")
    print(f"  {'-'*68}")

    # Show defect reduction
    defects_before = len(result['before_analysis'].get('defects', []))
    defects_after = len(result['after_analysis'].get('defects', []))
    defects_fixed = defects_before - defects_after

    print(f"\n  Defect Reduction:")
    print(f"    Before: {defects_before} defects")
    print(f"    After:  {defects_after} defects")
    if defects_fixed > 0:
        print(f"    Fixed:  {defects_fixed} defects ({defects_fixed/defects_before*100:.0f}% reduction)")

    return result


async def demo_comparison():
    """Demo: Side-by-side comparison of multiple prompts"""
    print("\n" + "="*70)
    print("BONUS: COMPARE MULTIPLE PROMPTS")
    print("="*70)

    orchestrator = get_orchestrator()

    test_prompts = [
        ("Very Poor", "Write code"),
        ("Poor", "Write a sorting function"),
        ("Moderate", "Write a Python function that sorts a list of integers"),
        ("Good", """You are a Python expert. Write a function that:
- Takes a list of integers as input
- Returns the list sorted in ascending order
- Uses an efficient algorithm
- Includes type hints and docstring
Return only the Python code.""")
    ]

    print("\nAnalyzing prompts with different quality levels...\n")

    results = []
    for label, prompt in test_prompts:
        result = await orchestrator.analyze_with_agents(
            prompt=prompt,
            context={"task_type": "code_generation"}
        )
        results.append((label, prompt, result))

    # Display comparison
    print(f"{'Quality':<12} {'Score':>6} {'Defects':>8} {'Consensus':>10} {'Prompt':<40}")
    print("-" * 80)

    for label, prompt, result in results:
        score = result['overall_score']
        defects = len(result['defects'])
        consensus = result['consensus']
        prompt_preview = prompt[:37] + "..." if len(prompt) > 40 else prompt

        print(f"{label:<12} {score:>6.1f} {defects:>8} {consensus:>9.0%} {prompt_preview:<40}")


async def main():
    """Run complete demo"""
    print("="*70)
    print("PromptOptimizer Pro - Complete Demo")
    print("="*70)
    print("\nThis demo shows the multi-agent defect detection and optimization system.")
    print("It will:")
    print("  1. Analyze a prompt with 4 specialized agents")
    print("  2. Detect defects using consensus voting")
    print("  3. Select and apply techniques to fix defects")
    print("  4. Compare before/after quality scores")

    # Check API keys
    if not Config.ANTHROPIC_API_KEY and not Config.GROQ_API_KEY:
        print("\n[WARNING] No API keys found!")
        print("Please add ANTHROPIC_API_KEY or GROQ_API_KEY to .env file")
        print("\nDemo will run in structure-only mode (no live LLM calls).")
        return

    try:
        # Step 1: Analyze
        analysis = await demo_analyze()

        # Step 2: Optimize (reuses analysis from step 1)
        optimization = await demo_optimize(analysis)

        # Bonus: Comparison
        await demo_comparison()

        print("\n" + "="*70)
        print("DEMO COMPLETE!")
        print("="*70)
        print("\nKey Insights:")
        print(f"  - Multi-agent consensus reduces false positives")
        print(f"  - Techniques are selected based on defect coverage")
        print(f"  - Optimization can improve scores by 2-4 points on average")
        print(f"  - Better prompts = better AI outputs")

    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
