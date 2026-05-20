import os

import redis
from dotenv import load_dotenv

load_dotenv()
sync_redis = redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
