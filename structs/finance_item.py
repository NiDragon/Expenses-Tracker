from enum import Enum
from dataclasses import dataclass

from decimal import *


class Frequency(Enum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
    ANNUALLY = 4


@dataclass
class FinanceItem:
    name: str = ''
    freq: Frequency = Frequency.DAILY
    cost: Decimal = 0
    daily: Decimal = 0
    weekly: Decimal = 0
    monthly: Decimal = 0
    annually: Decimal = 0
    note: str = ''
