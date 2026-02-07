"""
Test script for OptimizerService

Tests the optimizer service that applies techniques to fix prompt defects.
"""

import asyncio
import sys


def test_imports():
    """Test that optimizer components can be imported"""
    print("Testing optimizer imports...")

    try:
        from backend.services.optimizer_service import OptimizerService, get_optimizer
        from backend.models import get_techniques_for_defect, TechniqueCategory
        print("  [OK] Optimizer service imports successful")
        return True
    except ImportError as e:
        print(f"  [FAIL] Import failed: {e}")
        return False


def test_instantiation():
    """Test that optimizer can be instantiated"""
    print("\nTesting optimizer instantiation...")

    try:
        from backend.services.optimizer_service import get_optimizer

        optimizer = get_optimizer()
        print(f"  [OK] Created optimizer instance: {optimizer.__class__.__name__}")
        print(f"  [OK] Optimizer has orchestrator: {optimizer.orchestrator is not None}")
        return True
    except Exception as e:
        print(f"  [FAIL] Instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_technique_selection():
    """Test technique selection logic"""
    print("\nTesting technique selection...")

    try:
        from backend.services.optimizer_service import get_optimizer

        optimizer = get_optimizer()

        # Create mock defects
        mock_defects = [
            {"id": "D001", "name": "Ambiguity", "severity": "high"},
            {"id": "D002", "name": "Underspecification", "severity": "high"}
        ]

        # Test technique selection
        selected = optimizer._select_techniques(
            defects=mock_defects,
            optimization_level="balanced",
            max_techniques=5
        )

        print(f"  [OK] Selected {len(selected)} techniques for {len(mock_defects)} defects")

        if selected:
            for i, tech in enumerate(selected[:3], 1):
                print(f"    {i}. {tech.name} ({tech.id}) - effectiveness: {tech.effectiveness_score}")

        return True
    except Exception as e:
        print(f"  [FAIL] Technique selection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_technique_application():
    """Test that techniques can be applied to prompts"""
    print("\nTesting technique application...")

    try:
        from backend.services.optimizer_service import get_optimizer
        from backend.models import get_technique_by_id

        optimizer = get_optimizer()

        # Get a technique to test
        technique = get_technique_by_id("T001")  # Role Prompting
        if not technique:
            print("  [WARN] Technique T001 not found, skipping test")
            return True

        # Test prompt
        test_prompt = "Write a function to sort numbers"
        context = {"task_type": "code_generation", "domain": "software_engineering"}
        mock_defects = [{"id": "D002", "name": "Underspecification"}]

        # Apply technique
        modified, description = optimizer._apply_technique(
            prompt=test_prompt,
            technique=technique,
            context=context,
            defects=mock_defects
        )

        print(f"  [OK] Applied technique: {technique.name}")
        print(f"  [OK] Modification: {description}")
        print(f"  Original: {test_prompt}")
        print(f"  Modified: {modified[:100]}...")

        return True
    except Exception as e:
        print(f"  [FAIL] Technique application failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_optimization():
    """Test full optimization flow (requires API keys)"""
    print("\nTesting full optimization (requires API keys)...")

    try:
        from backend.services.optimizer_service import get_optimizer
        from backend.config import Config

        # Check if API keys are configured
        if not Config.ANTHROPIC_API_KEY and not Config.GROQ_API_KEY:
            print("  [WARN] No API keys configured - skipping live optimization test")
            print("    To test optimization, add ANTHROPIC_API_KEY or GROQ_API_KEY to .env")
            return True

        optimizer = get_optimizer()

        # Test with a known defective prompt
        test_prompt = "Write code"
        context = {"task_type": "code_generation", "domain": "software_engineering"}

        print(f"\n  Optimizing prompt: '{test_prompt}'")
        print("  This will:")
        print("    1. Analyze the prompt with multi-agent system")
        print("    2. Select techniques to fix defects")
        print("    3. Apply techniques sequentially")
        print("    4. Re-analyze to verify improvement")

        # Run optimization
        result = await optimizer.optimize(
            prompt=test_prompt,
            context=context,
            optimization_level="balanced",
            max_techniques=3
        )

        # Display results
        print(f"\n  [OK] Optimization complete!")
        print(f"    Original Score: {result['before_analysis']['overall_score']}/10")
        print(f"    Optimized Score: {result['after_analysis']['overall_score']}/10")
        print(f"    Improvement: +{result['improvement_score']}")
        print(f"    Techniques Applied: {len(result['techniques_applied'])}")

        if result['techniques_applied']:
            print("\n    Applied Techniques:")
            for tech in result['techniques_applied']:
                print(f"      - {tech['technique_name']}: {tech['modification']}")

        print(f"\n    Original Prompt:")
        print(f"      {result['original_prompt']}")
        print(f"\n    Optimized Prompt:")
        print(f"      {result['optimized_prompt'][:200]}...")

        return True

    except Exception as e:
        print(f"  [FAIL] Full optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("PromptOptimizer Pro - Optimizer Service Test")
    print("=" * 60)

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: Instantiation
    results.append(("Instantiation", test_instantiation()))

    # Test 3: Technique Selection
    results.append(("Technique Selection", test_technique_selection()))

    # Test 4: Technique Application
    results.append(("Technique Application", test_technique_application()))

    # Test 5: Full Optimization (if API keys available)
    results.append(("Full Optimization", await test_full_optimization()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{test_name:.<40} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All optimizer tests passed!")
        return 0
    else:
        print("\n[WARN] Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
