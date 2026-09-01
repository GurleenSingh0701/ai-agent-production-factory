import os
import litellm
from litellm import ModelResponse
from app.core.config import settings
from typing import cast # Import cast for ultimate safety

# Langfuse Setup
os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST

litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]

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

        # --- THE FIX: TYPE NARROWING ---
        # This proves to Pyright that 'response' is definitely a ModelResponse.
        # If it's not, it will raise a TypeError immediately.
        if not isinstance(response, ModelResponse):
            # If for some reason LiteLLM returns a dict instead of an object,
            # we convert it to a ModelResponse or handle it safely.
            raise TypeError(f"Expected ModelResponse, got {type(response)}")

        # Now Pyright is 100% certain that 'choices' exists.
        return response.choices[0].message.content or ""

    except Exception as e:
        try:
            litellm.flush_callbacks()
        except Exception:
            pass
        raise e
