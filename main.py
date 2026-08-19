from fastapi import FastAPI
from database import get_connection

from auth import (
    hash_password,
    verify_password,
    create_access_token
)
from datetime import datetime
from fastapi import Header
from auth import verify_token
from ollama import chat
from pydantic import BaseModel
from risk_prediction import RiskPredictionEngine
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from health_score import HealthScoreEngine
from health_recommendation import HealthRecommendationEngine
import csv
app = FastAPI()

class AIRequest(BaseModel):
    patient_id: int
    prompt: str

class Doctor(BaseModel):
    name: str
    specialization: str
    experience: int
    consultation_fee: int

class Appointment(BaseModel):
    id: str
    patient: str
    doctor: str
    hospital: str
    date: str
    time: str
    fee: int

class RegisterUser(BaseModel):
        name: str
        email: str
        password: str

class LoginUser(BaseModel):
        email: str
        password: str


class SymptomsRequest(BaseModel):
        symptoms: list[str]

class Patient(BaseModel):
    name: str
    age: int
    gender: str
    blood_group: str
    phone: str
    address: str

class MedicalRecord(BaseModel):
        patient_id: int
        symptoms: str
        diagnosis: str
        treatment: str
        doctor_notes: str

class Prescription(BaseModel):
    patient_id: int
    medicine: str
    dosage: str
    duration: str
    instructions: str


class LabReport(BaseModel):
    patient_id: int
    report_name: str
    report_result: str
    doctor_comments: str

class AIEngine:
    MODEL = "llama3.1:8b"

    SYSTEM_PROMPT ="""
    
    
You are AI LIFEOS, an intelligent healthcare assistant.

Rules:
- Introduce yourself as AI LIFEOS only when necessary.
- Do not repeat the introduction within the same response.
- Never repeat closing statements or self-introductions.
- Always introduce yourself as AI LIFEOS when relevant.
- Never mention Qwen, Ollama, Alibaba, or being a language model.
- Never provide a definite diagnosis.
- Fever, cough, pain, fatigue, and similar symptoms should be explained primarily by likely acute illnesses or conditions.
- Do not assume a chronic disease is the cause of the reported symptoms.
- Chronic diseases should only be mentioned as risk factors or considerations unless the symptoms strongly suggest a direct complication.
- Do not suggest specific complications (such as diabetic ketoacidosis) unless the reported symptoms support that possibility.
- Avoid unnecessary speculation.
- Keep the "Possible Causes" section focused on the most likely explanations based on the symptoms provided.
- First determine whether the user is reporting symptoms or only sharing a medical condition.
- If no symptoms are reported, do NOT generate a "Possible Causes" section.
- Do not assume fever, cough, pain, infection, fatigue, or any other symptoms unless explicitly mentioned.
- If the user only mentions a condition such as diabetes, hypertension, asthma, or thyroid disease, provide condition-specific guidance instead of symptom analysis.

 Use patient gender when generating recommendations.
- Never mention pregnancy unless the patient is female and pregnancy is relevant.
- Avoid irrelevant risk factors that do not match the patient profile.
- Only discuss conditions that exist in the patient's medical history or are relevant to the symptoms.

- NEVER say that diabetes, hypertension, or other chronic diseases are the direct cause of fever, cough, headache, or pain unless the user explicitly reports a diagnosed complication.

- For fever, cough, sore throat, body pain, or similar symptoms:
  Focus on infections, inflammation, allergies, or other symptom-related causes first.

- Chronic diseases should only be mentioned under risk factors, monitoring advice, or doctor consultation guidance.

- Example:
  Incorrect: "Your fever may be caused by diabetes."
  Correct: "Possible causes may include a viral or bacterial infection. Because you have diabetes, monitoring blood sugar during illness is important."   

- Always use patient age, gender, and medical context when available.
- Personalize recommendations based on patient profile.
- Mention high-risk factors such as diabetes, hypertension,
  old age, pregnancy, or chronic diseases when relevant.

- Use patient information for personalization.
- Do not repeatedly mention the patient's name unless necessary.
- Focus on age, risk factors, and medical context.

- Do not mention the patient's name in the response.
- Use the patient's age, gender, and medical history silently for personalization.
- Refer to the patient as "you" instead of using their name.

- Use phrases such as:
  'Possible causes may include...'
  'These symptoms can be associated with...'

- Give practical health guidance.
- Recommend professional medical care for severe symptoms.

- If symptoms include chest pain, breathing difficulty,
  unconsciousness, stroke signs, or severe bleeding,
  advise emergency medical attention immediately.
  - Do not state that a chronic disease directly causes symptoms unless medically appropriate.
- Distinguish between a condition being a risk factor and being the cause.
- Diabetes, hypertension, and similar conditions should be treated as risk factors, not assumed causes of fever, cough, or pain.
- Base possible causes primarily on the reported symptoms.

- Keep responses concise and easy to understand.
- List only the most likely causes based on the reported symptoms.
- Do not add unlikely conditions unless symptoms support them.
- Avoid long lists of speculative causes.
- Prioritize common and evidence-supported explanations.
- Use age and gender silently for personalization.
- Do not explicitly mention age or gender unless medically relevant.
- Avoid phrases like "As a 28-year-old male" unless the information directly affects the advice.

- First determine whether the user is reporting symptoms or only mentioning a medical condition.

- If symptoms are reported:
  1. Possible Causes
  2. Self-Care Advice
  3. When to See a Doctor

- If no symptoms are reported:
  1. Condition Guidance
  2. Self-Care Advice
  3. Monitoring & Follow-Up

- Do not assume symptoms that were not mentioned.
- Do not invent fever, cough, pain, infection, fatigue, or other symptoms.
- If the user only mentions a condition such as diabetes, hypertension, asthma, or thyroid disease, provide condition-specific guidance instead of symptom analysis.
- If no symptoms are reported, do not refer to symptoms, illness, infection, recovery, or treatment.
- Focus only on condition management, monitoring, prevention, and lifestyle guidance.
"""

    @staticmethod
    def generate(prompt: str, patient, history=None) -> str:
        full_prompt = f"""
        Patient Profile:
        - Age: {patient['age']}
        - Gender: {patient['gender']}
        - Blood Group: {patient['blood_group']}

        Important Instructions:
        - Use this patient profile for personalization.
        - Do not mention the patient's name.
        - Address the patient as "you".
        - Use chronic diseases as risk factors, not automatic causes.
- Focus first on the reported symptoms when listing possible causes.
        - Consider age, gender and any known risk factors.
        - If the patient is young, avoid old-age warnings unless relevant.
        - If the patient has diabetes, hypertension, asthma or other conditions, consider them in advice.
        - Keep the answer practical and concise.
        se the patient's age and gender.
        - Focus on the symptoms provided by the patient.
- Do not invent additional symptoms.
- Mention only causes reasonably supported by the reported symptoms.
      
- Do not treat diabetes as the cause of fever.
- Use diabetes only as a risk factor.
- Focus on symptom-based causes first.
- Do not assume conditions that are not present.
- Do not mention pregnancy for male patients.
- Personalize recommendations based on the available profile only.
Important:
- Use the patient's age and gender.
- Use medical history only when relevant.
- Treat chronic diseases as risk factors, not automatic causes.
- Focus primarily on the symptoms reported by the patient.
- Do not mention conditions that are not present in the patient profile.
 

 Question:
 {prompt}
"""

        messages = [
            {
                "role": "system",
                "content": AIEngine.SYSTEM_PROMPT
            }
        ]

        if history:
            for item in reversed(history):
                messages.append(
                    {
                        "role": item["role"],
                        "content": item["message"]
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": full_prompt
            }
        )
        print("HISTORY:", history)
        print("MESSAGES:", messages)

        response = chat(
            model=AIEngine.MODEL,
            messages=messages
        )

        return response.message.content

