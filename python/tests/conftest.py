import pytest
from redis import asyncio as aioredis
from fastapi.testclient import TestClient
from main import app
from unittest.mock import Mock, MagicMock, AsyncMock

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_redis():
    redis_mock = Mock(spec=aioredis.Redis)
    pipeline_mock = MagicMock()
    
    redis_mock.pipeline.return_value = pipeline_mock
    pipeline_mock.incr.return_value = pipeline_mock
    pipeline_mock.expire.return_value = pipeline_mock
    
    execute_mock = AsyncMock()
    execute_mock.return_value = [1]
    pipeline_mock.execute = execute_mock
    
    return redis_mock
