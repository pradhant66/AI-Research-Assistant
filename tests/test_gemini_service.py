"""Test evidence selection and SDK handling, not model factual accuracy."""

from types import SimpleNamespace
import builtins
import re
from unittest.mock import Mock

import pytest

import gemini_service as service


@pytest.mark.parametrize("operation", ["summary", "question"])
def test_empty_text_does_not_call_model(monkeypatch, operation):
    generate = Mock()
    monkeypatch.setattr(service, "_generate", generate)
    with pytest.raises(service.AnalysisError, match="no extracted full text"):
        if operation == "summary":
            service.summarize("Paper", "")
        else:
            service.answer_question("Paper", "", "Why?")
    generate.assert_not_called()


def test_short_summary_includes_evidence_and_grounding_instructions(monkeypatch):
    generate = Mock(return_value="Problem: A controlled result.")
    monkeypatch.setattr(service, "_generate", generate)
    text = "[Page 1]\nA repeatable method.\n\n[Page 2]\nEvaluation evidence."
    assert service.summarize("Paper", text) == generate.return_value
    prompt = generate.call_args.args[0]
    assert "A repeatable method." in prompt and "Evaluation evidence." in prompt
    assert "Do not invent" in prompt and "page numbers" in prompt
    generate.assert_called_once()


def test_long_summary_combines_each_section(monkeypatch):
    generate = Mock(side_effect=["Section one evidence", "Section two evidence", "Combined summary"])
    monkeypatch.setattr(service, "_generate", generate)
    text = "[Page 1]\n" + "a" * 20000 + "\n\n[Page 2]\n" + "b" * 20000
    assert service.summarize("Paper", text) == "Combined summary"
    assert generate.call_count == 3
    prompts = [call.args[0] for call in generate.call_args_list]
    assert "[Page 1]" in prompts[0] and "[Page 2]" in prompts[1]
    assert "Section one evidence" in prompts[2] and "Section two evidence" in prompts[2]


def test_summary_does_not_silently_drop_end_of_a_long_page(monkeypatch):
    generate = Mock(return_value="Controlled summary")
    monkeypatch.setattr(service, "_generate", generate)
    text = "[Page 1]\n" + "a" * 30000 + " CONCLUSION_AT_END"
    service.summarize("Paper", text)
    prompts = [call.args[0] for call in generate.call_args_list]
    assert any("CONCLUSION_AT_END" in prompt for prompt in prompts)


def test_summary_over_limit_is_rejected_before_model_calls(monkeypatch):
    generate = Mock()
    monkeypatch.setattr(service, "_generate", generate)
    text = "\n\n".join(f"[Page {i}]\n" + "evidence " * 3000 for i in range(1, 10))
    with pytest.raises(service.AnalysisError, match="too long"):
        service.summarize("Paper", text)
    generate.assert_not_called()


def test_question_uses_all_pages_when_text_fits(monkeypatch):
    generate = Mock(return_value="Answer from page 7.")
    monkeypatch.setattr(service, "_generate", generate)
    text = "\n\n".join(f"[Page {i}]\nUnique evidence {i}." for i in range(1, 8))
    assert service.answer_question("Paper", text, "What was evaluated?") == generate.return_value
    prompt = generate.call_args.args[0]
    assert text in prompt
    assert "What was evaluated?" in prompt and "Do not use outside knowledge" in prompt


def test_long_question_uses_relevant_pages_and_discloses_excerpts(monkeypatch):
    generate = Mock(return_value="Answer based on the supplied excerpts.")
    monkeypatch.setattr(service, "_generate", generate)
    parts = []
    for i in range(1, 8):
        prefix = "evaluation metrics " * i
        parts.append(f"[Page {i}]\n" + prefix + "filler " * 9000)
    text = "\n\n".join(parts)
    assert len(text) > service.MAX_QUESTION_TEXT_CHARS
    answer = service.answer_question("Paper", text, "Which evaluation metrics?")
    prompt = generate.call_args.args[0]
    expected_pages = {1, 4, 5, 6, 7}
    assert set(map(int, re.findall(r"\[Page (\d+)\]", prompt))) == expected_pages
    assert len(prompt) < len(text)
    assert answer.startswith("Note: This long paper was answered using selected pages (1, 4, 5, 6, 7), not its full text.")
    assert answer.endswith(generate.return_value)


def test_missing_key_reports_configuration_error():
    with pytest.raises(service.AnalysisError, match="Set GEMINI_API_KEY"):
        service._generate("A prompt")


def test_sdk_result_is_trimmed_and_plain_text_requested(monkeypatch):
    from google import genai
    generate = Mock(return_value=SimpleNamespace(text="  Controlled response  "))
    client = SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    factory = Mock(return_value=client)
    monkeypatch.setattr(genai, "Client", factory)
    monkeypatch.setenv("GEMINI_API_KEY", "test-only-placeholder")
    assert service._generate("Evidence prompt") == "Controlled response"
    assert generate.call_args.kwargs["model"] == service.MODEL
    contents = generate.call_args.kwargs["contents"]
    assert "plain text only" in contents and "Evidence prompt" in contents
    assert "test-only-placeholder" not in contents


