# 상위 클래스: 모든 현악기의 공통 속성
class StringInstrument:
    def __init__(self, serial_number: str, spec):
        self.serial_number = serial_number
        self.spec = spec  # Composition (StringInstrumentSpec 또는 하위 클래스)

    def get_serial_number(self) -> str:
        return self.serial_number

    def get_spec(self):
        return self.spec


# 악기 스펙 상위 클래스
class StringInstrumentSpec:
    def __init__(self, price: float, maker: str, model: str,
                 top_wood: str, back_wood: str, string_num: int):
        self.price = price
        self.maker = maker
        self.model = model
        self.top_wood = top_wood
        self.back_wood = back_wood
        self.string_num = string_num

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
        return (f"{self.__class__.__name__}(maker={self.maker}, model={self.model}, "
                f"price={self.price}, strings={self.string_num})")


# 개별 악기 스펙 (확장 가능)
class GuitarSpec(StringInstrumentSpec):
    pass


class ViolinSpec(StringInstrumentSpec):
    pass


class CelloSpec(StringInstrumentSpec):
    pass


# 구체 악기 클래스 (확장 가능)
class Guitar(StringInstrument):
    pass


class Violin(StringInstrument):
    pass


class Cello(StringInstrument):
    pass


# 사용 예시
if __name__ == "__main__":
    # 각 악기 스펙 정의
    guitar_spec = GuitarSpec(1500.0, "Fender", "Stratocaster", "Maple", "Alder", 6)
    violin_spec = ViolinSpec(4000.0, "Yamaha", "ClassicV", "Spruce", "Maple", 4)
    cello_spec = CelloSpec(6000.0, "Stradivarius", "SoloMaster", "Spruce", "Willow", 4)

    # 각 악기 생성
    guitar = Guitar("G123", guitar_spec)
    violin = Violin("V456", violin_spec)
    cello = Cello("C789", cello_spec)

    # 출력
    for instrument in [guitar, violin, cello]:
        print(f"{instrument.__class__.__name__}")
        print(f"Serial Number: {instrument.get_serial_number()}")
        print(f"Spec: {instrument.get_spec()}\n")