@app.get("/admin/analytics")
def analytics(
        authorization: str = Header(None)
):


    print("AUTH HEADER:", authorization)

    if not authorization:
        return {
            "message": "Token missing"
        }

    token = authorization.replace(
        "Bearer ",
        ""
    )

    print("TOKEN:", token)

    payload = verify_token(token)

    print("PAYLOAD:", payload)

    if not payload:
        return {
            "message": "Invalid token"
        }

    if payload.get("role") != "admin":
        return {
            "message": "Admin access required"
        }

    # 👇 YAHAN SE DATABASE CODE START HOGA
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COUNT(*) as total_doctors FROM doctors"
    )
    total_doctors = cursor.fetchone()["total_doctors"]

    cursor.execute(
        "SELECT COUNT(*) as total_appointments FROM appointments"
    )
    total_appointments = cursor.fetchone()["total_appointments"]

    cursor.execute(
        """
        SELECT COUNT(*) as completed_appointments
        FROM appointments
        WHERE status = 'completed'
        """
    )
    completed_appointments = cursor.fetchone()[
        "completed_appointments"
    ]

    cursor.execute(
        """
        SELECT COUNT(*) as cancelled_appointments
        FROM appointments
        WHERE status = 'cancelled'
        """
    )
    cancelled_appointments = cursor.fetchone()[
        "cancelled_appointments"
    ]

    cursor.execute(
        """
        SELECT COUNT(*) as booked_appointments
        FROM appointments
        WHERE status = 'booked'
        """
    )
    booked_appointments = cursor.fetchone()[
        "booked_appointments"
    ]

    cursor.execute(
        "SELECT COALESCE(SUM(fee),0) as total_revenue FROM appointments"
    )
    total_revenue = cursor.fetchone()["total_revenue"]

    cursor.execute(
        "SELECT COUNT(*) as total_users FROM auth_users"
    )
    total_users = cursor.fetchone()
    return {
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "booked_appointments": booked_appointments,
        "total_revenue": total_revenue,
        "total_users": total_users
    }

