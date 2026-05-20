import os
from dotenv import load_dotenv
import redis

load_dotenv()
sync_redis = redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)