import os
import sys
import litellm
from litellm import ModelResponse
from app.core.config import settings

# --- FIX: LITELLM/LANGFUSE VERSION CONFLICT PATCH ---
# This solves the "module 'langfuse' has no attribute 'version'" error
try:
    import langfuse
    if not hasattr(langfuse, "version"):
        # We manually add the version attribute so litellm doesn't crash
        setattr(langfuse, "version", "2.0.0") 
except ImportError:
    pass
# ----------------------------------------------------

# Langfuse Setup
os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST

# Official Callbacks
litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]

# Bridge for Local/Cloud Ollama
os.environ["OLLAMA_API_BASE"] = os.getenv("OLLAMA_API_BASE", settings.OLLAMA_API_BASE)

async def call_llm(prompt: str, model: str = settings.DEFAULT_MODEL, json_mode: bool = False) -> str:
    try:
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"} if json_mode else None
        )
        
        try:
            litellm.flush_callbacks()
        except Exception:
            pass

        if not isinstance(response, ModelResponse):
            raise TypeError(f"Expected ModelResponse, got {type(response)}")

        return response.choices[0].message.content or ""

    except Exception as e:
        try:
            litellm.flush_callbacks()
        except Exception:
            pass
        raise e
