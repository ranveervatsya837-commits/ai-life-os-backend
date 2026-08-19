import json
from models.user import User
from engines.lifestyle_engine import LifestyleEngine
from engines.health_data_engine import HealthDataEngine
from data.data_manager import DataManager
from data.data_manager import DataManager
from engines.ai_brain import AIBrain
from engines.doctor_system import DoctorSystem
from engines.hospital_system import HospitalSystem
from engines.appointment_system import AppointmentSystem
from engines.emergency_system import EmergencySystem
from engines.health_report import ReportSystem
from engines.health_tips import HealthTips
from engines.security import SecuritySystem
from engines.admin_panel import AdminPanel
from engines.ai_safety import AISafetyLayer
print("Welcome to AI_LIFEOS")
print("your personal health and life style assistant")
name=input("what is your name?")
age=input("what is your age?")
print("Hello",name)
print("Nice to meet you!")
goal=input("what is your main goal today?")
print("your goal is:",goal)
print("AI_LIFEOS is to help you!")
print("Let's make your day better !")
print("I can help you with your daily goals.")
print("Let's get started.")
mood=input("How are you feeling today?")
print("I understand.")
print("Let's work on making your day better !")
print("your goal:",goal)
print("your mood:",mood)
print("Keep going!")
print("AI_LIFEOS is here to support you.")
sleep=float(input("How many  hour did you sleep?"))
water=input("Did you drink enough water today?")
exercise=input("Did you exercise today?")
height=float(input("entre you height"))
weight=float(input("entre you weight"))
print("sleep:",sleep,"hour")
print("water intake:",water)
print("exercise:",exercise)
print("whight:",height)
print("weight:",weight)
print("Great! your daily information is recorded.")
print("Small healthy habits can make a diffrence. ")
print("AI_LIFEOS will help you track your lifestyle.")
print("daily check completed!")
if exercise.lower == "yes":
    print("Great! keep your exercise routine")
else:
    print("try to include some physical activity today.")
    if water.lower()=="yes":
        print("Good job staying hydrated.")
    else:
        print("Remember to drink enough water.")
    if sleep >=7:
        print("Great your sleep duration looks good.")
    else:
        print("Try to get more sleep tonight.")
    if mood.lower()=="good":
        print("That's great! keep you mood relax")
    else:
        print("That's some time to relax and recharge.")
    if exercise.lower()=="no":
            print("A short walk can be good start.")

            print("your daily health check is completed.")
            print("AI_LIFEOS has genrated your basic advice.")
    score=0
    if sleep>=7:
        score+=1
    if water.lower()=="yes":
        score+=1
    if exercise.lower()=="yes":
            score+=1
            print("your health score:",score,"/3")
    if score==3:
        print("Excellent! great daily habits.")
    elif score==2:
        print("Good job! keep improving")
    else:
        print("Let's improve your daily habits")
    if score==3:
        print("Today's plan: keep your current routine.")
        print("Stay consitent with your healthy  habits.")
    elif score==2:
        print("Today's plan  improve  one habits.")
        print("Focous on sleep, water, or exercise.")
    else:
        print("Today's plan: start with one small change.")
        print("Drink water and take a short walk.")
        print("Try to improve your sleep tonight.")
        print("you can build better habits step by step.")
profile={
"names":name,
"age":age,
"mood":mood,
"sleep":sleep,
"water":water,
"exercise":exercise,
"health_score":score,
 "height":height,
 "weight":weight
}
print("\n___ your profile___")
print("Name:",profile["names"])
print("Age:",profile["age"])
print("Mood:",profile["mood"])
print("Sleep:",profile["sleep"])
print("Water:",profile["water"])
print("Exercise:",profile["exercise"])
print("Health Score:",profile["health_score"])
print("height:",profile["height"])
print("weight:",profile["weight"])

with open("profile.json","w") as file:
    json.dump(profile,file,indent=4)
print("profile saved successfully")
with open("profile.json","r") as file:
    saved_profile=json.load(file)
