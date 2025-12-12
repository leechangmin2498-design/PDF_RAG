class Employee:
    def __init__(self, name, address, phone_number):
        self.name = name
        self.address = address
        self.phone_number = phone_number

    def get_contact_info(self):
        return f"{self.address}, {self.phone_number}"
