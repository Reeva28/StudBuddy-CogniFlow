"""Simple Hugging Face Inference API client wrapper used by CogniFlow.

This module provides a tiny helper to call the public Hugging Face Inference
API. It expects the environment variable / pydantic setting
`HUGGINGFACE_API_KEY` to contain a valid API token. The default model is
`google/flan-t5-small` but can be overridden by passing `model=` or by
setting `HUGGINGFACE_MODEL` in the project's settings.

The implementation is intentionally small and synchronous to keep
dependencies light (uses requests). It returns the generated text and
raises on transport or inference errors so callers can decide how to
fallback.
"""
from typing import Optional
import requests

from app.core.config import settings


def _get_headers() -> dict:
	api_key = getattr(settings, "HUGGINGFACE_API_KEY", None)
	if not api_key:
		raise RuntimeError("HUGGINGFACE_API_KEY not set in settings or environment")
	return {"Authorization": f"Bearer {api_key}"}


def _inference_url(model: str) -> str:
	# Allow a custom inference URL to be provided; otherwise use public endpoint
	custom = getattr(settings, "HUGGINGFACE_INFERENCE_URL", None)
	if custom:
		return custom.rstrip("/")
	return f"https://api-inference.huggingface.co/models/{model}"


def generate_text(
	prompt: str,
	model: Optional[str] = None,
	max_new_tokens: int = 256,
	temperature: float = 0.0,
	timeout: int = 60,
) -> str:
	"""Synchronous text generation using the Hugging Face Inference API.

	Returns the generated text (string) or raises an exception on failure.
	"""
	model = model or getattr(settings, "HUGGINGFACE_MODEL", "google/flan-t5-small")
	url = _inference_url(model)
	headers = _get_headers()
	payload = {
		"inputs": prompt,
		"parameters": {"max_new_tokens": max_new_tokens, "temperature": temperature},
	}

	resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
	resp.raise_for_status()
	data = resp.json()

	# Typical responses are either a list of dicts with 'generated_text' or
	# a string/list of strings. Normalize those shapes to a single string.
	if isinstance(data, dict):
		# Error payloads may be dicts with an "error" key
		if "error" in data:
			raise RuntimeError(data.get("error"))
		# Some models may return {'generated_text': '...'}
		if "generated_text" in data:
			return data["generated_text"]

	if isinstance(data, list):
		first = data[0]
		if isinstance(first, dict) and "generated_text" in first:
			return first["generated_text"]
		if isinstance(first, str):
			return first

	# Fallback: stringify the JSON response
	return str(data)


def safe_generate_text(*args, **kwargs) -> Optional[str]:
	"""Call generate_text but return None on error (convenience wrapper)."""
	try:
		return generate_text(*args, **kwargs)
	except Exception:
		return None

