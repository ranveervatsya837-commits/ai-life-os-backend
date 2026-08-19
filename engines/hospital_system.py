class HospitalSystem:

    def __init__(self, doctor_type):
        self.doctor_type = doctor_type

    def recommend_hospital(self):

        if self.doctor_type == "Psychologist":
            return "MindCare Mental Health Hospital"

        elif self.doctor_type == "Nutritionist":
            return "Healthy Life Nutrition Center"

        elif self.doctor_type == "Dietitian":
            return "Wellness Diet Clinic"

        elif self.doctor_type == "Sleep Specialist":
            return "Sleep Care Institute"

        elif self.doctor_type == "General Physician":
            return "City General Hospital"

        else:
            return "AI LIFEOS Health Center"