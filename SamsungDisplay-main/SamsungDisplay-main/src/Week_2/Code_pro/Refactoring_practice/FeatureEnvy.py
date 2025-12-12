class Address:
    def __init__(self, street, city, zip_code):
        self.street = street
        self.city = city
        self.zip_code = zip_code


class Customer:
    def __init__(self, name, address):
        self.name = name
        self.address = address


class Invoice:
    def print_customer_info(self, customer):
        # Address 데이터를 과도하게 직접 사용
        address = customer.address
        print("Customer Address:")
        print(f"{address.street}, {address.city} {address.zip_code}")




address = Address("123 Main St", "Seoul", "12345")
customer = Customer("Alice", address)
invoice = Invoice()
invoice.print_customer_info(customer)
