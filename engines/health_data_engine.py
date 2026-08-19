class HealthDataEngine:

    def __init__(self, user):
        self.user = user

    def collect_health_data(self):
        health_data = {
            "name": self.user.name,
            "age": self.user.age,
            "mood": self.user.mood,
            "sleep": self.user.sleep,
            "water": self.user.water,
            "exercise": self.user.exercise
        }

        return health_data

    def calculate_bmi(self):

        # Convert height from feet to meters
        height_m = self.user.height * 0.3048

        bmi = self.user.weight / (height_m ** 2)

        print(f"BMI: {bmi:.2f}")

        return bmi

    def show_health_data(self):
        data = self.collect_health_data()

        print("\n--- Health Data ---")
        print("Name:", data["name"])
        print("Age:", data["age"])
        print("Mood:", data["mood"])
        print("Sleep:", data["sleep"])
        print("Water:", data["water"])
        print("Exercise:", data["exercise"])
        bmi = self.calculate_bmi()
        print("BMI:", bmi)
        print("\n---BMI---")
        if bmi < 18.5:
            print("status: underweight")
        elif bmi < 25:
            print("status: normal")
        elif bmi < 30:
            print("status: overweight")
        else:
            print("status: obese")
