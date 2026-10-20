# AgentVQA Evaluation

[Benchmark overview, results, and citation](../README.md)

API-based evaluation built on [lmms-eval](https://github.com/EvolvingLMMs-Lab/lmms-eval), with model-specific preprocessing, optional reasoning, resumable runs, and subset, domain, and overall accuracy.

Data and media are loaded from [Hugging Face](https://huggingface.co/datasets/zlab-princeton/AgentVQA); no local dataset preparation is required. Evaluation uses the `train` split without few-shot examples and supports variable option counts. Use `--revision <commit>` to select another dataset release.

## Installation

Python 3.10 or later is required. No GPU or local model weights are needed. On Linux:

```bash
git clone https://github.com/advaitgupta/AgentVQA.git
cd AgentVQA/evaluation
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install torch==2.7.1+cpu torchvision==0.22.1+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
python -m pip check
```

On other platforms, install the appropriate PyTorch build instead of the Linux CPU wheels. Run all commands below from `AgentVQA/evaluation`. Set `HF_HOME` to choose the dataset cache location.

## API configuration

Set the credential environment variable for your provider and pass its exact model ID. Availability depends on the provider, region, and account; model versions and sizes are never substituted.

| Provider flag | Credential variable | Example model IDs |
| --- | --- | --- |
| `openai` | `OPENAI_API_KEY` | `gpt-5.6-sol`, `gpt-5.6-luna` |
| `openai-chat` | `OPENAI_API_KEY` | `gpt-4o` |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-opus-4-8`, `claude-sonnet-5`, `claude-fable-5` |
| `gemini` | `GEMINI_API_KEY` | `gemini-3.1-pro-preview`, `gemini-3.7-flash` |
| `dashscope` | `DASHSCOPE_API_KEY` | `qwen3.5-27b` |
| `zai` | `ZAI_API_KEY` | `glm-4.5v`, `glm-4.6v` |
| `moonshot` | `MOONSHOT_API_KEY` | `kimi-k3` |
| `openrouter` | `OPENROUTER_API_KEY` | `qwen/qwen3.5-27b`, `meta-llama/llama-4-maverick` |
| `together` | `TOGETHER_API_KEY` | `moonshotai/Kimi-K3` |
| `compatible` | `MODEL_API_KEY` | Model ID served by your endpoint |

The native provider routes use official APIs directly. For regional or custom endpoints, use `--base-url` and optionally `--api-key-env`; do not include credentials in URLs.

## Running evaluations

List subsets and validate annotations without model calls:

```bash
python -m agentvqa_eval catalog
python -m agentvqa_eval validate --output outputs/validation.json
```

Start with a small run after setting your API key:

```bash
python -m agentvqa_eval evaluate \
  --provider openai --model gpt-5.6-sol \
  --reasoning-effort high --max-tokens 16384 \
  --subset GameQA --limit 5 --max-api-calls 10 \
  --output outputs/gpt56-gameqa
```

Add `--dry-run` to inspect prompts and media without paid inference. Repeat `--subset` or use `--domain 'Egocentric Videos'` to select data; omit both to evaluate all 23 subsets. `--limit` and `--offset` apply per subset. Invalid dataset annotations stop evaluation before inference.

The paper's Spatial Planning domain is named `Spatial Understanding` in the CLI and reports; use that name with `--domain`.

### Reasoning

| Flag | Purpose |
| --- | --- |
| `--request-reasoning` | Request a brief explanation alongside the final answer. |
| `--extract-reasoning` | Save reasoning text or summaries exposed by the provider. |
| `--reasoning-effort`, `--thinking`, `--thinking-budget` | Configure inference-time reasoning where supported. |

These controls are independent: disabling extraction does not disable inference-time reasoning. The default output budget is 4,096 tokens; increase `--max-tokens` for reasoning models.

```bash
python -m agentvqa_eval evaluate \
  --provider anthropic --model claude-opus-4-8 \
  --thinking adaptive --reasoning-effort high \
  --request-reasoning --extract-reasoning --max-tokens 16384 \
  --subset ManipBench --output outputs/claude-manipbench
```

Use only settings supported by the selected model. Gemini accepts either a thinking level through `--reasoning-effort` or a `--thinking-budget`, not both. Additional generation parameters can be supplied with `--extra-body '{"parameter": "value"}'`.

## Visual preprocessing

### Videos

`--video-mode auto` prefers native video where supported and falls back to frames if the video request is rejected.

| API route | Default video handling |
| --- | --- |
| Gemini | Native video through inline data or the Files API. |
| Supported Qwen models on DashScope | Native video through a public Hub URL. |
| GLM-V on Z.ai | Native video through a public Hub URL. |
| Kimi on Moonshot | Native video through the Files API. |
| OpenAI GPT / Anthropic Claude | Uniformly sampled frames. |
| OpenRouter | Native video only when advertised by the exact model. |
| Together / unspecified compatible endpoint | Frames unless native support is explicitly configured. |

Frame mode samples **32 uniformly spaced frames**, including the first and last, without duplicating frames in shorter videos. Use `--video-mode frames` for a fixed frame-based protocol or `--num-frames` to change the count. Native video sampling follows the provider's implementation.

### Images

Multi-image questions are stitched in groups of **up to four images per 2×2 composite**, read left-to-right and top-to-bottom. Video frames use the same packing when needed: a 10-image endpoint receives eight composites containing all 32 frames. Single-image questions are not stitched. Use `--image-limit` to specify an endpoint's cap and `--max-side` to optionally resize images.

### Coordinates

Image-point options use source-image pixel `[x, y]` coordinates, with origin at the top-left. The evaluator converts them as follows:

| Model/profile | Option format |
| --- | --- |
| Gemini | Integer `[y, x]`, normalized to 0–1000 |
| Qwen2.5-VL | Pixel `[x, y]`, matched to transmitted image dimensions |
| Qwen3-VL and later Qwen multimodal families on DashScope | Integer `[x, y]`, normalized to 0–999 |
| Other Qwen routes | Integer `[x, y]`, normalized to 0–1000 |
| Other models | `[x, y]`, normalized to 0–1 |

These are evaluation profiles, not universal provider requirements. Override them with `--coordinate-format`: `pixel-xy`, `unit-xy`, `1000-xy`, `1000-yx`, `999-xy`, or `999-yx`. Conversion applies only to image-point tasks, not grid positions or symbolic trajectories. Qwen2.5-VL uses 28-pixel-grid resizing before pixel-coordinate options are generated; `--qwen-max-pixels` controls its image budget.

## Scoring and resuming

**Accuracy = correct answers / tested samples with a successfully extracted valid option.** API failures, invalid or unextractable answers, and unattempted samples are excluded. An extracted valid but incorrect answer remains in the denominator. If no valid answers are available, accuracy is `null`. Coverage is valid answers divided by all selected samples.

Subset, domain, and overall scores pool the corresponding correct and valid-answer counts. Reports include selected, answered, excluded, and correct counts alongside accuracy and coverage.

Requests have up to three attempts per sample by default. Use `--retry-invalid` to retry unextractable answers and `--max-api-calls` to cap inference attempts, including retries. Authentication, access, billing, and missing-model errors stop the run.

Completed samples are checkpointed automatically. Resume with the same command and output directory plus `--resume`; add `--retry-failed` to retry failures without resampling valid answers. Resume requires unchanged run settings, data, code, and dependencies.

The output directory contains `manifest.json`, per-sample checkpoints, `predictions.jsonl`, `summary.json`, `accuracy.csv`, and, after evaluator completion, `lmms_results.json`. Interrupted runs are marked incomplete; dry runs are not benchmark results.

## Tests

```bash
python -m pytest -q tests
python -m agentvqa_eval --help
```

Tests use synthetic media and mocked model responses; no API credentials or paid calls are required. See `python -m agentvqa_eval evaluate --help` for all options.
