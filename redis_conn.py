import os
import aioredis

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost')

conn = None

async def get_connection() -> aioredis.RedisConnection:
    global conn

    # Lazy connection
    if conn is None:
        conn = await aioredis.create_redis(REDIS_URL, encoding='utf-8')

    return conn
