from abc import ABC, abstractmethod


# 상위 추상화 계층 (Interface)
class MessageService(ABC):
    @abstractmethod
    def send_message(self, recipient: str, content: str):
        pass


# 구체적 구현 1: EmailService
class EmailService(MessageService):
    def send_message(self, recipient: str, content: str):
        print(f"[이메일 전송] 받는 사람: {recipient}, 내용: {content}")


# 구체적 구현 2: SMSService
class SMSService(MessageService):
    def send_message(self, recipient: str, content: str):
        print(f"[SMS 전송] 받는 사람: {recipient}, 내용: {content}")


# 상위 모듈: Notification — 구체 클래스가 아닌 추상 인터페이스에 의존함
class Notification:
    def __init__(self, message_service: MessageService):
        self.message_service = message_service  # 추상화에 의존

    def notify_user(self, user: str, message: str):
        self.message_service.send_message(user, message)


# DIP Demo
def main():
    email_service = EmailService()
    sms_service = SMSService()

    # Email 기반 알림
    email_notifier = Notification(email_service)
    email_notifier.notify_user("alice@example.com", "이메일 알림이 도착했습니다!")

    # SMS 기반 알림
    sms_notifier = Notification(sms_service)
    sms_notifier.notify_user("010-1234-5678", "문자 알림이 도착했습니다!")


if __name__ == "__main__":
    main()
