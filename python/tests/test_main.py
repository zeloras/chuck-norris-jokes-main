from fastapi.testclient import TestClient
from main import app
from rate_limit.plans import Plan
import pytest
from unittest.mock import patch

class TestJokeEndpoint:
    def setup_method(self):
        self.auth_accounts_patcher = patch('auth.Auth.accounts', new={"1111-2222-3333": {"plan": "FREE"}})
        self.mock_auth_accounts = self.auth_accounts_patcher.start()
        
        self.client = TestClient(app)
        self.valid_token = "1111-2222-3333"

    def teardown_method(self):
        self.auth_accounts_patcher.stop()

    def test_invalid_token(self):
        response = self.client.get("/joke")

        assert response.status_code == 403
        assert response.json() == {'error': 'Invalid request!'}

    def test_valid_token(self):
        with patch('rate_limit.limits.RateLimiter.is_allowed', return_value=True):
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
        with patch('rate_limit.limits.RateLimiter.is_allowed', return_value=False):
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
        
        received_plan = None
        
        def mock_is_allowed(auth_token, plan):
            nonlocal received_plan
            received_plan = plan
            return True
            
        with patch('auth.Auth.accounts', new=mock_accounts), \
             patch('rate_limit.limits.RateLimiter.is_allowed', side_effect=mock_is_allowed):
                
            self.client.get(
                "/joke",
                headers={"Authorization": self.valid_token}
            )
            
            assert received_plan == test_case["expected_plan"]