print("\n___ your saved_profile___")
print("Name:",saved_profile["names"])
print("Age:",saved_profile["age"])
print("Health Score:",saved_profile["health_score"])
print("height:",saved_profile["height"])
print("weight:",saved_profile["weight"])
user=User(
    profile["names"],
    profile["age"],
    profile["mood"],
    profile["sleep"],
    profile["water"],
    profile["exercise"],
    profile["health_score"],
    profile["height"],
    profile["weight"]
)
user = User(
    profile["names"],
    profile["age"],
    profile["mood"],
    profile["sleep"],
    profile["water"],
    profile["exercise"],
    profile["health_score"],
    profile["height"],
    profile["weight"]
)
user.calculate_health_score()
print("User object created successfully!")
print("\nUser object created successfully!")
print("User:",user.name)
print("Health Score:",user.health_score)
user.calculate_health_score()

data_manager = DataManager()

user_data = {
    "name": user.name,
    "age": user.age,
    "mood": user.mood,
    "sleep": user.sleep,
    "water": user.water,
    "exercise": user.exercise,
    "health_score": user.health_score,
    "height": user.height,
    "weight": user.weight
}

data_manager.save_user(user_data)
lifestyle = LifestyleEngine(user)

score = lifestyle.calculate_lifestyle_score()
lifestyle.show_lifestyle_score()

health_engine = HealthDataEngine(user)

health_engine.show_health_data()
bmi = health_engine.calculate_bmi()
user_data = {
    "name": user.name,
    "age": user.age,
}
data_manager.update_user(user.name,"mood","great")
data_manager.delete_user(user.name)
found_user = data_manager.find_user(user.name)
print(found_user)
print(data_manager.load_users())
brain = AIBrain(user, score, bmi)

recommendations = brain.generate_recommendations()

print("\n=== AI Recommendations ===")

for rec in recommendations:
    print("-", rec)
print("DEBUG Lifestyle Score:", score)
print("DEBUG BMI:", bmi)
brain = AIBrain(user, score, bmi)
doctor_system = DoctorSystem(user, bmi, score)
doctor = doctor_system.recommend_doctor()
print("\n=== Doctor Recommendation ===")
print("Recommended Doctor:", doctor)
hospital_system = HospitalSystem(doctor)
hospital = hospital_system.recommend_hospital()
print("\n=== Hospital Recommendation ===")
print("Recommended Hospital:", hospital)
appointment_system = AppointmentSystem(
    user,
    doctor,
    hospital
)

appointment = appointment_system.book_appointment()

print("\n=== Appointment Details ===")
print("Patient:", appointment["patient"])
print("Doctor:", appointment["doctor"])
print("Hospital:", appointment["hospital"])
print("Date:", appointment["date"])
print("Time:", appointment["time"])
print("Token:", appointment["token"])
print("Status:", appointment["status"])
print("Consultation Fee: ₹", appointment["fee"])
appointment_system.display_appointment_history()
emergency_system = EmergencySystem(user, bmi)

risk = emergency_system.check_risk()

print("\n=== Emergency Alert ===")
print(risk)
report = ReportSystem(user, bmi, score)
report.generate_report()
tips = HealthTips()

print("\n=== Daily Health Tip ===")
print(tips.get_tip())
security = SecuritySystem(user)

token = security.generate_access_token()

print("\n=== Security Layer ===")
print("Access Token:", token)

if security.verify_user():
    print("User Verification: Success")

security.create_audit_log("Health Report Accessed")
admin = AdminPanel()

admin.show_system_stats()
admin.view_all_users()
admin.view_all_appointments()
safety = AISafetyLayer(user)
safety.generate_safety_report()
admin.show_health_statistics()
admin.show_top_doctors()
admin.show_active_users()
admin.show_revenue_report()
admin.show_best_doctors()

@app.get("/analytics")
def analytics():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) as total_doctors
        FROM doctors
        """
    )
    total_doctors = cursor.fetchone()["total_doctors"]

    cursor.execute(
        """
        SELECT COUNT(*) as total_appointments
        FROM appointments
        """
    )
    total_appointments = cursor.fetchone()["total_appointments"]

    cursor.execute(
        """
        SELECT COALESCE(SUM(fee), 0) as total_revenue
        FROM appointments
        """
    )
    total_revenue = cursor.fetchone()["total_revenue"]

    cursor.execute(
        """
        SELECT COUNT(*) as total_users
        FROM auth_users
        """
    )
    total_users = cursor.fetchone()["total_users"]

    connection.close()

    return {
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "total_revenue": total_revenue,
        "total_users": total_users



@app.get("/doctors")
def get_doctors():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM doctors
    """)

    doctors = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return doctors

@app.get("/doctors")
def get_doctors():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()

    connection.close()

    return doctors