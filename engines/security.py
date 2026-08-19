import secrets
from datetime import datetime


class SecuritySystem:

    def __init__(self, user):
        self.user = user
        self.access_token = None

    def generate_access_token(self):
        self.access_token = secrets.token_hex(16)
        return self.access_token

    def verify_user(self):
        return self.user is not None

    def create_audit_log(self, action):
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        print("\n=== Security Audit Log ===")
        print("User:", self.user.name)
        print("Action:", action)
        print("Time:", timestamp)