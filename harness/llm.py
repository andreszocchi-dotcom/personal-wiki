"""The only module that talks to the model: local Gemma served by Ollama.

Uses Ollama's HTTP API with the standard library, so the harness has no
Python dependencies and makes no network calls beyond localhost.
"""

import json
import time
import urllib.error
import urllib.request

from . import config


class ModelUnavailable(RuntimeError):
    """Ollama is not running, or the configured model is not pulled."""


def _post(path, body, timeout=600):
    req = urllib.request.Request(
        f"{config.OLLAMA_HOST}{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")
        if err.code == 404 and "not found" in detail:
            raise ModelUnavailable(
                f"Model '{config.MODEL}' is not pulled. Run: ollama pull {config.MODEL}"
            ) from err
        raise RuntimeError(f"Ollama returned {err.code}: {detail}") from err
    except urllib.error.URLError as err:
        raise ModelUnavailable(
            f"Can't reach Ollama at {config.OLLAMA_HOST} ({err.reason}). "
            "Start it with `ollama serve` (or open the Ollama app)."
        ) from err


def _get(path):
    try:
        with urllib.request.urlopen(f"{config.OLLAMA_HOST}{path}", timeout=5) as resp:
            return json.load(resp)
    except urllib.error.URLError as err:
        raise ModelUnavailable(
            f"Can't reach Ollama at {config.OLLAMA_HOST} ({err.reason}). "
            "Start it with `ollama serve` (or open the Ollama app)."
        ) from err


def check_ready():
    """Fail early with a useful message instead of a stack trace mid-answer."""
    names = {m["name"] for m in _get("/api/tags").get("models", [])}
    if config.MODEL not in names and f"{config.MODEL}:latest" not in names:
        raise ModelUnavailable(
            f"Model '{config.MODEL}' is not pulled. Run: ollama pull {config.MODEL}\n"
            f"Pulled models: {', '.join(sorted(names)) or 'none'}"
        )


def runtime_info():
    """Model + runtime identity recorded in every evidence file."""
    info = {"model": config.MODEL, "host": config.OLLAMA_HOST, "execution": "local"}
    try:
        info["ollama_version"] = _get("/api/version").get("version")
        show = json.load(_post("/api/show", {"model": config.MODEL}, timeout=10))
        details = show.get("details", {})
        info["quantization"] = details.get("quantization_level")
        info["parameter_size"] = details.get("parameter_size")
        info["digest"] = next(
            (m["digest"][:12] for m in _get("/api/tags")["models"]
             if m["name"] == config.MODEL), None)
    except (ModelUnavailable, RuntimeError, KeyError):
        pass
    return info


def loaded_memory():
    """What Ollama reports for the loaded model (bytes total / in GPU memory)."""
    for m in _get("/api/ps").get("models", []):
        if m["name"] == config.MODEL:
            return {"size_bytes": m.get("size"), "size_vram_bytes": m.get("size_vram")}
    return None


def chat(messages, *, temperature=0.2, fmt=None, stream_to=None, think=False):
    """Send one /api/chat request and return (text, metrics).

    fmt: a JSON schema to force structured output (ingest, chat router).
    stream_to: a callable that receives text pieces as they arrive (CLI echo).
    """
    body = {
        "model": config.MODEL,
        "messages": messages,
        "stream": True,
        "think": think,
        "options": {"temperature": temperature, "num_ctx": config.NUM_CTX},
    }
    if fmt is not None:
        body["format"] = fmt

    started = time.perf_counter()
    first_token = None
    parts, final = [], {}
    with _post("/api/chat", body) as resp:
        for line in resp:
            line = line.strip()
            if not line:
                continue
            chunk = json.loads(line)
            if chunk.get("error"):
                raise RuntimeError(chunk["error"])
            piece = chunk.get("message", {}).get("content", "")
            if piece:
                if first_token is None:
                    first_token = time.perf_counter() - started
                parts.append(piece)
                if stream_to:
                    stream_to(piece)
            if chunk.get("done"):
                final = chunk
                break

    metrics = {
        "wall_seconds": round(time.perf_counter() - started, 2),
        "first_token_seconds": round(first_token, 2) if first_token else None,
        "prompt_tokens": final.get("prompt_eval_count"),
        "output_tokens": final.get("eval_count"),
        "load_seconds": round(final.get("load_duration", 0) / 1e9, 2),
    }
    if final.get("eval_duration"):
        metrics["tokens_per_second"] = round(
            final["eval_count"] / (final["eval_duration"] / 1e9), 1)
    return "".join(parts), metrics


def chat_json(messages, schema, temperature=0.1):
    """Structured call: returns (parsed_dict, metrics)."""
    text, metrics = chat(messages, temperature=temperature, fmt=schema)
    try:
        return json.loads(text), metrics
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Model returned invalid JSON: {text[:300]}") from err
