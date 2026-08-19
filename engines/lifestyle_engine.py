class LifestyleEngine:

    def __init__(self, user):
        self.user = user

    def calculate_lifestyle_score(self):
        score = 0

        # Mood
        if self.user.mood in ["good", "nice"]:
            score += 1

        # Sleep
        if self.user.sleep >= 7:
            score += 1

        # Water
        if self.user.water == "yes":
            score += 1

        # Exercise
        if self.user.exercise == "yes":
            score += 1

        return score

    def show_lifestyle_score(self):
        score = self.calculate_lifestyle_score()

        print("\n--- Lifestyle Score ---")
        print("Lifestyle Score:", score, "/ 4")

# @app.get("/appointments/doctor/{doctor_name}")
# def get_doctor_appointments(doctor_name: str):
#             connection = get_connection()
#             cursor = connection.cursor()
#
#             cursor.execute(
#                 """
#                 SELECT *
#                 FROM appointments
#                 WHERE LOWER(doctor) = LOWER(?)
#                 """,
#                 (doctor_name,)
#             )
#
#             appointments = [
#                 dict(row)
#                 for row in cursor.fetchall()
#             ]
#
#             connection.close()
#
#             return appointments