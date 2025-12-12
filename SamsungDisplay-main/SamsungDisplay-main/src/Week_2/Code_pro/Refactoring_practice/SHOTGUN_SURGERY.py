class Item:
    def __init__(self, price):
        self.price = price


class Order:
    def __init__(self, items):
        self.items = items
        self.base_discount = 0.1  # ❌ Order보다는 Item에 더 관련된 필드

    def calculate_total_price(self):
        total = 0
        for item in self.items:
            total += item.price - (item.price * self.base_discount)
        return total
