import random

class HealthTips:

    def get_tip(self):

        tips = [
            "Drink at least 2-3 liters of water daily.",
            "Sleep 7-8 hours every night.",
            "Exercise at least 30 minutes a day.",
            "Eat more fruits and vegetables.",
            "Take regular breaks from screens.",
            "Avoid excessive junk food.",
            "Maintain a healthy work-life balance.",
            "Practice stress management techniques."
        ]

        return random.choice(tips)
