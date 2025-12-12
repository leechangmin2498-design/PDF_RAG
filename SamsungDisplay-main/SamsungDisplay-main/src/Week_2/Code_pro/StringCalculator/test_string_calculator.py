from string_calculator import StringCalculator

def test_empty_string_returns_zero():
    calculator = StringCalculator()
    assert calculator.add("") == 0

def test_single_number_returns_itself():
    calculator = StringCalculator()
    assert calculator.add("5") == 5

def test_comma_separated_returns_sum():
    calculator = StringCalculator()
    assert calculator.add("1,2,3") == 6