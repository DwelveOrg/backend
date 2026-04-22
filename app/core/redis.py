import os
import json
import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
PENDING_TTL_SECONDS = 10 * 60
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24

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