import os

import redis
import redis.asyncio as aioredis
from dotenv import load_dotenv

load_dotenv()

# Sync client for sync code (CRUD endpoints)
sync_redis = redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)

# Async client for async code (background tasks, WebSocket)
async_redis = aioredis.from_url(os.environ["REDIS_URL"], decode_responses=True)
