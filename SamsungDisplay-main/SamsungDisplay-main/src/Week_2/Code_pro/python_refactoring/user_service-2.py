class UserService:
    def get_user_full_name(self, first_name: str, last_name: str) -> str:
        return first_name + " " + last_name

    def get_admin_full_name(self, first_name: str, last_name: str) -> str:
        return first_name + " " + last_name


# 실행 테스트
if __name__ == "__main__":
    service = UserService()

    # 사용자 이름 테스트
    user_full_name = service.get_user_full_name("Dae-Kyung", "Kim")
    print("User Full Name:", user_full_name)

    # 관리자 이름 테스트
    admin_full_name = service.get_admin_full_name("Admin", "Kim")
    print("Admin Full Name:", admin_full_name)
