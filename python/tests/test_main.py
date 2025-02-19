from fastapi.testclient import TestClient
from main import app
from rate_limit.plans import Plan
import json
import pytest
from unittest.mock import patch

class TestJokeEndpoint:
    def setup_method(self):
        self.client = TestClient(app)
        self.valid_token = "1111-2222-3333"

    def test_invalid_token(self):
        response = self.client.get("/joke")

        assert response.status_code == 403
        assert response.json() == {'error': 'Invalid request!'}

    def test_valid_token(self):
        with patch('main.rate_limiter.is_allowed', return_value=True):
            response = self.client.get(
                "/joke",
                headers={"Authorization": self.valid_token}
            )

            assert response.status_code == 200
            joke_data = response.json()
            assert isinstance(joke_data, dict)
            assert "id" in joke_data
            assert "joke" in joke_data

    def test_rate_limit_exceeded(self):
        with patch('main.rate_limiter.is_allowed', return_value=False):
            response = self.client.get(
                "/joke",
                headers={"Authorization": self.valid_token}
            )

            assert response.status_code == 429
            assert response.json() == {'error': 'Rate limit exceeded'}

    @pytest.mark.parametrize(
        "test_case",
        [
            pytest.param(
                {"plan": "FREE", "expected_plan": Plan.FREE},
                id="Free plan"
            ),
            pytest.param(
                {"plan": "PRO", "expected_plan": Plan.PRO},
                id="Pro plan"
            ),
            pytest.param(
                {"plan": "INVALID", "expected_plan": Plan.FREE},
                id="Invalid plan defaults to Free"
            ),
        ]
    )
    def test_assign_correct_plan(self, test_case):
        mock_accounts = {
            self.valid_token: {"plan": test_case["plan"]}
        }

        with patch('auth.ACCOUNTS_FILE', return_value='test_accounts.json'), \
             patch('builtins.open') as mock_open, \
             patch('main.rate_limiter.is_allowed', return_value=True) as mock_limiter:

            mock_open.return_value.__enter__.return_value.read.return_value = \
                json.dumps(mock_accounts)

            self.client.get(
                "/joke",
                headers={"Authorization": self.valid_token}
            )

            mock_limiter.assert_called_once()
            assert mock_limiter.call_args[0][1] == test_case["expected_plan"]
