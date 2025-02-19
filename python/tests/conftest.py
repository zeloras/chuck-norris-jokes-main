import pytest
from redis import Redis
from fastapi.testclient import TestClient
from main import app
from unittest.mock import Mock, MagicMock

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_redis():
    redis_mock = Mock(spec=Redis)
    pipeline_mock = MagicMock()

    redis_mock.pipeline.return_value = pipeline_mock

    pipeline_mock.incr.return_value = pipeline_mock
    pipeline_mock.expire.return_value = pipeline_mock
    pipeline_mock.execute.return_value = [1]

    return redis_mock
