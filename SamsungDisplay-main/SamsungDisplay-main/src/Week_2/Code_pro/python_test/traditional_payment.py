# traditional_payment.py
from decimal import Decimal


class PaymentResult:
    def __init__(self, success: bool, amount: Decimal):
        self.success = success
        self.amount = amount

    def __repr__(self):
        return f"PaymentResult(success={self.success}, amount={self.amount})"


class TraditionalPaymentProcessor:
    """초기부터 모든 결제 방식을 한 클래스에 넣는 전통적 방식"""

    def process_payment(
        self,
        amount: Decimal,
        method: str,
        card_number: str = None,
        bank_account: str = None,
        crypto_wallet: str = None,
        paypal_email: str = None,
        apple_token: str = None,
        google_token: str = None
    ) -> PaymentResult:

        if method == "card":
            if not card_number:
                raise ValueError("Card number required")
            # (여기 100줄의 카드 결제 검증 로직이 있다고 가정)
            return PaymentResult(True, amount)

        elif method == "bank_transfer":
            if not bank_account:
                raise ValueError("Bank account required")
            # (여기 80줄의 은행 이체 로직이 있다고 가정)
            return PaymentResult(True, amount)

        elif method == "crypto":
            if not crypto_wallet:
                raise ValueError("Crypto wallet required")
            return PaymentResult(True, amount)

        elif method == "paypal":
            if not paypal_email:
                raise ValueError("PayPal email required")
            return PaymentResult(True, amount)

        elif method == "apple_pay":
            if not apple_token:
                raise ValueError("ApplePay token required")
            return PaymentResult(True, amount)

        elif method == "google_pay":
            if not google_token:
                raise ValueError("GooglePay token required")
            return PaymentResult(True, amount)

        else:
            raise ValueError(f"Unknown payment method: {method}")


# --------------------------
# 실행 테스트
# --------------------------
if __name__ == "__main__":
    processor = TraditionalPaymentProcessor()
    result = processor.process_payment(
        amount=Decimal("10000"),
        method="card",
        card_number="1111-2222-3333-4444"
    )
    print(result)
