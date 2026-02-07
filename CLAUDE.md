# Instructions for Claude Code - PromptOptimizer Pro

## Project Context

You are working on **PromptOptimizer Pro**, a final year engineering project that implements automated prompt engineering using multi-agent defect detection. This project is based on a published research survey (Nagpure et al., 2025, IJFMR).

**Current Progress: ~80-85% Complete**

---

## What's Already Done

### **Configuration Layer** (Complete)
- `.env.example` - Environment template
- `.env` - Actual config (needs API keys)
- `backend/config.py` - All settings, enums, model registry
- `backend/requirements.txt` - Dependencies

### **Utilities Layer** (Complete)
- `backend/utils/__init__.py` - Package exports
- `backend/utils/logger.py` - Structured logging
- `backend/utils/validators.py` - Input validation
- `backend/utils/token_counter.py` - Tiktoken integration
- `backend/utils/response_parser.py` - JSON parsing from LLM
- `backend/utils/error_handlers.py` - Custom exceptions

### **Models Layer** (Complete)
- `backend/models/__init__.py` - Package exports
- `backend/models/defect_taxonomy.py` - **28 defects** from Tian et al.
- `backend/models/technique_registry.py` - **41+ prompt engineering techniques**
- `backend/models/request_models.py` - Pydantic request models
- `backend/models/response_models.py` - Pydantic response models

### **Agents Layer** (Complete)
- `backend/agents/__init__.py` - Package exports
- `backend/agents/base_agent.py` - Abstract base class for all agents
- `backend/agents/clarity_agent.py` - D001-D004 (Specification & Intent)
- `backend/agents/structure_agent.py` - D005-D009 (Structure & Formatting)
- `backend/agents/context_agent.py` - D010-D014 (Context & Memory)
- `backend/agents/security_agent.py` - D023-D028 (Security & Safety)

### **Services Layer** (Complete)
- `backend/services/__init__.py` - Service exports
- `backend/services/llm_service.py` - Anthropic Claude + Groq abstraction
- `backend/services/agent_orchestrator.py` - **Core innovation**: parallel agent execution with consensus
- `backend/services/optimizer_service.py` - Prompt optimization logic
- `backend/services/analyzer_service.py` - High-level analysis orchestration
- `backend/services/evaluator_service.py` - Evaluate optimization effectiveness
- `backend/services/tester_service.py` - A/B testing original vs optimized prompts

### **Prompts Layer** (Partially Complete)
- `backend/prompts/__init__.py` - Package initializer
- `backend/prompts/agents_prompts.py` - Meta-prompts for all 4 agents (complete)

### **Application Layer** (Working)
- `backend/app.py` - Flask REST API
- `backend/routes/` - Route definitions
- `cli.py` - Command line interface
- `demo.py` - Demo script

---

## Architecture (Implemented)

```
User Prompt
    |
AgentOrchestrator
    |
[Parallel Execution]
    |
+-- ClarityAgent --> LLM --> D001-D004 defects
+-- StructureAgent --> LLM --> D005-D009 defects
+-- ContextAgent --> LLM --> D010-D014 defects
+-- SecurityAgent --> LLM --> D023-D028 defects
    |
Consensus Mechanism (voting + aggregation)
    |
Unified Analysis Result
```

---

## Working Example

The multi-agent system is functional. You can use it like this:

```python
from backend.services.agent_orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
result = await orchestrator.analyze_with_agents(
    prompt="Write a function to sort numbers",
    context={"task_type": "code_generation"}
)

print(result["overall_score"])  # e.g., 6.5
print(result["defects"])        # List of detected defects
print(result["consensus"])      # e.g., 0.85
```

---

## Remaining Work

### Empty Prompt Files (0 bytes - need implementation)
- `backend/prompts/analysis_prompts.py` - Prompts for overall analysis
- `backend/prompts/optimization_prompts.py` - Prompts for generating optimizations

### Integration Work
- Frontend integration (React frontend exists in `frontend/`)
- End-to-end testing of full pipeline
- API route completeness

---

## Implementation Guidelines

### Use Existing Code
- Import from `utils` for logging, validation, parsing
- Use `llm_service.call()` for all LLM interactions
- Use `Config` for all settings
- Raise custom exceptions from `error_handlers`

### Coding Standards
```python
# Always include docstrings
def function_name(param: str) -> Dict:
    """
    Brief description

    Args:
        param: Description

    Returns:
        Description of return value
    """
    pass

# Use type hints everywhere
# Use dataclasses for data structures
# Use enums for fixed sets of values
# Log all important operations
```

---

## Important Notes

1. **NO Redis** - Don't implement any caching with Redis
2. **API Keys** - Use from Config, don't hardcode
3. **Error Handling** - Use existing custom exceptions
4. **Logging** - Use get_logger() for all logging
5. **Token Limits** - Check with token_counter before LLM calls
6. **Async Support** - Use asyncio for parallel agent execution

---

## Reference Files

Key files to review:
- `backend/config.py` - See AGENT_TYPES configuration
- `backend/models/defect_taxonomy.py` - All 28 defects defined
- `backend/models/technique_registry.py` - All 41+ techniques defined
- `backend/services/llm_service.py` - How to call LLM
- `backend/services/agent_orchestrator.py` - Multi-agent coordination
- `backend/services/analyzer_service.py` - High-level analysis API
- `backend/services/optimizer_service.py` - Prompt optimization
- `backend/services/evaluator_service.py` - Optimization evaluation
- `backend/services/tester_service.py` - A/B testing
- `backend/agents/base_agent.py` - Agent architecture
- `backend/utils/` - All utility functions available
