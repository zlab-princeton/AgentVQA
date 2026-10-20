import json
from types import SimpleNamespace

import httpx
import pytest

from agentvqa_eval.providers import Provider, ProviderError, RunConfig


def provider(monkeypatch, route, **kwargs):
    monkeypatch.setenv("TEST_MODEL_KEY", "unit-test-not-a-real-credential")
    return Provider(
        RunConfig(
            model=kwargs.pop("model", "test-model"),
            provider=route,
            api_key_env="TEST_MODEL_KEY",
            **kwargs,
        )
    )


def test_openai_official_responses_reasoning(monkeypatch):
    client = provider(
        monkeypatch, "openai", model="gpt-5.6-sol", extract_reasoning=True, reasoning_effort="high"
    )
    route, body, headers = client.build_request("question", [b"image"])
    assert client.config.base_url == "https://api.openai.com/v1"
    assert route == "/responses"
    assert body["reasoning"] == {"effort": "high", "summary": "auto"}
    assert body["input"][0]["content"][0]["type"] == "input_image"
    assert not body["store"]
    assert "temperature" not in body
    result = client.parse_response(
        {
            "output": [
                {"type": "reasoning", "summary": [{"text": "summary"}]},
                {"type": "message", "content": [{"type": "output_text", "text": "E"}]},
            ]
        }
    )
    assert result.text == "E" and result.reasoning == "summary"


def test_anthropic_native_thinking(monkeypatch):
    client = provider(
        monkeypatch,
        "anthropic",
        model="claude-opus-4-8",
        thinking="adaptive",
        extract_reasoning=True,
    )
    route, body, headers = client.build_request("question", [b"image"])
    assert route == "/messages"
    assert "x-api-key" in headers
    assert body["thinking"] == {"type": "adaptive", "display": "summarized"}
    assert body["messages"][0]["content"][0]["source"]["type"] == "base64"


def test_thinking_disabled_does_not_return_provider_reasoning(monkeypatch):
    client = provider(monkeypatch, "zai", thinking="disabled")
    _, body, _ = client.build_request("question", [b"image"])
    assert body["thinking"] == {"type": "disabled"}
    result = client.parse_response(
        {"choices": [{"message": {"content": "H", "reasoning_content": "secret"}}]}
    )
    assert result.reasoning is None and result.text == "H"


def test_qwen_official_video_url(monkeypatch, tmp_path):
    client = provider(monkeypatch, "dashscope", model="qwen3.5-27b", thinking="enabled")
    path = tmp_path / "video.mp4"
    path.write_bytes(b"fake video")
    uri = "hf://datasets/AgentVQA/AgentVQA@" + "a" * 40 + "/media/MarioQA/abc.mp4"
    _, body, _ = client.build_request("question", [], path, uri)
    video = body["messages"][0]["content"][0]
    assert video["type"] == "video_url"
    assert video["video_url"]["url"].startswith(
        "https://huggingface.co/datasets/AgentVQA/AgentVQA/resolve/"
    )
    assert body["enable_thinking"] is True


def test_qwen25_image_pixel_limits_match_preprocessing(monkeypatch):
    client = provider(monkeypatch, "dashscope", model="qwen2.5-vl-72b-instruct")
    _, body, _ = client.build_request("question", [b"image"])
    part = body["messages"][0]["content"][0]
    assert part["min_pixels"] == 3136
    assert part["max_pixels"] == client.config.qwen_max_pixels == 1003520


def test_http_retry_classification(monkeypatch):
    client = provider(monkeypatch, "openai-chat")
    client.client.close()
    client.client = httpx.Client(
        transport=httpx.MockTransport(lambda r: httpx.Response(429, headers={"Retry-After": "7"}))
    )
    with pytest.raises(ProviderError) as raised:
        client.generate("question", [b"image"])
    assert raised.value.transient and raised.value.retry_after == 7


@pytest.mark.parametrize("code", [400, 401, 402, 403, 404, 413])
def test_nontransient_http_codes(code):
    assert not ProviderError("error", code).transient


