import time
from redis import asyncio as aioredis
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from rate_limit.plans import Plan

class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, redis_client: aioredis.Redis):
        super().__init__(app)
        self.redis = redis_client

    async def dispatch(self, request, call_next):
        auth_token = request.headers.get('authorization')
        plan = getattr(request.state, 'plan', Plan.FREE)
        
        if not await self.is_allowed(auth_token, plan):
            return JSONResponse(status_code=429, content={'error': 'Rate limit exceeded'})
        
        return await call_next(request)

    async def is_allowed(self, auth_token: str, plan: Plan) -> bool:
        try:
            now = int(time.time())
            async with self.redis.pipeline() as redis_storage:
                for limit in plan.value.limits:
                    window = now // limit.period_seconds
                    key = f"{limit.name}:{auth_token}:{window}"
                    await redis_storage.incr(key)
                    await redis_storage.expire(key, limit.period_seconds)

                results = await redis_storage.execute()
                
                if not results:
                    return True
                
                for i, limit in enumerate(plan.value.limits):
                    if i*2 >= len(results):
                        continue
                        
                    count = results[i*2]
                    if count is None or not isinstance(count, int):
                        continue
                        
                    if count > limit.requests:
                        return False
                        
                return True
        except Exception as e:
            return False
