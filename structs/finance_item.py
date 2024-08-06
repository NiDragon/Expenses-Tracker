from enum import Enum
from dataclasses import dataclass


class Frequency(Enum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    ANNUALLY = 4


@dataclass
class FinanceItem:
    name: str = ''
    freq: Frequency = Frequency.DAILY
    cost: float = 0
    daily: float = 0
    weekly: float = 0
    monthly: float = 0
    annually: float = 0
    note: str = ''
