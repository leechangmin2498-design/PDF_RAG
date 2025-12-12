class UserService:
    def _format_full_name(self, first_name: str, last_name: str) -> str:
        return first_name + " " + last_name

    def get_user_full_name(self, first_name: str, last_name: str) -> str:
        return self._format_full_name(first_name, last_name)

    def get_admin_full_name(self, first_name: str, last_name: str) -> str:
        return self._format_full_name(first_name, last_name)


# 실행 테스트
if __name__ == "__main__":
    service = UserService()

    # 사용자 이름 테스트
    print(service.get_user_full_name("Dae-Kyung", "Kim"))

    # 관리자 이름 테스트
    print(service.get_admin_full_name("Admin", "Lee"))
