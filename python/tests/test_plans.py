import pytest
from rate_limit.plans import Plan, RateLimit

@pytest.mark.parametrize("input_plan,expected_plan", [
    ("FREE", Plan.FREE),
    ("PRO", Plan.PRO),
    ("pro", Plan.PRO),
    ("INVALID", Plan.FREE),
    (None, Plan.FREE)
])
def test_get_plan(input_plan, expected_plan):
    assert Plan.get_plan(input_plan) == expected_plan
