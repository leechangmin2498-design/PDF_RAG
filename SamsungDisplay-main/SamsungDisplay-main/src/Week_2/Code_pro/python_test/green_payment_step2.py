# green_payment_step2.py
from decimal import Decimal


class PaymentResult:
    def __init__(self, success: bool, amount: Decimal):
        self.success = success
        self.amount = amount

    def __repr__(self):
        return f"PaymentResult(success={self.success}, amount={self.amount})"


class PaymentProcessor:
    """GREEN 단계 확장: 카드 + 은행 이체만 최소 구현"""

    def process_card_payment(self, amount: Decimal, card_number: str) -> PaymentResult:
        return PaymentResult(success=True, amount=amount)

    def process_bank_transfer(self, amount: Decimal, account: str) -> PaymentResult:
        return PaymentResult(success=True, amount=amount)


# ----------------------
# 실행 예시
# ----------------------
if __name__ == "__main__":
    processor = PaymentProcessor()

    print(processor.process_card_payment(Decimal("10000"), "1234-5678"))
    print(processor.process_bank_transfer(Decimal("50000"), "110-123-456789"))
