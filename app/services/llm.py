import os
import sys
import types
import json
from typing import cast # Import cast for type safety
import litellm
from litellm import ModelResponse # Import ModelResponse for type hinting
from app.core.config import settings
from app.services.cache import cache

# --- VERSION PATCH ---
try:
    import langfuse
    version_module = types.ModuleType("langfuse.version")
    setattr(version_module, "__version__", "2.0.0")
    setattr(langfuse, "version", version_module)
    sys.modules["langfuse.version"] = version_module
except Exception as e:
    print(f"Version patch failed: {e}")

# Langfuse Setup
os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST

litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]
os.environ["OLLAMA_API_BASE"] = os.getenv("OLLAMA_API_BASE", settings.OLLAMA_API_BASE)

import re

def clean_json_string(text: str) -> str:
    """Strips markdown code blocks, triple backticks, and leading/trailing noise to extract valid JSON."""
    cleaned = text.strip()

    # Strip opening/closing markdown code fences (```json ... ``` or ``` ...)
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    # Strip standalone 'json' prefix if present
    if cleaned.startswith("json\n") or cleaned.startswith("json\r\n"):
        cleaned = cleaned[4:].strip()
    elif cleaned.startswith("json"):
        cleaned = cleaned[4:].strip()

    # Extract JSON structure {...} or [...] using regex if extra text surrounds it
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
    if match:
        return match.group(1)

    return cleaned

class LiteLLMService:
    async def complete(self, prompt: str, model: str = settings.DEFAULT_MODEL) -> str:
        # Cache lookup
        cached_val = cache.get(prompt, model)
        if cached_val:
            return str(cached_val)

        try:
            # Explicitly set stream=False to help the type checker and runtime
            response = await litellm.acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=False 
            )
            
            # FIX: Cast the response to ModelResponse to solve Pyright "CustomStreamWrapper" error
            typed_response = cast(ModelResponse, response)
            
            try:
                litellm.flush_callbacks()
            except:
                pass

            content = typed_response.choices[0].message.content or ""
            cache.set(prompt, model, content)
            return content
        except Exception as e:
            try:
                litellm.flush_callbacks()
            except:
                pass
            raise e

    async def complete_json(self, prompt: str, response_model, model: str = settings.DEFAULT_MODEL):
        """Calls LLM in JSON mode and parses it into a Pydantic model."""
        try:
            response = await litellm.acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                stream=False
            )
            
            # FIX: Cast the response to ModelResponse here as well
            typed_response = cast(ModelResponse, response)
            
            content = typed_response.choices[0].message.content or "{}"
            cleaned_content = clean_json_string(content)
            # Parse the string JSON into the Pydantic model
            return response_model.model_validate_json(cleaned_content)
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            raise e

_default_llm_service = LiteLLMService()

async def call_llm(prompt: str, model: str = settings.DEFAULT_MODEL, json_mode: bool = False) -> str:
    """Helper function for calling LLM (used by day_01 and day_02 agents)."""
    if json_mode:
        response = await litellm.acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            stream=False
        )
        typed_response = cast(ModelResponse, response)
        content = typed_response.choices[0].message.content or "{}"
        return clean_json_string(content)
    return await _default_llm_service.complete(prompt, model=model)

