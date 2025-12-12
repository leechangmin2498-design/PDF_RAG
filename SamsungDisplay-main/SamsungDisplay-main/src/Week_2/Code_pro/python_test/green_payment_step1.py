# green_payment_step1.py
from decimal import Decimal


class PaymentResult:
    def __init__(self, success: bool, amount: Decimal):
        self.success = success
        self.amount = amount

    def __repr__(self):
        return f"PaymentResult(success={self.success}, amount={self.amount})"


class PaymentProcessor:
    """GREEN 단계: 카드 결제만 필요한 만큼만 구현"""

    def process_card_payment(self, amount: Decimal, card_number: str) -> PaymentResult:
        return PaymentResult(success=True, amount=amount)


# -----------------------
# 실행 예시
# -----------------------
if __name__ == "__main__":
    processor = PaymentProcessor()
    result = processor.process_card_payment(
        amount=Decimal("10000"),
        card_number="1234-5678-9012-3456"
    )
    print(result)
