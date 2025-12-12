# class Calculator:
#     def add(self, a, b):
#         return a + b

# class Calculator:
#     """간단한 덧셈 계산기"""
#
#     def add(self, a: float, b: float) -> float:
#         """두 수를 더한 결과를 반환합니다."""
#         return a + b

# class Calculator:
#     """간단한 덧셈 계산기"""
#
#     def add(self, a: float, b: float) -> float:
#         return a + b
#
#     def add_multiple(self, numbers: list[float]) -> float:
#         return sum(numbers)

from typing import Iterable

class Calculator:
    """클린 코드 스타일의 덧셈 계산기"""

    def add(self, a: float, b: float) -> float:
        """두 수를 더합니다."""
        return a + b

    def add_all(self, numbers: Iterable[float]) -> float:
        """여러 수를 모두 더합니다."""
        return sum(numbers)