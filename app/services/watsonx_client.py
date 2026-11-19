# app/services/watsonx_client.py
# Low-level IBM watsonx.ai inference client.
# Wraps ibm-watsonx-ai ModelInference for Granite text generation.

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as Params

import json
import logging

logger = logging.getLogger(__name__)

# ─── Default generation parameters ──────────────────────────────────────────

_DEFAULT_PARAMS = {
    Params.DECODING_METHOD: "greedy",
    Params.MAX_NEW_TOKENS: 1024,
    Params.REPETITION_PENALTY: 1.05,
    Params.STOP_SEQUENCES: ["<|user|>", "<|system|>"],
}

# ─── Client singleton ────────────────────────────────────────────────────────

_model: ModelInference | None = None


def _get_model(api_key: str, url: str, project_id: str) -> ModelInference:
    """Return a cached ModelInference instance, creating it on first call."""
    global _model
    if _model is None:
        credentials = Credentials(url=url, api_key=api_key)
        _model = ModelInference(
            model_id="ibm/granite-3-8b-instruct",
            credentials=credentials,
            project_id=project_id,
            params=_DEFAULT_PARAMS,
        )
        logger.info("watsonx.ai ModelInference initialised (ibm/granite-3-8b-instruct)")
    return _model


# ─── Public interface ────────────────────────────────────────────────────────

def generate_json(
    prompt: str,
    api_key: str,
    url: str,
    project_id: str,
) -> dict:
    """
    Send *prompt* to Granite and return the parsed JSON response.

    Raises:
        ValueError: if the model output cannot be parsed as JSON.
        RuntimeError: if the watsonx.ai API call fails.
    """
    model = _get_model(api_key, url, project_id)

    try:
        response = model.generate_text(prompt=prompt)
    except Exception as exc:
        logger.error("watsonx.ai generate_text failed: %s", exc)
        raise RuntimeError(f"watsonx.ai API error: {exc}") from exc

    raw = response.strip() if isinstance(response, str) else str(response).strip()
    logger.debug("Raw model output: %s", raw[:500])

    # Strip optional markdown code fence (```json … ```)
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(
            line for line in lines if not line.strip().startswith("```")
        )

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("JSON parse error. Raw output:\n%s", raw)
        raise ValueError(f"Model returned non-JSON output: {exc}") from exc
