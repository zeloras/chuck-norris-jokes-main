from enum import Enum
from dataclasses import dataclass
from typing import Optional

@dataclass
class RateLimit:
    requests_per_second: Optional[int] = None
    daily_limit: Optional[int] = None

class Plan(Enum):
    FREE = RateLimit(requests_per_second=1, daily_limit=50)
    PRO = RateLimit(requests_per_second=10, daily_limit=12000)
    ENTERPRISE = RateLimit(requests_per_second=100)

    @classmethod
    def get_plan(cls, name: str) -> 'Plan':
        try:
            return cls[name.upper()]
        except (KeyError, AttributeError):
            return cls.FREE
