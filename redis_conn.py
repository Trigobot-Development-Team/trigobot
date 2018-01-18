import os
import aioredis

REDIS_URL = os.environ.get('REDISCLOUD_URL', 'redis://localhost')

_conn = None
async def get_connection() -> aioredis.RedisConnection:
    global _conn

    # Lazy connection
    if _conn is None:
        _conn = await aioredis.create_redis(REDIS_URL, encoding='utf-8')

    return _conn