@app.get("/doctors/search/{specialization}")
def search_doctors(specialization: str):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM doctors
        WHERE specialization = ?
        """,
        (specialization,)
    )

    doctors = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return doctors
@app.get("/doctors/search/{specialization}")
def search_doctors(specialization: str):

    print("SEARCH:", specialization)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM doctors")

    rows = cursor.fetchall()

    print("ROWS:", rows)

    doctors = [
        dict(row)
        for row in rows
    ]

    connection.close()

    return doctors
@app.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: int,
    doctor: Doctor
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE doctors
        SET name = ?,
            specialization = ?,
            experience = ?,
            consultation_fee = ?
        WHERE id = ?
        """,
        (
            doctor.name,
            doctor.specialization,
            doctor.experience,
            doctor.consultation_fee,
            doctor_id
        )
    )

    connection.commit()
    connection.close()

    return {
        "message": "Doctor updated successfully"
    }
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM doctors
        WHERE id = ?
        """,
        (doctor_id,)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Doctor deleted successfully"
    }

@app.post("/appointments")
def create_appointment(appointment: Appointment):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO appointments
        (
            id,
            patient,
            doctor,
            hospital,
            date,
            time,
            fee
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            appointment.id,
            appointment.patient,
            appointment.doctor,
            appointment.hospital,
            appointment.date,
            appointment.time,
            appointment.fee
        )
    )

    connection.commit()
    connection.close()

    return {
        "message": "Appointment created successfully"
    }
@app.get("/appointments")
def get_appointments():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
                   SELECT *
                   FROM appointments
                   """)

    appointments = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return appointments
@app.get("/appointments/{appointment_id}")
def get_appointment(appointment_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM appointments
        WHERE id = ?
        """,
        (appointment_id,)
    )

    appointment = cursor.fetchone()

    connection.close()

    if not appointment:
        return {"message": "Appointment not found"}

    return dict(appointment)
@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM appointments
        WHERE id = ?
        """,
        (appointment_id,)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Appointment deleted successfully"
    }


@app.post("/register")
def register(user: RegisterUser):
        connection = get_connection()
        cursor = connection.cursor()

        hashed_password = hash_password(user.password)

        cursor.execute(
            """
            INSERT INTO auth_users
                (name, email, password, created_at, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user.name,
                user.email,
                hashed_password,
                datetime.now().isoformat(),
                "user"
            )
        )

        connection.commit()
        connection.close()

        return {
            "message": "User registered successfully"
        }
@app.post("/login")
def login(user: LoginUser):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM auth_users
        WHERE email = ?
        """,
        (user.email,)
    )

    db_user = cursor.fetchone()

    connection.close()

    if not db_user:
        return {
            "message": "Invalid credentials"
        }

    if not verify_password(
        user.password,
        db_user["password"]
    ):
        return {
            "message": "Invalid credentials"
        }

    token = create_access_token(
        {
            "sub": user.email,
            "role": db_user["role"]
        }
    )

    return {
        "access_token": token
    }
@app.get("/me")
def get_me(authorization: str = Header(None)):

    if not authorization:
        return {"message": "Token missing"}

    token = authorization.replace(
        "Bearer ",
        ""
    )
    print("AUTH HEADER:", authorization)
    print("TOKEN:", token)
    payload = verify_token(token)

    print("PAYLOAD:", payload)
    payload = verify_token(token)

    if not payload:
        return {
            "message": "Invalid or expired token"
        }

    return {
        "email": payload["sub"],
        "role": payload["role"]
    }
@app.get("/my-appointments")
def my_appointments(
    authorization: str = Header(None)
):

    if not authorization:
        return {
            "message": "Token missing"
        }

    token = authorization.replace(
        "Bearer ",
        ""
    )

    payload = verify_token(token)

    if not payload:
        return {
            "message": "Invalid token"
        }

    email = payload["sub"]

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM auth_users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    if not user:
        connection.close()
        return {
            "message": "User not found"
        }

    cursor.execute(
        """
        SELECT *
        FROM appointments
        WHERE patient = ?
        """,
        (user["name"],)
    )

    appointments = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return appointments

@app.put("/appointments/{appointment_id}/status")
def update_appointment_status(
    appointment_id: str,
    status: str
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE appointments
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            appointment_id
        )
    )

    connection.commit()
    connection.close()

    return {
        "message": "Appointment status updated"
    }


