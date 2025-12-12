from abc import ABC, abstractmethod


# 1. 기본 인터페이스: 모든 동물이 공통적으로 수행하는 행동
class BasicAnimalActions(ABC):
    @abstractmethod
    def eat(self):
        pass

    @abstractmethod
    def sleep(self):
        pass


# 2. 수영 가능한 동물 인터페이스
class SwimmingAnimalActions(ABC):
    @abstractmethod
    def swim(self):
        pass


#  3. 날 수 있는 동물 인터페이스
class FlyingAnimalActions(ABC):
    @abstractmethod
    def fly(self):
        pass


# Fish: 수영할 수 있는 동물
class Fish(BasicAnimalActions, SwimmingAnimalActions):
    def eat(self):
        print("물고기가 먹고 있습니다.")

    def sleep(self):
        print("물고기가 잠자고 있습니다.")

    def swim(self):
        print("물고기가 헤엄치고 있습니다.")


# Dog: 수영하지 않지만 기본 행동만 수행
class Dog(BasicAnimalActions):
    def eat(self):
        print("개가 밥을 먹고 있습니다.")

    def sleep(self):
        print("개가 잠을 잡니다.")


# Bird: 날 수 있는 동물
class Bird(BasicAnimalActions, FlyingAnimalActions):
    def eat(self):
        print("새가 벌레를 먹고 있습니다.")

    def sleep(self):
        print("새가 나뭇가지 위에서 잠듭니다.")

    def fly(self):
        print("새가 하늘을 날고 있습니다.")


# ISP 원칙 데모 (ISP Demo)
def main():
    animals = [Fish(), Dog(), Bird()]

    for animal in animals:
        print(f"\n[{animal.__class__.__name__}]")
        animal.eat()
        animal.sleep()

        if isinstance(animal, SwimmingAnimalActions):
            animal.swim()
        if isinstance(animal, FlyingAnimalActions):
            animal.fly()


if __name__ == "__main__":
    main()
