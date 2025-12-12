# GuitarSpec 클래스: 기타의 세부 스펙 관리
class GuitarSpec:
    def __init__(self, price: float, maker: str, model: str,
                 top_wood: str, back_wood: str, string_num: int):
        self.price = price
        self.maker = maker
        self.model = model
        self.top_wood = top_wood
        self.back_wood = back_wood
        self.string_num = string_num

    # getter methods
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
        return (f"GuitarSpec(maker={self.maker}, model={self.model}, "
                f"price={self.price}, top_wood={self.top_wood}, "
                f"back_wood={self.back_wood}, strings={self.string_num})")


# Guitar 클래스: 기타의 고유 식별자 관리
class Guitar:
    def __init__(self, serial_number: str, spec: GuitarSpec):
        self.serial_number = serial_number
        self.spec = spec  # GuitarSpec 객체 포함 (Composition)

    def get_serial_number(self) -> str:
        return self.serial_number

    def get_spec(self) -> GuitarSpec:
        return self.spec

    def __str__(self):
        return f"Guitar(serial_number={self.serial_number}, spec={self.spec})"


# 사용 예시
if __name__ == "__main__":
    spec = GuitarSpec(
        price=1500.0,
        maker="Fender",
        model="Stratocaster",
        top_wood="Maple",
        back_wood="Alder",
        string_num=6
    )

    guitar = Guitar(serial_number="A12345", spec=spec)

    print("Guitar Info")
    print("Serial Number:", guitar.get_serial_number())
    print("Maker:", guitar.get_spec().get_maker())
    print("Model:", guitar.get_spec().get_model())
    print("Price:", guitar.get_spec().get_price())
