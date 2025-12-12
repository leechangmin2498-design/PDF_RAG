class Bird:
    def fly(self):
        print("새가 날고 있습니다.")


class Sparrow(Bird):
    def fly(self):
        print("참새가 날고 있습니다.")


class Ostrich(Bird):
    def fly(self):
        # ❌ 타조는 날 수 없는데, 상속받은 fly() 메서드로 인해 논리적 오류 발생
        raise Exception("타조는 날 수 없습니다!")


def make_bird_fly(bird: Bird):
    bird.fly()


if __name__ == "__main__":
    sparrow = Sparrow()
    ostrich = Ostrich()

    make_bird_fly(sparrow)   # ✅ 정상 작동
    make_bird_fly(ostrich)   # ❌ LSP 위반 - 예외 발생
