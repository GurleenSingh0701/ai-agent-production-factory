import redis
import hashlib
import json
from typing import Optional, Any
from app.core.config import settings
from app.core.logger import logger

class RedisCache:
    def __init__(self):
        try:
            self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            logger.info("✅ Connected to Upstash Redis Cache")
        except Exception as e:
            logger.error(f"❌ Redis Connection Failed: {e}")
            self.client = None

    def _generate_key(self, prompt: str, model: str) -> str:
        """Creates a unique hash for the prompt and model combination."""
        combined = f"{model}:{prompt}"
        return f"cache:{hashlib.sha256(combined.encode()).hexdigest()}"

    def get(self, prompt: str, model: str) -> Optional[Any]:
        if not self.client: return None
        
        key = self._generate_key(prompt, model)
        cached_val = self.client.get(key)
        
        if cached_val:
            logger.info(f"🚀 Cache Hit for key: {key[:12]}...")
            return json.loads(cached_val)
        
        logger.info(f"❄️ Cache Miss for key: {key[:12]}...")
        return None

    def set(self, prompt: str, model: str, value: Any, ttl: int = 3600):
        if not self.client: return
        
        key = self._generate_key(prompt, model)
        self.client.setex(key, ttl, json.dumps(value))
        logger.info(f"💾 Cached response for key: {key[:12]}...")

# Singleton instance
cache = RedisCache()
