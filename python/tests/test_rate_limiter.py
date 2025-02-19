import pytest
from rate_limit.limits import RateLimiter
from rate_limit.plans import Plan

class TestRateLimiter:
    def setup_method(self):
        self.auth_token = "test_user"

    def test_allow_request_within_limits(self, mock_redis):
        limiter = RateLimiter(mock_redis)
        pipeline = mock_redis.pipeline()
        pipeline.execute.return_value = [1]

        result = limiter.is_allowed(self.auth_token, Plan.FREE)

        assert result is True
        assert pipeline.execute.called

    def test_too_many_requests_per_second(self, mock_redis):
        limiter = RateLimiter(mock_redis)
        pipeline = mock_redis.pipeline()
        pipeline.execute.return_value = [2]

        result = limiter.is_allowed(self.auth_token, Plan.FREE)

        assert result is False

    def test_daily_limit_exceeded(self, mock_redis):
        limiter = RateLimiter(mock_redis)
        pipeline = mock_redis.pipeline()
        pipeline.execute.return_value = [1, None, 51]

        result = limiter.is_allowed(self.auth_token, Plan.FREE)

        assert result is False

    def test_ignore_daily_limit(self, mock_redis):
        limiter = RateLimiter(mock_redis)
        pipeline = mock_redis.pipeline()
        pipeline.execute.return_value = [1, None, 1000]

        result = limiter.is_allowed(self.auth_token, Plan.ENTERPRISE)

        assert result is True

    @pytest.mark.parametrize(
        "test_case",
        [
            pytest.param(
                {
                    "plan": Plan.FREE,
                    "requests_per_second": 1,
                    "daily_requests": 49,
                    "expected": True
                },
                id="FREE plan within limits"
            ),
            pytest.param(
                {
                    "plan": Plan.PRO,
                    "requests_per_second": 10,
                    "daily_requests": 11999,
                    "expected": True
                },
                id="PRO plan within limits"
            ),
            pytest.param(
                {
                    "plan": Plan.ENTERPRISE,
                    "requests_per_second": 99,
                    "daily_requests": None,
                    "expected": True
                },
                id="ENTERPRISE plan within limits"
            ),
        ]
    )
    def test_plans_limits(self, mock_redis, test_case):
        limiter = RateLimiter(mock_redis)
        pipeline = mock_redis.pipeline()

        if test_case["daily_requests"] is None:
            pipeline.execute.return_value = [test_case["requests_per_second"]]
        else:
            pipeline.execute.return_value = [
                test_case["requests_per_second"],
                None,
                test_case["daily_requests"]
            ]

        result = limiter.is_allowed(self.auth_token, test_case["plan"])

        assert result is test_case["expected"]

    def test_redis_failure_gracefully(self, mock_redis):
        limiter = RateLimiter(mock_redis)
        pipeline = mock_redis.pipeline()
        pipeline.execute.side_effect = Exception("Redis connection error")

        result = limiter.is_allowed(self.auth_token, Plan.FREE)

        assert result is False

    @pytest.mark.parametrize(
        "redis_response",
        [
            pytest.param(None, id="Redis returns None"),
            pytest.param([], id="Redis returns empty list"),
            pytest.param([None], id="Redis returns list with None"),
            pytest.param([0], id="Redis returns zero requests"),
        ]
    )
    def test_unexpected_redis_responses(self, mock_redis, redis_response):
        limiter = RateLimiter(mock_redis)
        pipeline = mock_redis.pipeline()
        pipeline.execute.return_value = redis_response

        result = limiter.is_allowed(self.auth_token, Plan.FREE)

        assert result is True
