class DoctorSystem:

    def __init__(self, user, bmi, lifestyle_score):
        self.user = user
        self.bmi = bmi
        self.lifestyle_score = lifestyle_score

    def recommend_doctor(self):

        if self.user.mood.lower() in ["sad", "stressed"]:
            return "Psychologist"

        elif self.bmi < 18.5:
            return "Nutritionist"

        elif self.bmi > 25:
            return "Dietitian"

        elif self.lifestyle_score < 2:
            return "General Physician"

        else:
            return "No doctor consultation needed"