@pytest.fixture
def sdk_stub(monkeypatch):
    """Replace only the SDK boundary; keep the application's wrapper active."""
    from google import genai
    generate = Mock(return_value=SimpleNamespace(text="Controlled response"))
    factory = Mock(return_value=SimpleNamespace(models=SimpleNamespace(generate_content=generate)))
    monkeypatch.setattr(genai, "Client", factory)
    monkeypatch.setenv("GEMINI_API_KEY", "test-only-placeholder")
    return factory, generate


@pytest.mark.parametrize("code,message", [
    (400, "rejected the request"),
    (403, "API key or project access"),
    (402, "billing or prepaid credits"),
    (404, "model is unavailable"),
    (429, "rate limit or quota"),
    (503, "temporarily unavailable"),
    (418, "API request failed"),
])
def test_sdk_api_errors_are_classified_without_leaking_details(sdk_stub, code, message):
    from google.genai.errors import APIError
    _, generate = sdk_stub
    generate.side_effect = APIError(code, {"error": {"message": "PRIVATE_PROVIDER_DETAIL"}})
    with pytest.raises(service.AnalysisError) as caught:
        service._generate("PRIVATE_PAPER_TEXT")
    visible = str(caught.value)
    assert message in visible
    assert f"HTTP {code}" in visible
    assert "PRIVATE_PROVIDER_DETAIL" not in visible
    assert "PRIVATE_PAPER_TEXT" not in visible
    assert "test-only-placeholder" not in visible


@pytest.mark.parametrize("text", [None, "   "])
def test_empty_sdk_response_is_an_explicit_failure(sdk_stub, text):
    _, generate = sdk_stub
    generate.return_value = SimpleNamespace(text=text)
    with pytest.raises(service.AnalysisError, match="model returned no text"):
        service._generate("Evidence")
    generate.assert_called_once()


@pytest.mark.parametrize("stage", ["client", "request", "response"])
def test_unexpected_sdk_failure_names_stage_without_exception_details(sdk_stub, stage):
    factory, generate = sdk_stub
    error = RuntimeError("PRIVATE_EXCEPTION_DETAIL")
    if stage == "client":
        factory.side_effect = error
        label = "creating the Gemini client"
    elif stage == "request":
        generate.side_effect = error
        label = "sending the request"
    else:
        class BrokenResponse:
            @property
            def text(self):
                raise error
        generate.return_value = BrokenResponse()
        label = "reading the model response"
    with pytest.raises(service.AnalysisError) as caught:
        service._generate("PRIVATE_PAPER_TEXT")
    visible = str(caught.value)
    assert label in visible and "RuntimeError" in visible
    assert "PRIVATE_EXCEPTION_DETAIL" not in visible
    assert "PRIVATE_PAPER_TEXT" not in visible


def test_missing_sdk_dependency_has_actionable_error(monkeypatch):
    original_import = builtins.__import__
    def missing_sdk(name, *args, **kwargs):
        if name == "google.genai.errors":
            raise ImportError("Controlled missing dependency")
        return original_import(name, *args, **kwargs)
    monkeypatch.setenv("GEMINI_API_KEY", "test-only-placeholder")
    monkeypatch.setattr(builtins, "__import__", missing_sdk)
    with pytest.raises(service.AnalysisError, match="Install the project requirements"):
        service._generate("Evidence")


@pytest.mark.parametrize("size,uses_excerpts", [(400000, False), (400001, True)])
def test_question_context_boundary(monkeypatch, size, uses_excerpts):
    generate = Mock(return_value="Controlled answer")
    monkeypatch.setattr(service, "_generate", generate)
    header = "[Page 1]\n"
    text = header + "a" * (size - len(header))
    assert len(text) == size
    answer = service.answer_question("Paper", text, "What evidence?")
    generate.assert_called_once()
    prompt = generate.call_args.args[0]
    if uses_excerpts:
        assert "selected pages (1), not its full text" in answer
        assert text not in prompt
        assert "[Page 1]" in prompt
        assert "could not find it in the selected excerpts" in prompt
    else:
        assert text in prompt
        assert answer == "Controlled answer"


def test_eight_summary_chunks_are_accepted(monkeypatch):
    generate = Mock(return_value="Controlled grounded partial")
    monkeypatch.setattr(service, "_generate", generate)
    text = "\n\n".join(f"[Page {i}]\n" + "evidence " * 3000 for i in range(1, 9))
    assert service.summarize("Paper", text) == generate.return_value
    assert generate.call_count == 9  # Eight partials and one synthesis.
    for i, call in enumerate(generate.call_args_list[:8], 1):
        assert f"[Page {i}]" in call.args[0]
    assert "Section summaries:" in generate.call_args_list[-1].args[0]
