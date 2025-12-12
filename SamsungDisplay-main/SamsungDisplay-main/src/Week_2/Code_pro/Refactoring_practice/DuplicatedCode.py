def print_order_details(order):
    print("Order Summary:")
    total = 0

    # 총액 계산 로직 (길고 반복될 가능성 있음)
    for item in order['items']:
        total += item['price']

    print("Total Price:", total)
