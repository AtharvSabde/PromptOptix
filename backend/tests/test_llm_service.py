from backend.services.llm_service import LLMService


def test_call_with_json_response_uses_repair_before_default():
    service = LLMService.__new__(LLMService)

    calls = {"count": 0}

    def fake_call(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return {
                "provider": "gemini",
                "model": "gemini-2.5-pro",
                "response": '{"optimized_prompt": "broken',
                "usage": {},
                "cost": {}
            }
        return {
            "provider": "gemini",
            "model": "gemini-2.5-pro",
            "response": '{"optimized_prompt": "fixed by repair", "changes_made": []}',
            "usage": {},
            "cost": {}
        }

    service.call = fake_call
    service._repair_json_response = LLMService._repair_json_response.__get__(service, LLMService)
    service._regenerate_json_response = LLMService._regenerate_json_response.__get__(service, LLMService)
    service._apply_field_defaults = LLMService._apply_field_defaults.__get__(service, LLMService)

    result = service.call_with_json_response(
        prompt="Rewrite this prompt",
        system_prompt="Return JSON",
        provider="gemini",
        required_fields=["optimized_prompt"],
        default={"optimized_prompt": "fallback", "changes_made": []},
        field_defaults={"changes_made": []}
    )

    assert result["parsed_response"]["optimized_prompt"] == "fixed by repair"
    assert calls["count"] == 2


def test_call_with_json_response_uses_default_after_repair_and_regen_fail():
    service = LLMService.__new__(LLMService)

    def fake_call(*args, **kwargs):
        return {
            "provider": "gemini",
            "model": "gemini-2.5-pro",
            "response": '{"optimized_prompt": "broken',
            "usage": {},
            "cost": {}
        }

    def fail_repair(*args, **kwargs):
        raise ValueError("repair failed")

    def fail_regen(*args, **kwargs):
        raise ValueError("regen failed")

    service.call = fake_call
    service._repair_json_response = fail_repair
    service._regenerate_json_response = fail_regen
    service._apply_field_defaults = LLMService._apply_field_defaults.__get__(service, LLMService)

    result = service.call_with_json_response(
        prompt="Rewrite this prompt",
        system_prompt="Return JSON",
        provider="gemini",
        required_fields=["optimized_prompt"],
        default={"optimized_prompt": "fallback", "changes_made": []},
        field_defaults={"changes_made": []}
    )

    assert result["parsed_response"]["optimized_prompt"] == "fallback"
