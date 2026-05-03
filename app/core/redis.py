import os
import json
import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
PENDING_TTL_SECONDS = 10 * 60
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24
REFRESH_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 30 дней

redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)


async def set_pending_registration(email: str, data: dict) -> None:
    await redis_client.setex(
        f"pending:{email}",
        PENDING_TTL_SECONDS,
        json.dumps(data)
    )


async def get_pending_registration(email: str) -> dict | None:
    raw = await redis_client.get(f"pending:{email}")
    if not raw:
        return None
    return json.loads(raw)


async def delete_pending_registration(email: str) -> None:
    await redis_client.delete(f"pending:{email}")


async def blacklist_token(token: str) -> None:
    await redis_client.setex(
        f"blacklist:{token}",
        ACCESS_TOKEN_EXPIRE_SECONDS,
        "1"
    )


async def is_token_blacklisted(token: str) -> bool:
    result = await redis_client.get(f"blacklist:{token}")
    return result is not None


async def store_refresh_token(user_id: int, token: str) -> None:
    await redis_client.setex(
        f"refresh:{user_id}",
        REFRESH_TOKEN_EXPIRE_SECONDS,
        token
    )


async def get_refresh_token(user_id: int) -> str | None:
    return await redis_client.get(f"refresh:{user_id}")


async def delete_refresh_token(user_id: int) -> None:
    await redis_client.delete(f"refresh:{user_id}")