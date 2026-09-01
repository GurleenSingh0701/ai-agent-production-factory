import os
import sys
import types
import litellm
from litellm import ModelResponse
from app.core.config import settings
from app.services.cache import cache

# --- THE ULTIMATE VERSION PATCH ---
# This solves the "'str' object has no attribute '__version__'" error
try:
    import langfuse
    # Create a dummy object that looks like a module
    version_module = types.ModuleType("langfuse.version")
    # Assign the version string to the __version__ attribute of that dummy module
    setattr(version_module, "__version__", "2.0.0")
    # Attach this dummy module to the langfuse package
    setattr(langfuse, "version", version_module)
    # Ensure it's registered in sys.modules so other libraries find it
    sys.modules["langfuse.version"] = version_module
except Exception as e:
    print(f"Version patch failed, but proceeding: {e}")
# ----------------------------------

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
    # Check cache first
    cached_val = cache.get(prompt, model)
    if cached_val is not None:
        return str(cached_val)

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

        content = response.choices[0].message.content or ""

        # Store response in cache
        cache.set(prompt, model, content)

        return content

    except Exception as e:
        try:
            litellm.flush_callbacks()
        except Exception:
            pass
        raise e
