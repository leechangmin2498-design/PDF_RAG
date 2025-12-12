# main.py

from user_service_4 import UserService

if __name__ == "__main__":
    service = UserService()

    print(service.get_user_full_name("Dae-Kyung", "Kim"))
    print(service.get_admin_full_name("Admin", "Lee"))
