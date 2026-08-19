import json
import os


class DataManager:

    def __init__(self, file_path="data/users.json"):
        self.file_path = file_path

    def save_user(self, user_data):
        users = self.load_users()

        users.append(user_data)

        with open(self.file_path, "w") as file:
            json.dump(users, file, indent=4)

        print("User data saved successfully!")

    def load_users(self):
        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, "r") as file:
            return json.load(file)

    def update_user(self, name, key, new_value):
        users = self.load_users()

        for user in users:
            if user["name"] == name:
                user[key] = new_value

                with open(self.file_path, "w") as file:
                    json.dump(users, file, indent=4)

                print("User data updated successfully!")
                return True

        print("User not found!")
        return False

    def delete_user(self, name):
        users = self.load_users()

        for user in users:
            if user["name"] == name:
                users.remove(user)

                with open(self.file_path, "w") as file:
                    json.dump(users, file, indent=4)

                print("User deleted successfully!")
                return True

        print("User not found!")
        return False

    def find_user(self, name):
        users = self.load_users()

        for user in users:
            if user["name"] == name:
                return user

        return None





