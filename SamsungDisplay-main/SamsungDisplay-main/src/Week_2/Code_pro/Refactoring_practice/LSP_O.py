from abc import ABC, abstractmethod

# 1️⃣ 공통 상위 클래스: 모든 새의 기본 행동 정의
class Bird(ABC):
    def eat(self):
        print("새가 먹고 있습니다.")


# 2️⃣ 날 수 있는 새만 구현할 인터페이스 (추상 클래스)
class Flyable(ABC):
    @abstractmethod
    def fly(self):
        pass


# 3️⃣ 실제 새 클래스들
class Sparrow(Bird, Flyable):
    def fly(self):
        print("참새가 날고 있습니다.")


class Ostrich(Bird):  # ❌ Flyable을 상속하지 않음
    def run(self):
        print("타조가 달리고 있습니다.")


# 4️⃣ LSP 준수 테스트 함수
def make_bird_move(bird: Bird):
    bird.eat()  # 모든 새가 공통으로 먹을 수 있음

    if isinstance(bird, Flyable):
        bird.fly()  # 날 수 있는 새만 fly() 호출
    else:
        print("이 새는 날지 않습니다.")


# 5️⃣ 실행 예시
if __name__ == "__main__":
    sparrow = Sparrow()
    ostrich = Ostrich()

    print("🕊️ [참새 행동]")
    make_bird_move(sparrow)

    print("\n🐦 [타조 행동]")
    make_bird_move(ostrich)