@app.get("/reports/revenue")
def revenue_report():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(fee),0) as total_revenue
        FROM appointments
    """)
    total_revenue = cursor.fetchone()["total_revenue"]

    cursor.execute("""
        SELECT COALESCE(SUM(fee),0) as completed_revenue
        FROM appointments
        WHERE status = 'completed'
    """)
    completed_revenue = cursor.fetchone()["completed_revenue"]

    cursor.execute("""
        SELECT COUNT(*) as completed_appointments
        FROM appointments
        WHERE status = 'completed'
    """)
    completed_appointments = cursor.fetchone()["completed_appointments"]

    cursor.execute("""
        SELECT COUNT(*) as cancelled_appointments
        FROM appointments
        WHERE status = 'cancelled'
    """)
    cancelled_appointments = cursor.fetchone()["cancelled_appointments"]

    connection.close()

    return {
        "total_revenue": total_revenue,
        "completed_revenue": completed_revenue,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments
    }
@app.get("/admin/dashboard")
def admin_dashboard():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) as total_doctors FROM doctors"
    )
    total_doctors = cursor.fetchone()["total_doctors"]

    cursor.execute(
        "SELECT COUNT(*) as total_users FROM auth_users"
    )
    total_users = cursor.fetchone()["total_users"]

    cursor.execute(
        "SELECT COUNT(*) as total_appointments FROM appointments"
    )
    total_appointments = cursor.fetchone()["total_appointments"]

    cursor.execute(
        """
        SELECT COUNT(*) as completed_appointments
        FROM appointments
        WHERE status = 'completed'
        """
    )
    completed_appointments = cursor.fetchone()["completed_appointments"]

    cursor.execute(
        """
        SELECT COUNT(*) as cancelled_appointments
        FROM appointments
        WHERE status = 'cancelled'
        """
    )
    cancelled_appointments = cursor.fetchone()["cancelled_appointments"]

    cursor.execute(
        """
        SELECT COALESCE(SUM(fee),0) as total_revenue
        FROM appointments
        """
    )
    total_revenue = cursor.fetchone()["total_revenue"]

    connection.close()

    return {
        "total_doctors": total_doctors,
        "total_users": total_users,
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
        "total_revenue": total_revenue
    }
@app.post("/ai/recommend")
def ai_recommend(data: SymptomsRequest):

    symptoms = [s.lower() for s in data.symptoms]

    if "fever" in symptoms and "cough" in symptoms:
        return {
            "possible_condition": "Common Cold",
            "recommendation": "Consult a General Physician"
        }

    if "chest pain" in symptoms:
        return {
            "possible_condition": "Heart-related issue",
            "recommendation": "Consult a Cardiologist immediately"
        }

    return {
        "possible_condition": "Unknown",
        "recommendation": "Consult a Doctor"
    }

@app.post("/patients")
def create_patient(patient: Patient):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO patients
        (
            name,
            age,
            gender,
            blood_group,
            phone,
            address
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            patient.name,
            patient.age,
            patient.gender,
            patient.blood_group,
            patient.phone,
            patient.address
        )
    )

    connection.commit()

    patient_id = cursor.lastrowid

    connection.close()

    return {
        "message": "Patient created successfully",
        "patient_id": patient_id
    }
@app.get("/patients")
def get_patients():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM patients
        ORDER BY id DESC
        """
    )

    patients = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return patients
@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM patients
        WHERE id = ?
        """,
        (patient_id,)
    )

    patient = cursor.fetchone()

    connection.close()

    if not patient:
        return {
            "message": "Patient not found"
        }

    return dict(patient)
@app.put("/patients/{patient_id}")
def update_patient(
    patient_id: int,
    patient: Patient
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE patients
        SET
            name = ?,
            age = ?,
            gender = ?,
            blood_group = ?,
            phone = ?,
            address = ?
        WHERE id = ?
        """,
        (
            patient.name,
            patient.age,
            patient.gender,
            patient.blood_group,
            patient.phone,
            patient.address,
            patient_id
        )
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        return {
            "message": "Patient not found"
        }

    connection.close()

    return {
        "message": "Patient updated successfully"
    }
@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM patients
        WHERE id = ?
        """,
        (patient_id,)
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        return {
            "message": "Patient not found"
        }

    connection.close()

    return {
        "message": "Patient deleted successfully"
    }
@app.post("/medical-records")
def create_medical_record(record: MedicalRecord):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO medical_records
        (
            patient_id,
            symptoms,
            diagnosis,
            treatment,
            doctor_notes
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            record.patient_id,
            record.symptoms,
            record.diagnosis,
            record.treatment,
            record.doctor_notes
        )
    )

    connection.commit()

    record_id = cursor.lastrowid

    connection.close()

    return {
        "message": "Medical record created successfully",
        "record_id": record_id
    }
@app.get("/patients/{patient_id}/medical-records")
def get_patient_medical_records(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM medical_records
        WHERE patient_id = ?
        ORDER BY id DESC
        """,
        (patient_id,)
    )

    records = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return records

@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM patients
        WHERE id = ?
        """,
        (patient_id,)
    )

    patient = cursor.fetchone()

    connection.close()

    if not patient:
        return {
            "message": "Patient not found"
        }

    return dict(patient)
@app.put("/patients/{patient_id}")
def update_patient(patient_id: int, patient: Patient):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE patients
        SET
            name = ?,
            age = ?,
            gender = ?,
            blood_group = ?,
            phone = ?,
            address = ?
        WHERE id = ?
        """,
        (
            patient.name,
            patient.age,
            patient.gender,
            patient.blood_group,
            patient.phone,
            patient.address,
            patient_id
        )
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        return {"message": "Patient not found"}

    connection.close()

    return {"message": "Patient updated successfully"}