def test_exact_model_id_and_variable_choice_response(monkeypatch):
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "model": "exact-version",
                "choices": [
                    {
                        "message": {"content": "G", "reasoning": "provider summary"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"total_tokens": 13},
            },
        )

    client = provider(
        monkeypatch,
        "compatible",
        model="exact-version",
        base_url="http://127.0.0.1:8000/v1",
        extract_reasoning=True,
    )
    client.client.close()
    client.client = httpx.Client(transport=httpx.MockTransport(handler))
    result = client.generate("A B C D E F G H", [b"image"])
    assert seen[0]["model"] == "exact-version"
    assert result.text == "G" and result.usage["total_tokens"] == 13


def test_forbid_input_overrides_and_url_credentials():
    with pytest.raises(ValueError):
        RunConfig(model="test", provider="openai", extra_body={"messages": []})
    with pytest.raises(ValueError):
        RunConfig(model="test", provider="compatible", base_url="https://key:secret@example.com")


def test_gemini_native_file_lifecycle_and_summary(monkeypatch, tmp_path):
    from google import genai
    from google.genai import types

    calls = []
    file = SimpleNamespace(
        name="files/test", uri="https://provider.test/video", state=SimpleNamespace(name="ACTIVE")
    )

    class Client:
        def __init__(self, **kwargs):
            assert kwargs["http_options"].retry_options.attempts == 1
            self.files = SimpleNamespace(upload=self.upload, delete=self.delete)
            self.models = SimpleNamespace(generate_content=self.generate)

        def upload(self, **kwargs):
            calls.append(("upload", kwargs))
            return file

        def delete(self, **kwargs):
            calls.append(("delete", kwargs))

        def generate(self, **kwargs):
            calls.append(("generate", kwargs))
            assert kwargs["config"].thinking_config.include_thoughts is True
            assert kwargs["contents"][0].parts[0].file_data.file_uri == file.uri
            return types.GenerateContentResponse(
                candidates=[
                    types.Candidate(
                        content=types.Content(
                            parts=[types.Part(text="summary", thought=True), types.Part(text="J")]
                        ),
                        finish_reason="STOP",
                    )
                ],
                model_version="exact-model",
                response_id="test-response",
            )

        def close(self):
            calls.append(("close", {}))

    monkeypatch.setattr(genai, "Client", Client)
    client = provider(
        monkeypatch, "gemini", model="gemini-test", extract_reasoning=True, native_max_mb=0.000001
    )
    video = tmp_path / "video.mp4"
    video.write_bytes(b"video-content")
    result = client.generate("question", [], video)
    assert result.text == "J" and result.reasoning == "summary"
    assert [name for name, _ in calls] == ["upload", "generate", "delete", "close"]


def test_moonshot_native_file_lifecycle(monkeypatch, tmp_path):
    seen = []

    def handler(request):
        seen.append((request.method, request.url.path))
        if request.url.path.endswith("/chat/completions"):
            body = json.loads(request.content)
            assert body["messages"][0]["content"][0]["video_url"]["url"] == "ms://file-test"
            return httpx.Response(200, json={"choices": [{"message": {"content": "E"}}]})
        if request.method == "POST":
            return httpx.Response(200, json={"id": "file-test"})
        return httpx.Response(200, json={"deleted": True})

    client = provider(monkeypatch, "moonshot", model="kimi-k3")
    client.client.close()
    client.client = httpx.Client(transport=httpx.MockTransport(handler))
    path = tmp_path / "video.mp4"
    path.write_bytes(b"video")
    assert client.generate("question", [], path).text == "E"
    assert seen == [
        ("POST", "/v1/files"),
        ("POST", "/v1/chat/completions"),
        ("DELETE", "/v1/files/file-test"),
    ]


def test_openrouter_exact_model_video_capability(monkeypatch):
    from agentvqa_eval.capabilities import capabilities

    request = httpx.Request("GET", "https://openrouter.ai/api/v1/models")
    response = httpx.Response(
        200,
        request=request,
        json={
            "data": [
                {
                    "id": "qwen/exact-version",
                    "architecture": {"input_modalities": ["text", "image", "video"]},
                }
            ]
        },
    )
    monkeypatch.setattr(httpx, "get", lambda *a, **k: response)
    assert capabilities(RunConfig(model="qwen/exact-version", provider="openrouter"))[
        "native_video"
    ]
    with pytest.raises(ValueError, match="Exact model ID"):
        capabilities(RunConfig(model="qwen/other-size", provider="openrouter"))
