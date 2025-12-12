# user_service.py

from name_formatter_4 import NameFormatter

class UserService:
    def get_user_full_name(self, first_name: str, last_name: str) -> str:
        return NameFormatter.format_full_name(first_name, last_name)

    def get_admin_full_name(self, first_name: str, last_name: str) -> str:
        return NameFormatter.format_full_name(first_name, last_name)
