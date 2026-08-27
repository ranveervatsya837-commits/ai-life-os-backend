import os
import csv
import time
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from database import get_connection
from auth import hash_password, verify_password, create_access_token, verify_token
from risk_prediction import RiskPredictionEngine
from health_score import HealthScoreEngine
from health_recommendation import HealthRecommendationEngine

app = FastAPI(title="AI LIFEOS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- DATABASE AUTO-INITIALIZATION ----------------- #
def init_db():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT UNIQUE,
                password TEXT,
                role TEXT DEFAULT 'user',
                is_verified INTEGER DEFAULT 0,
                created_at TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                blood_group TEXT,
                phone TEXT,
                address TEXT,
                created_at TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id TEXT PRIMARY KEY,
                patient TEXT NOT NULL,
                doctor TEXT NOT NULL,
                hospital TEXT,
                date TEXT,
                time TEXT,
                fee INTEGER,
                status TEXT DEFAULT 'booked',
                created_at TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                experience INTEGER,
                consultation_fee INTEGER
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                symptoms TEXT,
                diagnosis TEXT,
                treatment TEXT,
                doctor_notes TEXT,
                created_at TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                medicine TEXT,
                dosage TEXT,
                duration TEXT,
                instructions TEXT,
                created_at TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lab_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                report_name TEXT,
                report_result TEXT,
                doctor_comments TEXT,
                created_at TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                title TEXT,
                content TEXT,
                created_at TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                role TEXT,
                message TEXT,
                created_at TEXT
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("Database schema successfully verified and initialized.")
    except Exception as e:
        print(f"Database init error: {e}")

init_db()

@app.on_event("startup")
def on_startup():
    init_db()


# ----------------- GROQ CLIENT & SCHEMAS ----------------- #
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key) if groq_api_key else None

class AIRequest(BaseModel):
    patient_id: int
    prompt: str

class DoctorModel(BaseModel):
    name: str
    specialization: str
    experience: int
    consultation_fee: int

class AppointmentCreate(BaseModel):
    id: Optional[str] = None
    patient: str
    doctor: str
    hospital: Optional[str] = "General Hospital"
    date: Optional[str] = None
    time: Optional[str] = "10:00 AM"
    fee: Optional[int] = 0

