import time
from redis import Redis
from rate_limit.plans import Plan

class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def is_allowed(self, auth_token: str, plan: Plan) -> bool:
        try:
            now = int(time.time())
            redis_storage = self.redis.pipeline()

            # Check requests per second
            requests_key = f"requests:{auth_token}:{now}"
            redis_storage.incr(requests_key)
            redis_storage.expire(requests_key, 1)

            # Check daily limit if applicable
            if plan.value.daily_limit is not None:
                daily_key = f"daily:{auth_token}:{now // 86400}"
                redis_storage.incr(daily_key)
                redis_storage.expire(daily_key, 86400)

            results = redis_storage.execute()

            if not results:
                return True

            requests_count = results[0] or 0
            if requests_count > plan.value.requests_per_second:
                return False

            if plan.value.daily_limit is not None:
                daily_count = results[2] if len(results) > 2 else 0
                if daily_count and daily_count > plan.value.daily_limit:
                    return False

            return True

        except Exception:
            return False
