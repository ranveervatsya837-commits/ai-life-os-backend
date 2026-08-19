import json
import random


class AppointmentSystem:

    DOCTOR_FEES = {
        "Nutritionist": 500,
        "Psychologist": 800,
        "General Physician": 400
    }

    AVAILABLE_SLOTS = {
        "1": "10:00 AM",
        "2": "11:00 AM",
        "3": "12:00 PM",
        "4": "02:00 PM"
    }

    def __init__(self, user, doctor, hospital):
        self.user = user
        self.doctor = doctor
        self.hospital = hospital

    def save_appointment(self, appointment):

        try:
            with open("data/appointments.json", "r") as file:
                appointments = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):
            appointments = []

        appointments.append(appointment)

        with open("data/appointments.json", "w") as file:
            json.dump(appointments, file, indent=4)

        print("\nAppointment saved successfully!")

    def get_appointment_history(self):

        try:
            with open("data/appointments.json", "r") as file:
                return json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def display_appointment_history(self):

        appointments = self.get_appointment_history()

        if not appointments:
            print("\nNo appointment history found.")
            return

        print("\n========== APPOINTMENT HISTORY ==========")

        for index, appointment in enumerate(appointments, start=1):

            print(f"\nAppointment #{index}")
            print("-" * 40)
            print(f"Patient : {appointment.get('patient')}")
            print(f"Doctor  : {appointment.get('doctor')}")
            print(f"Hospital: {appointment.get('hospital')}")
            print(f"Date    : {appointment.get('date')}")
            print(f"Time    : {appointment.get('time')}")
            print(f"Token   : {appointment.get('token')}")
            print(f"Status  : {appointment.get('status')}")
            print(f"Fee     : ₹ {appointment.get('fee')}")
            print(f"Rating  : ⭐ {appointment.get('rating', 'N/A')}")

    def get_rating(self):

        while True:

            try:
                rating = int(input("Rate Doctor (1-5): "))

                if 1 <= rating <= 5:
                    return rating

                print("Please enter a rating between 1 and 5.")

            except ValueError:
                print("Please enter a valid number.")

    def get_slot(self):

        print("\nAvailable Slots:")

        for key, value in self.AVAILABLE_SLOTS.items():
            print(f"{key}. {value}")

        choice = input("Select Slot (1-4): ")

        return self.AVAILABLE_SLOTS.get(choice, "10:00 AM")

    def get_consultation_fee(self):

        return self.DOCTOR_FEES.get(self.doctor, 300)

    def generate_token(self):

        return f"AIL-{random.randint(1000, 9999)}"

    def book_appointment(self):

        appointment_date = input(
            "\nEnter Appointment Date (DD-MM-YYYY): "
        )

        appointment_time = self.get_slot()

        fee = self.get_consultation_fee()

        rating = self.get_rating()

        appointment = {
            "patient": self.user.name,
            "doctor": self.doctor,
            "hospital": self.hospital,
            "date": appointment_date,
            "time": appointment_time,
            "token": self.generate_token(),
            "status": "Confirmed",
            "fee": fee,
            "rating": rating
        }

        self.save_appointment(appointment)

        print("\n========== APPOINTMENT DETAILS ==========")
        print("Patient          :", appointment["patient"])
        print("Doctor           :", appointment["doctor"])
        print("Hospital         :", appointment["hospital"])
        print("Date             :", appointment["date"])
        print("Time             :", appointment["time"])
        print("Token            :", appointment["token"])
        print("Status           :", appointment["status"])
        print("Consultation Fee : ₹", appointment["fee"])
        print("Doctor Rating    : ⭐", appointment["rating"])

        return appointment