@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM patients
        WHERE id = ?
        """,
        (patient_id,)
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()
        return {"message": "Patient not found"}

    connection.close()

    return {"message": "Patient deleted successfully"}
@app.post("/prescriptions")
def create_prescription(prescription: Prescription):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO prescriptions
        (
            patient_id,
            medicine,
            dosage,
            duration,
            instructions
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            prescription.patient_id,
            prescription.medicine,
            prescription.dosage,
            prescription.duration,
            prescription.instructions
        )
    )

    connection.commit()

    prescription_id = cursor.lastrowid

    connection.close()

    return {
        "message": "Prescription created successfully",
        "prescription_id": prescription_id
    }
@app.get("/patients/{patient_id}/prescriptions")
def get_patient_prescriptions(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM prescriptions
        WHERE patient_id = ?
        ORDER BY id DESC
        """,
        (patient_id,)
    )

    prescriptions = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return prescriptions
@app.post("/lab-reports")
def create_lab_report(report: LabReport):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO lab_reports
        (
            patient_id,
            report_name,
            report_result,
            doctor_comments
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            report.patient_id,
            report.report_name,
            report.report_result,
            report.doctor_comments
        )
    )

    connection.commit()

    report_id = cursor.lastrowid

    connection.close()

    return {
        "message": "Lab report created successfully",
        "report_id": report_id
    }
@app.get("/patients/{patient_id}/health-summary")
def health_summary(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,)
    )
    patient = cursor.fetchone()

    if not patient:
        connection.close()
        return {"message": "Patient not found"}

    cursor.execute(
        "SELECT * FROM medical_records WHERE patient_id = ?",
        (patient_id,)
    )
    records = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        "SELECT * FROM prescriptions WHERE patient_id = ?",
        (patient_id,)
    )
    prescriptions = [dict(row) for row in cursor.fetchall()]

    cursor.execute(
        "SELECT * FROM lab_reports WHERE patient_id = ?",
        (patient_id,)
    )
    reports = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return {
        "patient": dict(patient),
        "medical_records": records,
        "prescriptions": prescriptions,
        "lab_reports": reports
    }
