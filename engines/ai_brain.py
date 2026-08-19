class AIBrain:

    def __init__(self, user, lifestyle_score, bmi):
        self.user = user
        self.lifestyle_score = lifestyle_score
        self.bmi = bmi

    def generate_recommendations(self):

        recommendations = []

        # Mood Analysis
        if self.user.mood.lower() in ["happy", "good"]:
            recommendations.append(
                "Great! Keep maintaining your positive mindset."
            )

        elif self.user.mood.lower() == "sad":
            recommendations.append(
                "Try talking to friends or doing activities you enjoy."
            )

        elif self.user.mood.lower() in ["stressed", "bad"]:
            recommendations.append(
                "Take short breaks and practice deep breathing."
            )

        # Sleep Analysis
        if self.user.sleep < 7:
            recommendations.append(
                "Try to sleep at least 7-8 hours daily."
            )

        # Water Analysis
        if self.user.water.lower() == "no":
            recommendations.append(
                "Increase your daily water intake."
            )

        # Exercise Analysis
        if self.user.exercise.lower() == "no":
            recommendations.append(
                "Add at least 20-30 minutes of physical activity."
            )

        # BMI Analysis
        if self.bmi < 18.5:
            recommendations.append(
                "You appear underweight. Consider a nutrition plan."
            )

        elif self.bmi > 25:
            recommendations.append(
                "You appear overweight. Focus on exercise and balanced meals."
            )

        # Lifestyle Score Analysis
        if self.lifestyle_score < 2:
            recommendations.append(
                "Your lifestyle score is low. Focus on sleep, water and exercise."
            )

        return recommendations