class RegisterUser(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = ""

class LoginUser(BaseModel):
    email: str
    password: str

class UpdateProfile(BaseModel):
    current_email: str
    name: str
    email: str

class ChangePassword(BaseModel):
    email: str
    old_password: str
    new_password: str

class SymptomsRequest(BaseModel):
    symptoms: List[str]

class Patient(BaseModel):
    name: str
    age: int
    gender: str
    blood_group: Optional[str] = "O+"
    phone: Optional[str] = ""
    address: Optional[str] = ""

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

class Note(BaseModel):
    patient_id: int
    title: str
    content: str

class LabReport(BaseModel):
    patient_id: int
    report_name: str
    report_result: str
    doctor_comments: str


# ----------------- AI ENGINE ----------------- #
# ----------------- AI ENGINE ----------------- #


class AIEngine:
    SYSTEM_PROMPT = """
You are AI LIFEOS, an intelligent healthcare assistant.
Rules:
- Introduce yourself as AI LIFEOS only when necessary.
- Never provide a definite diagnosis. Recommend consulting a doctor.
- Personalize recommendations using provided patient info and medical records.
- If symptoms are reported: 1. Possible Causes, 2. Self-Care Advice, 3. When to See a Doctor.
- If the user asks 'What did I ask earlier?', return previous user questions only.
"""

    @staticmethod
    def generate(prompt: str, patient, history=None, medical_records=None, lab_reports=None, prescriptions=None, memory_text="") -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "AI service is currently unavailable. Please check your GROQ_API_KEY."

        groq_client = Groq(api_key=api_key)

        medical_history_text = ""
        if medical_records:
            for record in medical_records:
                medical_history_text += f"- Symptoms: {record['symptoms']}\n  Diagnosis: {record['diagnosis']}\n  Treatment: {record['treatment']}\n  Doctor Notes: {record['doctor_notes']}\n\n"
        else:
            medical_history_text = "No medical records found."

        lab_reports_text = ""
        if lab_reports:
            for report in lab_reports:
                lab_reports_text += f"- Report: {report['report_name']}, Result: {report['report_result']}, Comments: {report['doctor_comments']}\n"
        else:
            lab_reports_text = "No lab reports found."

        prescriptions_text = ""
        if prescriptions:
            for pres in prescriptions:
                prescriptions_text += f"- Med: {pres['medicine']}, Dose: {pres['dosage']}, Duration: {pres['duration']}, Info: {pres['instructions']}\n"
        else:
            prescriptions_text = "No prescriptions found."

        full_prompt = f"""
Patient Profile:
- Name: {patient['name']}
- Age: {patient['age']}
- Gender: {patient['gender']}
- Blood Group: {patient['blood_group']}

Medical History:
{medical_history_text}

Lab Reports:
{lab_reports_text}

Prescriptions:
{prescriptions_text}

Conversation Memory:
{memory_text}

Question:
{prompt}
"""
        messages = [{"role": "system", "content": AIEngine.SYSTEM_PROMPT}]
        if history:
            for item in reversed(history):
                messages.append({"role": item["role"], "content": item["message"]})
        messages.append({"role": "user", "content": full_prompt})

        try:
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI Processing Error: {str(e)}"
# ----------------- AUTH ENDPOINTS ----------------- #
@app.post("/register")
def register(user: RegisterUser):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM auth_users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            return {"message": "Email already registered"}

        hashed_password = hash_password(user.password)
        cursor.execute(
            "INSERT INTO auth_users (name, email, password, created_at, role, phone) VALUES (?, ?, ?, ?, ?, ?)",
            (user.name, user.email, hashed_password, datetime.utcnow().isoformat(), "user", user.phone or "")
        )
        conn.commit()
        return {"message": "User registered successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/login")
def login(user: LoginUser):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auth_users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    conn.close()

    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": db_user["email"], "role": db_user["role"]})
    return {"access_token": token}

@app.get("/me")
def get_me(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token missing")

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, role, is_verified, phone FROM auth_users WHERE email = ?", (payload["sub"],))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)

@app.post("/change-password")
def change_password(data: ChangePassword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auth_users WHERE email = ?", (data.email,))
    db_user = cursor.fetchone()

    if not db_user or not verify_password(data.old_password, db_user["password"]):
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid current password")

    new_hash = hash_password(data.new_password)
    cursor.execute("UPDATE auth_users SET password = ? WHERE email = ?", (new_hash, data.email))
    conn.commit()
    conn.close()
    return {"message": "Password changed successfully"}

@app.put("/profile")
def update_profile(data: UpdateProfile):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE auth_users SET name = ?, email = ? WHERE email = ?", (data.name, data.email, data.current_email))
    conn.commit()
    conn.close()
    return {"message": "Profile updated successfully"}


# ----------------- PATIENTS ENDPOINTS ----------------- #
@app.post("/patients")
def create_patient(patient: Patient):
    init_db()
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            INSERT INTO patients (name, age, gender, blood_group, phone, address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(patient.name).strip(),
                int(patient.age),
                str(patient.gender).strip(),
                str(patient.blood_group or 'O+').strip(),
                str(patient.phone or '').strip(),
                str(patient.address or '').strip(),
                created_at
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return {"status": "success", "message": "Patient added successfully", "id": new_id, "patient": patient.dict()}
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patients")
def get_patients():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    patients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return patients

@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return dict(patient)

@app.put("/patients/{patient_id}")
def update_patient(patient_id: int, patient: Patient):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE patients
        SET name = ?, age = ?, gender = ?, blood_group = ?, phone = ?, address = ?
        WHERE id = ?
        """,
        (patient.name, patient.age, patient.gender, patient.blood_group, patient.phone, patient.address, patient_id)
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient updated successfully"}

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}


# ----------------- APPOINTMENTS ENDPOINTS ----------------- #
@app.post("/appointments")
def create_appointment(appointment: AppointmentCreate):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    app_id = appointment.id or str(uuid.uuid4())
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO appointments (id, patient, doctor, hospital, date, time, fee, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            app_id,
            appointment.patient,
            appointment.doctor,
            appointment.hospital or "General Hospital",
            appointment.date or datetime.utcnow().strftime("%Y-%m-%d"),
            appointment.time or "10:00 AM",
            appointment.fee or 0,
            "booked",
            created_at
        )
    )
    conn.commit()
    conn.close()
    return {"id": app_id, "message": "Appointment created successfully"}

@app.get("/appointments")
def get_appointments():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments ORDER BY created_at DESC")
    appointments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return appointments

@app.get("/appointments/{appointment_id}")
def get_appointment(appointment_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
    appointment = cursor.fetchone()
    conn.close()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return dict(appointment)

@app.put("/appointments/{appointment_id}/status")
def update_appointment_status(appointment_id: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
    conn.commit()
    conn.close()
    return {"message": "Appointment status updated"}

@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    return {"message": "Appointment deleted successfully"}

@app.get("/my-appointments")
def my_appointments(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token missing")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM auth_users WHERE email = ?", (payload["sub"],))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute("SELECT * FROM appointments WHERE patient = ?", (user["name"],))
    appointments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return appointments


# ----------------- DOCTORS CRUD ----------------- #
@app.get("/doctors")
def get_all_doctors():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors")
    doctors = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return doctors

@app.get("/doctors/search/{specialization}")
def search_doctors(specialization: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE LOWER(specialization) LIKE LOWER(?)", (f"%{specialization}%",))
    doctors = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return doctors

@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, doctor: DoctorModel):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE doctors
        SET name = ?, specialization = ?, experience = ?, consultation_fee = ?
        WHERE id = ?
        """,
        (doctor.name, doctor.specialization, doctor.experience, doctor.consultation_fee, doctor_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Doctor updated successfully"}

@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
    conn.commit()
    conn.close()
    return {"message": "Doctor deleted successfully"}


# ----------------- MEDICAL RECORDS & PRESCRIPTIONS ----------------- #
@app.post("/medical-records")
def create_medical_record(record: MedicalRecord):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO medical_records (patient_id, symptoms, diagnosis, treatment, doctor_notes, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (record.patient_id, record.symptoms, record.diagnosis, record.treatment, record.doctor_notes, created_at)
    )
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return {"message": "Medical record created successfully", "record_id": record_id}

@app.get("/patients/{patient_id}/medical-records")
def get_patient_medical_records(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medical_records WHERE patient_id = ? ORDER BY id DESC", (patient_id,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

@app.post("/prescriptions")
def create_prescription(prescription: Prescription):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO prescriptions (patient_id, medicine, dosage, duration, instructions, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (prescription.patient_id, prescription.medicine, prescription.dosage, prescription.duration, prescription.instructions, created_at)
    )
    conn.commit()
    prescription_id = cursor.lastrowid
    conn.close()
    return {"message": "Prescription created successfully", "prescription_id": prescription_id}

@app.get("/patients/{patient_id}/prescriptions")
def get_patient_prescriptions(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prescriptions WHERE patient_id = ? ORDER BY id DESC", (patient_id,))
    prescriptions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return prescriptions

@app.post("/lab-reports")
def create_lab_report(report: LabReport):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO lab_reports (patient_id, report_name, report_result, doctor_comments, created_at) VALUES (?, ?, ?, ?, ?)",
        (report.patient_id, report.report_name, report.report_result, report.doctor_comments, created_at)
    )
    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return {"message": "Lab report created successfully", "report_id": report_id}

@app.post("/notes")
def create_note(note: Note):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO notes (patient_id, title, content, created_at) VALUES (?, ?, ?, ?)", (note.patient_id, note.title, note.content, created_at))
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return {"success": True, "message": "Note created successfully", "note_id": note_id}

@app.get("/notes/{patient_id}")
def get_notes(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE patient_id = ? ORDER BY id DESC", (patient_id,))
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"success": True, "count": len(notes), "notes": notes}

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return {"success": deleted, "message": "Note deleted" if deleted else "Note not found"}


# ----------------- TIMELINE & PDF REPORT ----------------- #
@app.get("/patients/{patient_id}/timeline")
def get_patient_timeline(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    timeline = []

    cursor.execute("SELECT created_at, 'Medical Record' as type, diagnosis as title FROM medical_records WHERE patient_id = ?", (patient_id,))
    for row in cursor.fetchall():
        timeline.append(dict(row))

    cursor.execute("SELECT created_at, 'Prescription' as type, medicine as title FROM prescriptions WHERE patient_id = ?", (patient_id,))
    for row in cursor.fetchall():
        timeline.append(dict(row))

    cursor.execute("SELECT created_at, 'Lab Report' as type, report_name as title FROM lab_reports WHERE patient_id = ?", (patient_id,))
    for row in cursor.fetchall():
        timeline.append(dict(row))

    conn.close()
    timeline.sort(key=lambda x: str(x.get("created_at") or ""))
    return {"patient_id": patient_id, "timeline": timeline}

@app.get("/patients/{patient_id}/report")
def generate_pdf_report(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
    patient = cursor.fetchone()
    if not patient:
        conn.close()
        raise HTTPException(status_code=404, detail="Patient not found")

    cursor.execute("SELECT * FROM medical_records WHERE patient_id = ? ORDER BY id DESC LIMIT 5", (patient_id,))
    records = cursor.fetchall()
    cursor.execute("SELECT * FROM prescriptions WHERE patient_id = ? ORDER BY id DESC LIMIT 5", (patient_id,))
    prescriptions = cursor.fetchall()
    conn.close()

    pdf_file = f"patient_{patient_id}_report.pdf"
    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()
    content = [
        Paragraph("AI LIFEOS - Patient Health Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Name: {patient['name']}", styles["BodyText"]),
        Paragraph(f"Age: {patient['age']}", styles["BodyText"]),
        Paragraph(f"Gender: {patient['gender']}", styles["BodyText"]),
        Spacer(1, 20),
        Paragraph("Medical Records", styles["Heading2"]),
        Spacer(1, 10),
    ]

    for r in records:
        content.append(Paragraph(f"Diagnosis: {r['diagnosis']} | Treatment: {r['treatment']}", styles["BodyText"]))
        content.append(Spacer(1, 5))

    content.append(Spacer(1, 10))
    content.append(Paragraph("Prescriptions", styles["Heading2"]))
    for p in prescriptions:
        content.append(Paragraph(f"Medicine: {p['medicine']} ({p['dosage']}) - {p['duration']}", styles["BodyText"]))
        content.append(Spacer(1, 5))

    doc.build(content)
    return FileResponse(pdf_file, media_type="application/pdf", filename=pdf_file)


# ----------------- HEALTH RISK & ENGINES ----------------- #
@app.get("/patients/{patient_id}/risk")
def patient_risk(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
    patient = cursor.fetchone()
    if not patient:
        conn.close()
        return {"success": False, "message": "Patient not found"}

    cursor.execute("SELECT * FROM medical_records WHERE patient_id=?", (patient_id,))
    records = cursor.fetchall()
    conn.close()

    result = RiskPredictionEngine.calculate(patient, records)
    return {"success": True, "patient_id": patient_id, **result}

@app.get("/patients/{patient_id}/health-score")
def health_score(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
    patient = cursor.fetchone()
    if not patient:
        conn.close()
        return {"success": False, "message": "Patient not found"}

    cursor.execute("SELECT * FROM medical_records WHERE patient_id=?", (patient_id,))
    records = cursor.fetchall()
    conn.close()

    result = HealthScoreEngine.calculate(patient, records)
    return {"success": True, "patient_id": patient_id, **result}

@app.get("/patients/{patient_id}/recommendations")
def patient_recommendations(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
    patient = cursor.fetchone()
    if not patient:
        conn.close()
        return {"success": False, "message": "Patient not found"}

    cursor.execute("SELECT * FROM medical_records WHERE patient_id=?", (patient_id,))
    records = cursor.fetchall()

    health = HealthScoreEngine.calculate(patient, records)
    recommendations = HealthRecommendationEngine.generate(patient, records, health["health_score"])
    conn.close()

    return {
        "success": True,
        "patient_id": patient_id,
        "health_score": health["health_score"],
        "recommendations": recommendations
    }


# ----------------- AI CHAT & HISTORY ----------------- #
@app.post("/ai/recommend")
def ai_recommend(data: SymptomsRequest):
    symptoms = [s.lower() for s in data.symptoms]
    if "fever" in symptoms and "cough" in symptoms:
        return {"possible_condition": "Common Cold / Viral Infection", "recommendation": "Consult a General Physician"}
    if "chest pain" in symptoms:
        return {"possible_condition": "Cardiovascular concern", "recommendation": "Consult a Cardiologist immediately"}
    return {"possible_condition": "Under assessment", "recommendation": "Consult a Physician"}

@app.post("/ai/chat")
def ai_chat(data: AIRequest):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, age, gender, blood_group FROM patients WHERE id=?", (data.patient_id,))
    patient = cursor.fetchone()

    if not patient:
        conn.close()
        return {"success": False, "message": "Patient not found"}

    prompt_lower = data.prompt.lower().strip()
    if prompt_lower in ["name", "my name", "what is my name", "who am i"]:
        conn.close()
        return {"success": True, "response": f"Your name is {patient['name']}."}
    if "blood group" in prompt_lower:
        conn.close()
        return {"success": True, "response": f"Your blood group is {patient['blood_group']}."}
    if "age" in prompt_lower:
        conn.close()
        return {"success": True, "response": f"You are {patient['age']} years old."}

    cursor.execute("SELECT symptoms, diagnosis, treatment, doctor_notes FROM medical_records WHERE patient_id = ? ORDER BY id DESC LIMIT 5", (data.patient_id,))
    medical_records = cursor.fetchall()

    cursor.execute("SELECT report_name, report_result, doctor_comments FROM lab_reports WHERE patient_id = ? ORDER BY id DESC LIMIT 5", (data.patient_id,))
    lab_reports = cursor.fetchall()

    cursor.execute("SELECT medicine, dosage, duration, instructions FROM prescriptions WHERE patient_id = ? ORDER BY id DESC LIMIT 5", (data.patient_id,))
    prescriptions = cursor.fetchall()

    cursor.execute("SELECT role, message FROM ai_conversations WHERE patient_id = ? ORDER BY id DESC LIMIT 10", (data.patient_id,))
    history = cursor.fetchall()

    answer = AIEngine.generate(
        prompt=data.prompt,
        patient=patient,
        history=history,
        medical_records=medical_records,
        lab_reports=lab_reports,
        prescriptions=prescriptions,
        memory_text=""
    )

    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO ai_conversations (patient_id, role, message, created_at) VALUES (?, ?, ?, ?)", (data.patient_id, "user", data.prompt, created_at))
    cursor.execute("INSERT INTO ai_conversations (patient_id, role, message, created_at) VALUES (?, ?, ?, ?)", (data.patient_id, "assistant", answer, created_at))
    conn.commit()
    conn.close()

    return {"success": True, "response": answer}

@app.get("/ai/history/{patient_id}")
def get_ai_history(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, role, message, created_at FROM ai_conversations WHERE patient_id = ? ORDER BY id ASC", (patient_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"success": True, "count": len(rows), "history": rows}

@app.delete("/ai/history/{patient_id}")
def clear_ai_history(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ai_conversations WHERE patient_id = ?", (patient_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Chat history cleared successfully"}


# ----------------- DASHBOARD & ANALYTICS ----------------- #
@app.get("/dashboard/stats")
def dashboard_stats():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
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
    conn.close()

    return {
        "total_patients": total_patients,
        "total_medical_records": total_records,
        "total_prescriptions": total_prescriptions,
        "total_lab_reports": total_lab_reports,
        "total_appointments": total_appointments
    }

@app.get("/analytics")
def analytics():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM patients")
    total_patients = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM medical_records")
    total_records = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM prescriptions")
    total_prescriptions = cursor.fetchone()["total"]

    cursor.execute("SELECT diagnosis, COUNT(*) as total FROM medical_records GROUP BY diagnosis ORDER BY total DESC LIMIT 1")
    disease = cursor.fetchone()

    conn.close()
    return {
        "success": True,
        "total_patients": total_patients,
        "total_medical_records": total_records,
        "total_prescriptions": total_prescriptions,
        "most_common_disease": disease["diagnosis"] if disease else "N/A"
    }

@app.get("/patients/{patient_id}/health-summary")
def health_summary(patient_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()

    if not patient:
        conn.close()
        raise HTTPException(status_code=404, detail="Patient not found")

    cursor.execute("SELECT * FROM medical_records WHERE patient_id = ?", (patient_id,))
    records = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM prescriptions WHERE patient_id = ?", (patient_id,))
    prescriptions = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM lab_reports WHERE patient_id = ?", (patient_id,))
    reports = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return {
        "patient": dict(patient),
        "medical_records": records,
        "prescriptions": prescriptions,
        "lab_reports": reports
    }

@app.get("/export/patients")
def export_patients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    csv_file = "patients_export.csv"
    with open(csv_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Age", "Gender", "Phone", "Address"])
        for p in patients:
            writer.writerow([p["id"], p["name"], p["age"], p["gender"], p["phone"], p["address"]])
    conn.close()
    return {"success": True, "file": csv_file}


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI LIFE OS - Healthcare Assistant</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen flex flex-col font-sans">
    <!-- Navbar -->
    <header class="bg-slate-800/80 backdrop-blur border-b border-slate-700 py-4 px-6 sticky top-0 z-50">
        <div class="max-w-6xl mx-auto flex items-center justify-between">
            <div class="flex items-center gap-3">
                <i class="fa-solid fa-heart-pulse text-rose-500 text-2xl"></i>
                <h1 class="text-xl font-bold tracking-wide text-white">AI LIFE <span class="text-rose-500">OS</span></h1>
            </div>
            <span class="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-full font-medium">
                ● Live API Connected
            </span>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-6xl w-full mx-auto p-4 sm:p-6 grid grid-cols-1 md:grid-cols-3 gap-6 flex-1">

        <!-- Left Column: Patient Selector & Profile -->
        <section class="bg-slate-800/60 border border-slate-700/70 rounded-2xl p-5 flex flex-col gap-4 shadow-xl">
            <h2 class="text-lg font-semibold text-slate-200 border-b border-slate-700 pb-2 flex items-center gap-2">
                <i class="fa-solid fa-user-circle text-sky-400"></i> Patient Profile
            </h2>

            <div>
                <label class="text-xs text-slate-400 uppercase font-semibold tracking-wider">Select Patient</label>
                <select id="patientSelect" onchange="loadPatientProfile()" class="w-full mt-1.5 bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-rose-500">
                    <option value="">Loading patients...</option>
                </select>
            </div>

            <!-- Patient Details Card -->
            <div id="patientDetails" class="bg-slate-950/60 rounded-xl p-4 border border-slate-800 text-sm space-y-2">
                <p class="text-slate-400 text-xs">Select or add a patient to view data.</p>
            </div>

            <!-- Quick Add Patient Accordion -->
            <details class="bg-slate-900/80 rounded-xl border border-slate-700/70 p-3">
                <summary class="text-xs font-semibold text-rose-400 cursor-pointer select-none">
                    + Add New Patient
                </summary>
                <form id="newPatientForm" onsubmit="createNewPatient(event)" class="mt-3 space-y-2">
                    <input type="text" id="pName" placeholder="Full Name" required class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200" />
                    <div class="grid grid-cols-2 gap-2">
                        <input type="number" id="pAge" placeholder="Age" required class="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200" />
                        <select id="pGender" class="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200">
                            <option>Male</option><option>Female</option><option>Other</option>
                        </select>
                    </div>
                    <div class="grid grid-cols-2 gap-2">
                        <input type="text" id="pBlood" placeholder="Blood Group (e.g. B+)" required class="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200" />
                        <input type="text" id="pPhone" placeholder="Phone" required class="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200" />
                    </div>
                    <input type="text" id="pAddress" placeholder="City / Address" required class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200" />
                    <button type="submit" class="w-full bg-rose-600 hover:bg-rose-500 text-white rounded-lg py-1.5 text-xs font-semibold transition">Save Patient</button>
                </form>
            </details>
        </section>

        <!-- Right Column: AI LifeOS Chat -->
        <section class="md:col-span-2 bg-slate-800/60 border border-slate-700/70 rounded-2xl p-5 flex flex-col shadow-xl min-h-[500px]">
            <div class="border-b border-slate-700 pb-3 mb-4 flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <i class="fa-solid fa-robot text-rose-500"></i>
                    <h2 class="text-lg font-semibold text-slate-200">AI Medical Consultation</h2>
                </div>
                <span class="text-xs text-slate-400">Powered by Groq OSS Engine</span>
            </div>

            <!-- Chat Box -->
            <div id="chatMessages" class="flex-1 overflow-y-auto space-y-3 pr-2 mb-4 max-h-[420px] text-sm scrollbar-thin">
                <div class="flex gap-3 items-start bg-slate-950/40 p-3 rounded-xl border border-slate-800">
                    <i class="fa-solid fa-heart-pulse text-rose-500 mt-1"></i>
                    <div>
                        <p class="font-semibold text-xs text-rose-400">AI LIFE OS</p>
                        <p class="text-slate-300 text-sm mt-0.5">Namaste! Select your profile and ask any health query or symptom evaluation.</p>
                    </div>
                </div>
            </div>

            <!-- Input Box -->
            <form id="chatForm" onsubmit="sendMessage(event)" class="flex gap-2">
                <input type="text" id="userPrompt" placeholder="Ask about diet, symptoms, or precautions..." required class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-rose-500" />
                <button type="submit" id="sendBtn" class="bg-rose-600 hover:bg-rose-500 px-5 py-2.5 rounded-xl text-sm font-semibold transition flex items-center gap-2">
                    <span>Ask AI</span>
                    <i class="fa-solid fa-paper-plane text-xs"></i>
                </button>
            </form>
        </section>

    </main>

    <script>
        const API_BASE = window.location.origin;
        let patientsList = [];

        async function fetchPatients() {
            try {
                const res = await fetch(`${API_BASE}/patients`);
                patientsList = await res.json();
                const sel = document.getElementById('patientSelect');
                sel.innerHTML = '';
                if (patientsList.length === 0) {
                    sel.innerHTML = '<option value="">No patients found. Add one!</option>';
                    document.getElementById('patientDetails').innerHTML = '<p class="text-xs text-amber-400">No patients registered in database.</p>';
                    return;
                }
                patientsList.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = `${p.name} (ID: ${p.id})`;
                    sel.appendChild(opt);
                });
                loadPatientProfile();
            } catch (err) {
                console.error(err);
            }
        }

        function loadPatientProfile() {
            const pId = parseInt(document.getElementById('patientSelect').value);
            const p = patientsList.find(item => item.id === pId);
            if (!p) return;
            document.getElementById('patientDetails').innerHTML = `
                <div class="text-slate-200 font-medium">${p.name}</div>
                <div class="text-xs text-slate-400">Age: <span class="text-slate-200">${p.age}</span> | Gender: <span class="text-slate-200">${p.gender}</span></div>
                <div class="text-xs text-slate-400">Blood Group: <span class="text-rose-400 font-semibold">${p.blood_group}</span></div>
                <div class="text-xs text-slate-400">Phone: <span class="text-slate-200">${p.phone}</span></div>
                <div class="text-xs text-slate-400">City: <span class="text-slate-200">${p.address}</span></div>
            `;
        }

        async function createNewPatient(e) {
            e.preventDefault();
            const body = {
                name: document.getElementById('pName').value,
                age: parseInt(document.getElementById('pAge').value),
                gender: document.getElementById('pGender').value,
                blood_group: document.getElementById('pBlood').value,
                phone: document.getElementById('pPhone').value,
                address: document.getElementById('pAddress').value
            };
            const res = await fetch(`${API_BASE}/patients`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (res.ok) {
                document.getElementById('newPatientForm').reset();
                await fetchPatients();
            }
        }

        async function sendMessage(e) {
            e.preventDefault();
            const promptInput = document.getElementById('userPrompt');
            const prompt = promptInput.value.trim();
            const patientId = parseInt(document.getElementById('patientSelect').value);

            if (!patientId) {
                alert('Please add or select a patient first!');
                return;
            }
            if (!prompt) return;

            const chatBox = document.getElementById('chatMessages');

            // Append User Message
            chatBox.innerHTML += `
                <div class="flex gap-3 items-start justify-end">
                    <div class="bg-rose-600/20 border border-rose-500/30 text-rose-100 p-3 rounded-xl max-w-[80%] text-right">
                        <p class="font-semibold text-xs text-rose-300">You</p>
                        <p class="text-sm mt-0.5">${prompt}</p>
                    </div>
                </div>
            `;
            promptInput.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            const btn = document.getElementById('sendBtn');
            btn.disabled = true;
            btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-xs"></i> <span>Thinking...</span>`;

            try {
                const res = await fetch(`${API_BASE}/ai/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ patient_id: patientId, prompt: prompt })
                });
                const data = await res.json();
                const aiReply = data.response ? data.response.replace(/\\n/g, '<br>') : (data.message || 'No response from server');

                chatBox.innerHTML += `
                    <div class="flex gap-3 items-start bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
                        <i class="fa-solid fa-heart-pulse text-rose-500 mt-1"></i>
                        <div class="flex-1">
                            <p class="font-semibold text-xs text-rose-400">AI LIFE OS</p>
                            <div class="text-slate-300 text-sm mt-1 leading-relaxed">${aiReply}</div>
                        </div>
                    </div>
                `;
            } catch (err) {
                chatBox.innerHTML += `<div class="text-rose-400 text-xs p-2">Error connecting to server.</div>`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = `<span>Ask AI</span> <i class="fa-solid fa-paper-plane text-xs"></i>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        }

        window.onload = fetchPatients;
    </script>
</body>
</html>
    """
