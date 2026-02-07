"""
Simple test to verify multi-agent system is working
"""

def main():
    print("=" * 60)
    print("PromptOptimizer Pro - Simple System Check")
    print("=" * 60)

    # Test 1: Import technique registry
    print("\n1. Testing Technique Registry...")
    try:
        from backend.models import TECHNIQUE_REGISTRY, get_techniques_for_defect
        print(f"   [OK] Loaded {len(TECHNIQUE_REGISTRY)} techniques")

        techniques = get_techniques_for_defect("D001")
        print(f"   [OK] Found {len(techniques)} techniques for D001")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False

    # Test 2: Import defect taxonomy
    print("\n2. Testing Defect Taxonomy...")
    try:
        from backend.models import DEFECT_TAXONOMY, get_defect_by_id
        print(f"   [OK] Loaded {len(DEFECT_TAXONOMY)} defects")

        defect = get_defect_by_id("D001")
        print(f"   [OK] D001: {defect.name}")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False

    # Test 3: Import agent classes (but don't instantiate without API keys)
    print("\n3. Testing Agent Imports...")
    try:
        from backend.agents.clarity_agent import ClarityAgent
        from backend.agents.structure_agent import StructureAgent
        from backend.agents.context_agent import ContextAgent
        from backend.agents.security_agent import SecurityAgent
        print("   [OK] All agent classes imported successfully")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False

    # Test 4: Check agent prompts
    print("\n4. Testing Agent Prompts...")
    try:
        from backend.prompts.agents_prompts import (
            get_clarity_agent_prompt,
            get_structure_agent_prompt,
            get_context_agent_prompt,
            get_security_agent_prompt
        )

        test_prompt = "Write code"
        clarity_prompt = get_clarity_agent_prompt(test_prompt)
        print(f"   [OK] Generated meta-prompt ({len(clarity_prompt)} chars)")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False

    # Test 5: Check models
    print("\n5. Testing Request/Response Models...")
    try:
        from backend.models import AnalyzeRequest, AnalysisResponse

        request = AnalyzeRequest(
            prompt="Write a function to sort numbers",
            task_type="code_generation"
        )
        print(f"   [OK] Created AnalyzeRequest: '{request.prompt[:30]}...'")
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False

    print("\n" + "=" * 60)
    print("[SUCCESS] All core components are working!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Add ANTHROPIC_API_KEY or GROQ_API_KEY to .env file")
    print("2. Then you can run live analysis with the orchestrator")
    print("\nThe multi-agent system is ready to use!")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
