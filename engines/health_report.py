class ReportSystem:

    def __init__(self, user, bmi, lifestyle_score):
        self.user = user
        self.bmi = bmi
        self.lifestyle_score = lifestyle_score

    def generate_report(self):

        print("\n=== Health Report ===")
        print("Name:", self.user.name)
        print("BMI:", round(self.bmi, 2))
        print("Lifestyle Score:", self.lifestyle_score, "/ 4")

        if self.bmi < 18.5:
            print("BMI Status: Underweight")
        elif self.bmi < 25:
            print("BMI Status: Normal")
        else:
            print("BMI Status: Overweight")