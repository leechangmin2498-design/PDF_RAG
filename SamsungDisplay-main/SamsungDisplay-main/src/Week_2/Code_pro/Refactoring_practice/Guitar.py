class Guitar:
    def __init__(self, serial_number: str, price: float, maker: str, model: str,
                 top_wood: str, back_wood: str, string_num: int):
        self.serial_number = serial_number
        self.price = price
        self.maker = maker
        self.model = model
        self.top_wood = top_wood
        self.back_wood = back_wood
        self.string_num = string_num

    # getter methods
    def get_serial_number(self) -> str:
        return self.serial_number

    def get_price(self) -> float:
        return self.price

    def get_maker(self) -> str:
        return self.maker

    def get_model(self) -> str:
        return self.model

    def get_top_wood(self) -> str:
        return self.top_wood

    def get_back_wood(self) -> str:
        return self.back_wood

    def get_string_num(self) -> int:
        return self.string_num

    def __str__(self):
        return (f"Guitar(serial_number={self.serial_number}, maker={self.maker}, "
                f"model={self.model}, price={self.price}, "
                f"top_wood={self.top_wood}, back_wood={self.back_wood}, "
                f"strings={self.string_num})")


if __name__ == "__main__":
    my_guitar = Guitar(
        serial_number="A12345",
        price=1500.0,
        maker="Fender",
        model="Stratocaster",
        top_wood="Maple",
        back_wood="Alder",
        string_num=6
    )

    print(my_guitar)
    print("Maker:", my_guitar.get_maker())
    print("Top wood:", my_guitar.get_top_wood())
