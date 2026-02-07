"""
Quick test script for the multi-agent defect detection system

Tests:
1. Can import all components
2. Can instantiate orchestrator
3. Can run simple analysis (requires API keys)
"""

import asyncio
import sys


def test_imports():
    """Test that all components can be imported"""
    print("Testing imports...")

    try:
        # Test models
        from backend.models import (
            DefectCategory, DefectSeverity, DEFECT_TAXONOMY,
            TechniqueCategory, TECHNIQUE_REGISTRY,
            AnalyzeRequest, AnalysisResponse
        )
        print("[OK] Models imported successfully")

        # Test agents
        from backend.agents import (
            BaseAgent, ClarityAgent, StructureAgent,
            ContextAgent, SecurityAgent
        )
        print("[OK] Agents imported successfully")

        # Test services
        from backend.services import get_orchestrator, get_llm_service
        print("[OK] Services imported successfully")

        # Test prompts
        from backend.prompts.agents_prompts import (
            get_clarity_agent_prompt,
            get_structure_agent_prompt,
            get_context_agent_prompt,
            get_security_agent_prompt
        )
        print("[OK] Prompts imported successfully")

        return True

    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_instantiation():
    """Test that agents and orchestrator can be instantiated"""
    print("\nTesting instantiation...")

    try:
        from backend.agents import (
            ClarityAgent, StructureAgent, ContextAgent, SecurityAgent
        )
        from backend.services import get_orchestrator

        # Create agents
        agents = [
            ClarityAgent(),
            StructureAgent(),
            ContextAgent(),
            SecurityAgent()
        ]
        print(f"[OK] Created {len(agents)} agents")

        # Create orchestrator
        orchestrator = get_orchestrator()
        print(f"[OK] Created orchestrator with {len(orchestrator.agents)} agents")

        return True

    except Exception as e:
        print(f"[FAIL] Instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_technique_registry():
    """Test technique registry"""
    print("\nTesting technique registry...")

    try:
        from backend.models import TECHNIQUE_REGISTRY, get_techniques_for_defect

        print(f"[OK] Loaded {len(TECHNIQUE_REGISTRY)} techniques")

        # Test getting techniques for a specific defect
        techniques_for_d001 = get_techniques_for_defect("D001")
        print(f"[OK] Found {len(techniques_for_d001)} techniques for D001 (Ambiguity)")

        if techniques_for_d001:
            top_technique = techniques_for_d001[0]
            print(f"  Top technique: {top_technique.name} (effectiveness: {top_technique.effectiveness_score})")

        return True

    except Exception as e:
        print(f"[FAIL] Technique registry test failed: {e}")
        return False


async def test_analysis():
    """Test running actual analysis (requires API keys)"""
    print("\nTesting analysis (requires API keys)...")

    try:
        from backend.services import get_orchestrator
        from backend.config import Config

        # Check if API keys are configured
        if not Config.ANTHROPIC_API_KEY and not Config.GROQ_API_KEY:
            print("[WARN] No API keys configured - skipping live analysis test")
            print("  To test analysis, add ANTHROPIC_API_KEY or GROQ_API_KEY to .env")
            return True

        # Create orchestrator
        orchestrator = get_orchestrator()

        # Test with a known defective prompt
        test_prompt = "Write a function to sort numbers"
        print(f"\nAnalyzing prompt: '{test_prompt}'")
        print("Expected defects: D002 (Underspecification), possibly D001 (Ambiguity)")

        # Run analysis
        result = await orchestrator.analyze_with_agents(
            prompt=test_prompt,
            context={"task_type": "code_generation", "domain": "software_engineering"}
        )

        # Display results
        print(f"\n[OK] Analysis complete!")
        print(f"  Overall Score: {result['overall_score']}/10")
        print(f"  Consensus: {result['consensus']}")
        print(f"  Defects Found: {len(result['defects'])}")

        if result['defects']:
            print("\n  Detected Defects:")
            for defect in result['defects']:
                print(f"    [{defect['severity'].upper()}] {defect['name']} ({defect['id']})")
                print(f"      Confidence: {defect['confidence']:.2f}")
                print(f"      Detected by: {', '.join(defect['detected_by'])}")
                print(f"      Evidence: {defect['evidence'][:100]}...")
        else:
            print("  No defects found (this is unexpected for the test prompt)")

        return True

    except Exception as e:
        print(f"[FAIL] Analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("PromptOptimizer Pro - Multi-Agent System Test")
    print("=" * 60)

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: Instantiation
    results.append(("Instantiation", test_instantiation()))

    # Test 3: Technique Registry
    results.append(("Technique Registry", test_technique_registry()))

    # Test 4: Live Analysis (if API keys available)
    results.append(("Live Analysis", await test_analysis()))

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
        print("\n[SUCCESS] All tests passed! Multi-agent system is ready to use.")
        return 0
    else:
        print("\n[WARN] Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
