# def calc(x, y, z):
#     if z == 1:
#         return x + y
#     elif z == 2:
#         return x - y
#     elif z == 3:
#         return x * y
#     elif z == 4:
#         return x / y
#     else:
#         return 0


from enum import Enum
from typing import Callable


class Operation(Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


class Calculator:
    def __init__(self):
        self._operations: dict[Operation, Callable] = {
            Operation.ADD: self._add,
            Operation.SUBTRACT: self._subtract,
            Operation.MULTIPLY: self._multiply,
            Operation.DIVIDE: self._divide
        }

    def calculate(self, x: float, y: float, operation: Operation) -> float:
        """두 숫자에 대한 사칙연산을 수행합니다."""
        if operation not in self._operations:
            raise ValueError(f"지원하지 않는 연산: {operation}")

        return self._operations[operation](x, y)

    def _add(self, x: float, y: float) -> float:
        return x + y

    def _subtract(self, x: float, y: float) -> float:
        return x - y

    def _multiply(self, x: float, y: float) -> float:
        return x * y

    def _divide(self, x: float, y: float) -> float:
        if y == 0:
            raise ZeroDivisionError("0으로 나눌 수 없습니다")
        return x / y


# 사용 예시
calculator = Calculator()
result = calculator.calculate(10, 5, Operation.ADD)  # 15
print(result)