@app.get("/patients/{patient_id}/ai-summary")
def ai_summary(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    # Patient
    cursor.execute(
        "SELECT * FROM patients WHERE id = ?",
        (patient_id,)
    )
    patient = cursor.fetchone()

    if not patient:
        connection.close()
        return {"message": "Patient not found"}

    # Medical Records
    cursor.execute(
        """
        SELECT *
        FROM medical_records
        WHERE patient_id = ?
        ORDER BY id DESC
        """,
        (patient_id,)
    )
    records = cursor.fetchall()

    # Prescriptions
    cursor.execute(
        """
        SELECT *
        FROM prescriptions
        WHERE patient_id = ?
        ORDER BY id DESC
        """,
        (patient_id,)
    )
    prescriptions = cursor.fetchall()

    # Lab Reports
    cursor.execute(
        """
        SELECT *
        FROM lab_reports
        WHERE patient_id = ?
        ORDER BY id DESC
        """,
        (patient_id,)
    )
    reports = cursor.fetchall()
    connection.close()


    summary_prompt = f"""
    Patient:
    {dict(patient)}

    Medical Records:
    {[dict(r) for r in records]}

   Prescriptions:
   {[dict(p) for p in prescriptions]}

   Lab Reports:
   {[dict(r) for r in reports]}

Create:

   1. Health Overview
   2. Major Medical Conditions
   3. Current Medications
   4. Important Risk Factors
   5. Recommended Follow-Up

   Keep the summary concise and patient-friendly.
   """

    summary = AIEngine.generate(
    prompt=summary_prompt,
    patient=patient
    )


    return {
    "success": True,
    "patient_id": patient_id,
    "summary": summary
} 
@app.get("/dashboard/stats")
def dashboard_stats():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM medical_records")
    total_records = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM prescriptions")
    total_prescriptions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lab_reports")
    total_lab_reports = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cursor.fetchone()[0]

    connection.close()

    return {
        "total_patients": total_patients,
        "total_medical_records": total_records,
        "total_prescriptions": total_prescriptions,
        "total_lab_reports": total_lab_reports,
        "total_appointments": total_appointments
    }
@app.get("/patients/{patient_id}/timeline")
def patient_timeline(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    timeline = []

    cursor.execute(
        """
        SELECT created_at, 'Medical Record' as type,
               diagnosis as title
        FROM medical_records
        WHERE patient_id = ?
        """,
        (patient_id,)
    )

    for row in cursor.fetchall():
        timeline.append(dict(row))

    cursor.execute(
        """
        SELECT created_at, 'Prescription' as type,
               medicine as title
        FROM prescriptions
        WHERE patient_id = ?
        """,
        (patient_id,)
    )

    for row in cursor.fetchall():
        timeline.append(dict(row))

    cursor.execute(
        """
        SELECT created_at, 'Lab Report' as type,
               report_name as title
        FROM lab_reports
        WHERE patient_id = ?
        """,
        (patient_id,)
    )

    for row in cursor.fetchall():
        timeline.append(dict(row))

    connection.close()

    timeline.sort(key=lambda x: x["created_at"])

    return {
        "patient_id": patient_id,
        "timeline": timeline
    }
@app.post("/ai/chat")
def ai_chat(data: AIRequest):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, age, gender, blood_group FROM patients WHERE id=?",
        (data.patient_id,)
    )

    patient = cursor.fetchone()

    if not patient:
        return {
            "success": False,
            "message": "Patient not found"
        }


    # Save user message

    cursor.execute(
        """
        INSERT INTO ai_conversations
            (patient_id, role, message)
        VALUES (?, ?, ?)
        """,
        (data.patient_id, "user", data.prompt)
    )
    cursor.execute(
        """
        SELECT role, message
        FROM ai_conversations
        WHERE patient_id = ?
        ORDER BY id DESC LIMIT 10
        """,
        (data.patient_id,)
    )

    history = cursor.fetchall()

    conn.commit()
    cursor.execute(
        """
        SELECT role, message
        FROM ai_conversations
        WHERE patient_id = ?
        ORDER BY id DESC LIMIT 10
        """,
        (data.patient_id,)
    )

    history = cursor.fetchall()

    answer = AIEngine.generate(
        prompt=data.prompt,
        patient=patient,
        history=history
    )

    cursor.execute(
        """
        INSERT INTO ai_conversations
        (patient_id, role, message)
        VALUES (?, ?, ?)
        """,
        (data.patient_id, "assistant", answer)
    )

    conn.commit()

    # Save AI response
    cursor.execute(
        """
        INSERT INTO ai_conversations
        (patient_id, role, message)
        VALUES (?, ?, ?)
        """,
        (
            data.patient_id,
            "assistant",
            answer
        )
    )

    conn.commit()

    return {
        "success": True,
        "response": answer
    }
@app.get("/ai/history/{patient_id}")
def get_ai_history(patient_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, role, message, created_at
        FROM ai_conversations
        WHERE patient_id = ?
        ORDER BY id ASC
        """,
        (patient_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return {
        "success": True,
        "count": len(rows),
        "history": [dict(row) for row in rows]
    }
@app.delete("/ai/history/{patient_id}")
def clear_ai_history(patient_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM ai_conversations
        WHERE patient_id = ?
        """,
        (patient_id,)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Chat history cleared successfully"
    }
@app.get("/patients/{patient_id}/risk")
def patient_risk(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id=?",
        (patient_id,)
    )

    patient = cursor.fetchone()

    if not patient:
        return {
            "success": False,
            "message": "Patient not found"
        }

    cursor.execute(
        """
        SELECT *
        FROM medical_records
        WHERE patient_id=?
        """,
        (patient_id,)
    )

    records = cursor.fetchall()

    result = RiskPredictionEngine.calculate(
        patient,
        records
    )

    return {
        "success": True,
        "patient_id": patient_id,
        **result
    }
@app.get("/patients/{patient_id}/report")
def generate_report(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id=?",
        (patient_id,)
    )

    patient = cursor.fetchone()

    if not patient:
        return {
            "success": False,
            "message": "Patient not found"
        }
    cursor.execute(
        """
        SELECT *
        FROM medical_records
        WHERE patient_id = ?
        ORDER BY id DESC LIMIT 5
        """,
        (patient_id,)
    )
    records = cursor.fetchall()
    cursor.execute(
        """
        SELECT *
        FROM prescriptions
        WHERE patient_id = ?
        ORDER BY id DESC LIMIT 5
        """,
        (patient_id,)
    )

    prescriptions = cursor.fetchall()



    pdf_file = f"patient_{patient_id}_report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "AI LIFEOS - Patient Health Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph(
            f"Name: {patient['name']}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"Age: {patient['age']}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"Gender: {patient['gender']}",
            styles["BodyText"]
        )
    )
    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "Medical Records",
            styles["Heading2"]
        )
    )
    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "Prescriptions",
            styles["Heading2"]
        )
    )

    for p in prescriptions:
        content.append(
            Paragraph(
                f"Medicine: {p['medicine']}",
                styles["BodyText"]
            )
        )

        content.append(
            Paragraph(
                f"Dosage: {p['dosage']}",
                styles["BodyText"]
            )
        )

        content.append(
            Paragraph(
                f"Duration: {p['duration']}",
                styles["BodyText"]
            )
        )

        content.append(Spacer(1, 10))

    for record in records:
        content.append(
            Paragraph(
                f"Diagnosis: {record['diagnosis']}",
                styles["BodyText"]
            )
        )

        content.append(
            Paragraph(
                f"Symptoms: {record['symptoms']}",
                styles["BodyText"]
            )
        )

        content.append(
            Paragraph(
                f"Treatment: {record['treatment']}",
                styles["BodyText"]
            )
        )

        content.append(Spacer(1, 10))
    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "Risk Assessment",
            styles["Heading2"]
        )
    )
    print("RECORDS:", records)
    risk = RiskPredictionEngine.calculate(
        patient,
        records
    )

    content.append(
        Paragraph(
            f"Risk Score: {risk['risk_score']}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"Risk Level: {risk['risk_level']}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"Risk Factors: {', '.join(risk['risk_factors'])}",
            styles["BodyText"]
        )
    )
    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "AI Summary",
            styles["Heading2"]
        )
    )
    print("RISK:", risk)

    summary = f"""
    The patient is a {patient['age']}-year-old {patient['gender']}
    diagnosed with {records[0]['diagnosis'] if records else 'N/A'}.

    Symptoms include:
    {records[0]['symptoms'] if records else 'N/A'}.

    Current treatment:
    {records[0]['treatment'] if records else 'N/A'}.

    Overall risk level:
    {risk.get('risk_level', 'Unknown')}.
    """
    content.append(
        Paragraph(
            summary.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    )
    doc.build(content)

    return {
        "success": True,
        "pdf_file": pdf_file
    }
@app.get("/analytics")
def analytics():

    connection = get_connection()
    cursor = connection.cursor()

    # Total Patients
    cursor.execute(
        "SELECT COUNT(*) as total FROM patients"
    )
    total_patients = cursor.fetchone()["total"]

    # Total Medical Records
    cursor.execute(
        "SELECT COUNT(*) as total FROM medical_records"
    )
    total_records = cursor.fetchone()["total"]

    # Total Prescriptions
    cursor.execute(
        "SELECT COUNT(*) as total FROM prescriptions"
    )
    total_prescriptions = cursor.fetchone()["total"]
    cursor.execute(
        """
        SELECT diagnosis, COUNT(*) as total
        FROM medical_records
        GROUP BY diagnosis
        ORDER BY total DESC LIMIT 1
        """
    )

    disease = cursor.fetchone()
    low_risk = 0
    medium_risk = 0
    high_risk = 0

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    for patient in patients:

        cursor.execute(
            """
            SELECT *
            FROM medical_records
            WHERE patient_id = ?
            """,
            (patient["id"],)
        )

        records = cursor.fetchall()

        risk = RiskPredictionEngine.calculate(
            patient,
            records
        )

        if risk["risk_level"] == "Low":
            low_risk += 1

        elif risk["risk_level"] == "Medium":
            medium_risk += 1

        elif risk["risk_level"] == "High":
            high_risk += 1
    connection.close()

    return {
        "success": True,
        "total_patients": total_patients,
        "total_medical_records": total_records,
        "total_prescriptions": total_prescriptions,
        "most_common_disease": (
            disease["diagnosis"]
            if disease else "N/A"
        ),

        "low_risk_patients": low_risk,
        "medium_risk_patients": medium_risk,
        "high_risk_patients": high_risk
    }
@app.get("/analytics/summary")
def analytics_summary():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) as total FROM patients"
    )
    total_patients = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT diagnosis, COUNT(*) as total
        FROM medical_records
        GROUP BY diagnosis
        ORDER BY total DESC
        LIMIT 1
        """
    )

    disease = cursor.fetchone()



    summary = (
        f"The system currently manages "
        f"{total_patients} patient(s). "
        f"The most common diagnosis is "
        f"{disease['diagnosis'] if disease else 'N/A'}."
    )

    low_risk = 0
    medium_risk = 0
    high_risk = 0

    insights = []

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    for patient in patients:

        cursor.execute(
            """
            SELECT *
            FROM medical_records
            WHERE patient_id = ?
            """,
            (patient["id"],)
        )

        records = cursor.fetchall()

        risk = RiskPredictionEngine.calculate(
            patient,
            records
        )

        if risk["risk_level"] == "Low":
            low_risk += 1

        elif risk["risk_level"] == "Medium":
            medium_risk += 1

        elif risk["risk_level"] == "High":
            high_risk += 1
        print("LOW:", low_risk)
        print("MEDIUM:", medium_risk)
        print("HIGH:", high_risk)
        print("DISEASE:", disease)
        if low_risk > 0:
            insights.append(
                f"All {low_risk} patient(s) are currently classified as Low Risk."
            )

        if high_risk == 0:
            insights.append(
                "No High Risk patients require urgent attention."
            )

        if disease:
            insights.append(
                f"{disease['diagnosis']} is the most frequently recorded diagnosis."
            )

        print("INSIGHTS:", insights)

    connection.close()


    return {
        "success": True,
        "summary": summary,
        "insights": insights
    }
@app.get("/patients/{patient_id}/health-score")
def health_score(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id=?",
        (patient_id,)
    )

    patient = cursor.fetchone()

    if not patient:
        return {
            "success": False,
            "message": "Patient not found"
        }

    cursor.execute(
        """
        SELECT *
        FROM medical_records
        WHERE patient_id=?
        """,
        (patient_id,)
    )

    records = cursor.fetchall()

    result = HealthScoreEngine.calculate(
        patient,
        records
    )

    connection.close()

    return {
        "success": True,
        "patient_id": patient_id,
        **result
    }
@app.get("/patients/{patient_id}/recommendations")
def patient_recommendations(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id=?",
        (patient_id,)
    )

    patient = cursor.fetchone()

    if not patient:
        return {
            "success": False,
            "message": "Patient not found"
        }

    cursor.execute(
        """
        SELECT *
        FROM medical_records
        WHERE patient_id=?
        """,
        (patient_id,)
    )

    records = cursor.fetchall()

    health = HealthScoreEngine.calculate(
        patient,
        records
    )

    recommendations = (
        HealthRecommendationEngine.generate(
            patient,
            records,
            health["health_score"]
        )
    )

    connection.close()

    return {
        "success": True,
        "patient_id": patient_id,
        "health_score": health["health_score"],
        "recommendations": recommendations
    }
@app.get("/patients/{patient_id}/timeline")
def patient_timeline(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    timeline = []

    # Medical Records
    cursor.execute(
        """
        SELECT *
        FROM medical_records
        WHERE patient_id = ?
        ORDER BY id ASC
        """,
        (patient_id,)
    )

    records = cursor.fetchall()

    for record in records:
        timeline.append({
            "type": "medical_record",
            "diagnosis": record["diagnosis"],
            "symptoms": record["symptoms"],
            "treatment": record["treatment"]
        })

    # Prescriptions
    cursor.execute(
        """
        SELECT *
        FROM prescriptions
        WHERE patient_id = ?
        ORDER BY id ASC
        """,
        (patient_id,)
    )

    prescriptions = cursor.fetchall()

    for p in prescriptions:
        timeline.append({
            "type": "prescription",
            "medicine": p["medicine"],
            "dosage": p["dosage"],
            "duration": p["duration"]
        })

    # Lab Reports
    cursor.execute(
        """
        SELECT *
        FROM lab_reports
        WHERE patient_id = ?
        ORDER BY id ASC
        """,
        (patient_id,)
    )

    reports = cursor.fetchall()

    for report in reports:
        timeline.append({
            "type": "lab_report",
            "report_name": report["report_name"],
            "result": report["report_result"]
        })

    connection.close()

    return {
        "success": True,
        "patient_id": patient_id,
        "timeline": timeline
    }
@app.get("/patients/{patient_id}/timeline-summary")
def timeline_summary(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id=?",
        (patient_id,)
    )

    patient = cursor.fetchone()

    if not patient:
        return {
            "success": False,
            "message": "Patient not found"
        }

    cursor.execute(
        """
        SELECT *
        FROM medical_records
        WHERE patient_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,)
    )

    record = cursor.fetchone()

    connection.close()

    if record:
        summary = (
            f"Patient {patient['name']} was diagnosed with "
            f"{record['diagnosis']}. Symptoms include "
            f"{record['symptoms']}. Treatment: "
            f"{record['treatment']}."
        )
    else:
        summary = "No medical history available."

    return {
        "success": True,
        "summary": summary
    }
