import re

import httpx


def capabilities(config):
    provider = config.provider
    model = config.model.lower()
    sources = []
    native = False
    limit = 10
    limit_basis = "conservative evaluation cap; override with --image-limit for your endpoint"
    if provider in ("openai", "openai-chat"):
        limit = 500
        limit_basis = "conservative cap within the OpenAI image-input limit"
        sources = ["https://developers.openai.com/api/docs/guides/images-vision"]
    elif provider == "anthropic":
        limit = 100
        limit_basis = "lowest documented Claude API image-count limit"
        sources = ["https://platform.claude.com/docs/en/build-with-claude/vision"]
    elif provider == "gemini":
        native = "gemini" in model
        limit = 100
        sources = ["https://ai.google.dev/gemini-api/docs/video-understanding"]
    elif provider == "dashscope":
        native = bool(re.search(r"qwen(?:2\.5-vl|3-vl|3\.[5-8])", model))
        sources = ["https://docs.modelstudio.console.alibabacloud.com/en/model-studio/vision"]
    elif provider == "zai":
        native = bool(re.search(r"glm-4\.[156]v", model))
        sources = ["https://docs.z.ai/guides/vlm/glm-4.6v"]
    elif provider == "moonshot":
        native = model.startswith(("kimi-k2.5", "kimi-k2.6", "kimi-k3"))
        limit = 100
        sources = ["https://platform.kimi.ai/docs/guide/use-kimi-vision-model"]
    elif provider == "openrouter":
        response = httpx.get(config.base_url + "/models", timeout=30)
        response.raise_for_status()
        found = [m for m in response.json()["data"] if m["id"] == config.model]
        if not found:
            raise ValueError(
                f"Exact model ID is absent from the OpenRouter catalog: {config.model}"
            )
        modalities = found[0].get("architecture", {}).get("input_modalities", [])
        if "image" not in modalities:
            raise ValueError("Selected OpenRouter model does not advertise image input")
        native = "video" in modalities
        sources = [
            config.base_url + "/models",
            "https://openrouter.ai/docs/guides/overview/multimodal/videos",
        ]
    elif provider == "together":
        sources = ["https://docs.together.ai/docs/inference/vision/inputs"]
    if config.native_supported is not None:
        native = config.native_supported
    if config.image_limit is not None:
        limit = config.image_limit
        limit_basis = "explicit --image-limit"
    return {
        "native_video": native,
        "image_limit": limit,
        "image_limit_basis": limit_basis,
        "sources": sources,
    }
