import aioredis

conn = None

async def get_connection() -> aioredis.RedisConnection:
    global conn

    # Lazy connection
    if conn is None:
        conn = await aioredis.create_redis('redis://localhost', encoding='utf-8')

    return conn
