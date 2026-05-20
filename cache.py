import os

import redis
import redis.asyncio as aioredis
from dotenv import load_dotenv

load_dotenv()

sync_redis = redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)

# For background tasks and websockets
async_redis = aioredis.from_url(os.environ["REDIS_URL"], decode_responses=True)
