from decimal import Decimal
from math import floor


DEFAULT_CURRENCY_PER_POINT = Decimal("1000")
DEFAULT_VISIT_REWARD_TARGET = 10
DEFAULT_POINTS_REWARD_TARGET = 100


class LoyaltyService:
    """Dual-track loyalty calculations — mirrors Flutter LoyaltyService."""

    def __init__(
        self,
        *,
        currency_per_point: Decimal = DEFAULT_CURRENCY_PER_POINT,
        visit_reward_target: int = DEFAULT_VISIT_REWARD_TARGET,
        points_reward_target: int = DEFAULT_POINTS_REWARD_TARGET,
    ):
        self.currency_per_point = currency_per_point
        self.visit_reward_target = visit_reward_target
        self.points_reward_target = points_reward_target

    def points_for_purchase(self, amount: Decimal) -> int:
        if amount <= 0 or self.currency_per_point <= 0:
            return 0
        earned = floor(float(amount / self.currency_per_point))
        return max(0, earned)

    def is_visit_gift_eligible(self, visits: int) -> bool:
        return self.visit_reward_target > 0 and visits >= self.visit_reward_target

    def is_points_gift_eligible(self, points: int) -> bool:
        return self.points_reward_target > 0 and points >= self.points_reward_target

    def is_eligible_for_any(self, visits: int, points: int) -> bool:
        return self.is_visit_gift_eligible(visits) or self.is_points_gift_eligible(points)

    def visits_after_redeem(self, visits: int) -> int:
        return visits - self.visit_reward_target

    def points_after_redeem(self, points: int) -> int:
        return points - self.points_reward_target

    def visit_cost(self) -> int:
        return max(0, self.visit_reward_target)

    def points_cost(self) -> int:
        return max(0, self.points_reward_target)
