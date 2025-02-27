from enum import Enum
from dataclasses import dataclass, field
from typing import List

@dataclass
class Limit:
    requests: int
    period_seconds: int
    name: str

@dataclass
class RateLimit:
    limits: List[Limit] = field(default_factory=list)

class Plan(Enum):
    FREE = RateLimit(limits=[
        Limit(requests=1, period_seconds=1, name="per_second"),
        Limit(requests=50, period_seconds=86400, name="daily")
    ])
    PRO = RateLimit(limits=[
        Limit(requests=10, period_seconds=1, name="per_second"),
        Limit(requests=12000, period_seconds=86400, name="daily")
    ])
    ENTERPRISE = RateLimit(limits=[
        Limit(requests=100, period_seconds=1, name="per_second")
    ])

    @classmethod
    def get_plan(cls, name: str) -> 'Plan':
        try:
            return cls[name.upper()]
        except (KeyError, AttributeError):
            return cls.FREE
