import pytest
from calculator import Calculator

# def test_add_two_numbers():
#     calc = Calculator()
#     result = calc.add(2, 3)
#     assert result == 5  # 기대: 2 + 3 = 5
#
# def test_add_multiple_numbers():
#     calc = Calculator()
#     result = calc.add_multiple([1, 2, 3, 4])
#     assert result == 10

from calculator import Calculator

def test_add_two_numbers():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_add_multiple_numbers():
    calc = Calculator()
    assert calc.add_all([1, 2, 3, 4]) == 10


