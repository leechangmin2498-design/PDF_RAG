class UserService:
    def get_user_full_name(self, first_name: str, last_name: str) -> str:
        return first_name + " " + last_name


# 동작 테스트용 코드
if __name__ == "__main__":
    service = UserService()

    # 입력값
    first = "Gil-Dong"
    last = "Hong"

    # 메서드 호출
    full_name = service.get_user_full_name(first, last)

    print("Full Name:", full_name)
