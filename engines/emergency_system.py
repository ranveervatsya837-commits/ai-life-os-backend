class EmergencySystem:

    def __init__(self, user, bmi):
        self.user = user
        self.bmi = bmi

    def check_risk(self):

        if self.bmi < 16:
            return "HIGH RISK: Severe Underweight"

        elif self.bmi > 35:
            return "HIGH RISK: Severe Obesity"

        elif self.user.sleep < 5:
            return "WARNING: Poor Sleep Detected"

        elif self.user.mood.lower() == "stressed":
            return "WARNING: Mental Health Support Recommended"

        else:
            return "No Immediate Health Risk"