@app.get("/patients/{patient_id}/doctor-notes")
def doctor_notes(patient_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id=?",
        (patient_id,)
    )

    patient = cursor.fetchone()

    if not patient:
        return {
            "success": False,
            "message": "Patient not found"
        }

    cursor.execute(
        """
        SELECT *
        FROM medical_records
        WHERE patient_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,)
    )

    record = cursor.fetchone()

    cursor.execute(
        """
        SELECT *
        FROM prescriptions
        WHERE patient_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,)
    )

    prescription = cursor.fetchone()

    connection.close()

    notes = f"""
Patient: {patient['name']}

Diagnosis: {record['diagnosis'] if record else 'N/A'}

Symptoms: {record['symptoms'] if record else 'N/A'}

Treatment: {record['treatment'] if record else 'N/A'}

Medication: {prescription['medicine'] if prescription else 'N/A'}

Doctor Recommendation:
Continue prescribed treatment and monitor symptoms.
Follow-up consultation if symptoms persist or worsen.
"""

    return {
        "success": True,
        "patient_id": patient_id,
        "doctor_notes": notes.strip()
    }

@app.get("/export/patients")
def export_patients():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM patients"
    )

    patients = cursor.fetchall()

    csv_file = "patients_export.csv"

    with open(
        csv_file,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "ID",
                "Name",
                "Age",
                "Gender",
                "Phone"
            ]
        )

        for patient in patients:

            writer.writerow([
                patient["id"],
                patient["name"],
                patient["age"],
                patient["gender"],
                patient["phone"]
            ])

    connection.close()

    return {
        "success": True,
        "file": csv_file
    }