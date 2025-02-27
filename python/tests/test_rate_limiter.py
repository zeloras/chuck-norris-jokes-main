import pytest
from rate_limit.limits import RateLimiter
from rate_limit.plans import Plan
from fastapi import FastAPI
from unittest.mock import AsyncMock

class TestRateLimiter:
    def setup_method(self):
        self.auth_token = "test_user"
        self.mock_app = FastAPI()
        
        # Setup pipeline mock for all tests
        self.pipeline_mock = AsyncMock()
        self.pipeline_mock.__aenter__.return_value = self.pipeline_mock
        self.pipeline_mock.__aexit__.return_value = None

    def setup_limiter(self, mock_redis):
        limiter = RateLimiter(self.mock_app, mock_redis)
        mock_redis.pipeline.return_value = self.pipeline_mock
        return limiter
        
    async def check_is_allowed(self, mock_redis, plan, mock_response, expected_result=True, side_effect=None):
        limiter = self.setup_limiter(mock_redis)
        
        if side_effect:
            self.pipeline_mock.execute.side_effect = side_effect
        else:
            self.pipeline_mock.execute.return_value = mock_response
            
        result = await limiter.is_allowed(self.auth_token, plan)
        assert result is expected_result
        return result

    @pytest.mark.asyncio
    async def test_allow_request_within_limits(self, mock_redis):
        result = await self.check_is_allowed(
            mock_redis, 
            Plan.FREE, 
            [1, None, 1, None]
        )
        assert self.pipeline_mock.execute.called

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "plan, response, expected",
        [
            pytest.param(Plan.FREE, [2, None, 1, None], False, id="per_second_exceeded"),
            pytest.param(Plan.FREE, [1, None, 51, None], False, id="daily_exceeded"),
            pytest.param(Plan.ENTERPRISE, [1, None], True, id="ignore_daily_limit"),
        ]
    )
    async def test_rate_limits(self, mock_redis, plan, response, expected):
        await self.check_is_allowed(
            mock_redis,
            plan,
            response,
            expected
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "test_case",
        [
            pytest.param(
                {
                    "plan": Plan.FREE,
                    "per_second_requests": 1,
                    "daily_requests": 49,
                    "expected": True
                },
                id="FREE plan within limits"
            ),
            pytest.param(
                {
                    "plan": Plan.PRO,
                    "per_second_requests": 10,
                    "daily_requests": 11999,
                    "expected": True
                },
                id="PRO plan within limits"
            ),
            pytest.param(
                {
                    "plan": Plan.ENTERPRISE,
                    "per_second_requests": 99,
                    "daily_requests": None,
                    "expected": True
                },
                id="ENTERPRISE plan within limits"
            ),
        ]
    )
    async def test_plans_limits(self, mock_redis, test_case):
        plan = test_case["plan"]
        
        if plan == Plan.ENTERPRISE:
            response = [test_case["per_second_requests"], None]
        else:
            response = [
                test_case["per_second_requests"], None,
                test_case.get("daily_requests", 0), None
            ]
            
        await self.check_is_allowed(
            mock_redis,
            test_case["plan"],
            response,
            test_case["expected"]
        )

    @pytest.mark.asyncio
    async def test_redis_failure_gracefully(self, mock_redis):
        await self.check_is_allowed(
            mock_redis,
            Plan.FREE,
            None,
            False,
            Exception("Redis connection error")
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "redis_response",
        [
            pytest.param(None, id="Returns None"),
            pytest.param([], id="Returns empty list"),
            pytest.param([None], id="Returns list with None"),
            pytest.param([0], id="Returns zero requests"),
            pytest.param(["some strinfg", None, 1, None], id="Returns string instead of int"),
        ]
    )
    async def test_unexpected_redis_responses(self, mock_redis, redis_response):
        await self.check_is_allowed(
            mock_redis,
            Plan.FREE,
            redis_response,
            True
        )
