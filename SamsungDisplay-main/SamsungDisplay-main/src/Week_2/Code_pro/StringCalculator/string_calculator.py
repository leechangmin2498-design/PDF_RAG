class StringCalculator:
    def add(self, numbers: str) -> int:
        if not numbers:
            return 0

        return self.calculate_sum(numbers)

    def calculate_sum(self, numbers):
        num_list = numbers.split(',')
        return sum(int(n) for n in num_list)