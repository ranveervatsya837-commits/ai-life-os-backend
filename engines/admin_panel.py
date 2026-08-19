import json


class AdminPanel:

    def __init__(self):
        pass

    def get_total_users(self):

        try:
            with open("data/users.json", "r") as file:
                users = json.load(file)

            return len(users)

        except:
            return 0

    def get_total_appointments(self):

        try:
            with open("data/appointments.json", "r") as file:
                appointments = json.load(file)

            return len(appointments)

        except:
            return 0

    def show_system_stats(self):

        print("\n========== ADMIN PANEL ==========")
        print("Total Users:", self.get_total_users())
        print("Total Appointments:", self.get_total_appointments())

    def view_all_users(self):

        try:
            with open("data/users.json", "r") as file:
                users = json.load(file)

            print("\n========== USER DATABASE ==========")

            for index, user in enumerate(users, start=1):

                print(f"\nUser #{index}")
                print("-" * 30)
                print("Name:", user.get("name"))
                print("Age:", user.get("age"))
                print("Health Score:", user.get("health_score"))

            print(f"\nTotal Users: {len(users)}")

        except Exception as error:
            print("Error:", error)

    def view_all_appointments(self):

        try:
            with open("data/appointments.json", "r") as file:
                appointments = json.load(file)

            print("\n========== APPOINTMENT DATABASE ==========")

            for index, appointment in enumerate(appointments, start=1):

                print(f"\nAppointment #{index}")
                print("-" * 40)
                print("Patient :", appointment.get("patient"))
                print("Doctor  :", appointment.get("doctor"))
                print("Hospital:", appointment.get("hospital"))
                print("Date    :", appointment.get("date"))
                print("Time    :", appointment.get("time"))
                print("Token   :", appointment.get("token"))
                print("Status  :", appointment.get("status"))

            print(f"\nTotal Appointments: {len(appointments)}")

        except Exception as error:
            print("Error:", error)

    def show_health_statistics(self):

        try:
            with open("data/users.json", "r") as file:
                users = json.load(file)

            total_score = sum(user.get("health_score", 0) for user in users)
            average_score = total_score / len(users)

            print("\n========== HEALTH STATISTICS ==========")
            print("Total Users:", len(users))
            print("Average Health Score:", round(average_score, 2))

        except Exception as error:
            print("Error:", error)

    def show_top_doctors(self):

        try:
            with open("data/appointments.json", "r") as file:
                appointments = json.load(file)

            doctor_count = {}

            for appointment in appointments:

                doctor = appointment.get("doctor", "").strip()

                if doctor in doctor_count:
                    doctor_count[doctor] += 1
                else:
                    doctor_count[doctor] = 1

            print("\n========== TOP DOCTORS ==========")

            sorted_doctors = sorted(
                doctor_count.items(),
                key=lambda item: item[1],
                reverse=True
            )

            for doctor, count in sorted_doctors:
                print(f"{doctor} : {count} Appointments")

        except Exception as error:
            print("Error:", error)

    def show_active_users(self):

        try:
            with open("data/appointments.json", "r") as file:
                appointments = json.load(file)

            user_count = {}

            for appointment in appointments:

                patient = appointment.get("patient", "").strip()

                if patient in user_count:
                    user_count[patient] += 1
                else:
                    user_count[patient] = 1

            print("\n========== ACTIVE USERS ==========")

            sorted_users = sorted(
                user_count.items(),
                key=lambda item: item[1],
                reverse=True
            )

            for user, count in sorted_users:
                print(f"{user} : {count} Appointments")

        except Exception as error:
            print("Error:", error)

    def show_revenue_report(self):

        try:
            with open("data/appointments.json", "r") as file:
                appointments = json.load(file)

            total_revenue = 0
            hospital_revenue = {}

            for appointment in appointments:

                fee = appointment.get("fee", 0)
                hospital = appointment.get("hospital", "Unknown")

                total_revenue += fee

                if hospital in hospital_revenue:
                    hospital_revenue[hospital] += fee
                else:
                    hospital_revenue[hospital] = fee

            print("\n========== REVENUE REPORT ==========")

            print("Total Appointments :", len(appointments))
            print("Total Revenue      : ₹", total_revenue)

            print("\nHospital Revenue Breakdown")
            print("-" * 40)

            sorted_hospitals = sorted(
                hospital_revenue.items(),
                key=lambda item: item[1],
                reverse=True
            )

            for hospital, revenue in sorted_hospitals:
                print(f"{hospital} : ₹{revenue}")

        except Exception as error:
            print("Error:", error)

    def show_best_doctors(self):

        try:
            with open("data/appointments.json", "r") as file:
                appointments = json.load(file)

            doctor_ratings = {}

            for appointment in appointments:

                doctor = appointment.get("doctor", "").strip()
                rating = appointment.get("rating")

                if rating is None:
                    continue

                if doctor not in doctor_ratings:
                    doctor_ratings[doctor] = {
                        "total_rating": 0,
                        "appointments": 0
                    }

                doctor_ratings[doctor]["total_rating"] += rating
                doctor_ratings[doctor]["appointments"] += 1

            print("\n========== BEST DOCTORS ==========")

            doctor_rankings = []

            for doctor, data in doctor_ratings.items():
                average_rating = (
                        data["total_rating"] /
                        data["appointments"]
                )

                doctor_rankings.append(
                    (
                        doctor,
                        round(average_rating, 2),
                        data["appointments"]
                    )
                )

            doctor_rankings.sort(
                key=lambda item: item[1],
                reverse=True
            )

            for rank, doctor_data in enumerate(
                    doctor_rankings,
                    start=1
            ):
                doctor = doctor_data[0]
                rating = doctor_data[1]
                appointments = doctor_data[2]

                print(f"\n#{rank} {doctor}")
                print(f"Average Rating : {rating} ⭐")
                print(f"Appointments   : {appointments}")

        except Exception as error:
            print("Error:", error)

