from fastapi import (
    FastAPI,
    Header,
    Depends
)

from fastapi.security import (
    OAuth2PasswordBearer
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

from pydantic import (
    BaseModel,
    EmailStr,
    Field
)

from datetime import datetime

import json
import uuid

from database import (
    create_tables,
    get_connection
)



from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_email,
    get_current_user_role,
    is_admin
)
# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="AI LIFEOS API",
    description="AI Powered Health & Wellness Operating System",
    version="2.0.0"
)

# JWT SECURITY
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

create_tables()
# =====================================================
# AI LIFEOS API
# AI Powered Health & Wellness Operating System
# Version : 2.0.0
# Developer : Ranveer
# =====================================================


class Appointment(BaseModel):
    doctor: str
    hospital: str
    date: str
    time: str
app=FastAPI(
    title="AI LIFEOS API",
    description="AI Powered Health & Wellness Operating System",
    version="2.0.0"
)

create_tables()

# =====================================================
# DATA FILES
# =====================================================



USERS_FILE = "data/users.json"
APPOINTMENTS_FILE = "data/appointments.json"
DOCTORS_FILE = "data/doctors.json"


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def load_json(file_path):

    try:
        with open(file_path, "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_json(file_path, data):

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


# =====================================================
# MODELS
# =====================================================

class User(BaseModel):
    name: str
    age: int
    email: EmailStr

class BMIRequest(BaseModel):
    weight: float = Field(..., gt=0, description="Weight in KG")
    height: float = Field(..., gt=0, description="Height in CM")

class BMIResponse(BaseModel):
    bmi: float
    category: str
    health_risk: str
    recommendation: str
# =====================================================
# SYSTEM ENDPOINTS
# =====================================================

@app.get("/")
def home():

    return {
        "project": "AILIFEOS",
        "version": "2.0.0",
        "status": "Online",
        "developer": "Ranveer",
        "timestamp": datetime.now()
    }


@app.get("/health")
def health_check():

    return {
        "status": "Healthy",
        "server_time": datetime.now()
    }


# =====================================================
# USER MANAGEMENT
# =====================================================
class RegisterUser(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6
    )

    role: str = Field(
        default="user"
    )
@app.post("/register")
def register(user: RegisterUser):

        connection = get_connection()
        cursor = connection.cursor()

        try:

            hashed_password = hash_password(
                user.password
            )

            cursor.execute(
                """
                INSERT INTO auth_users
                (name,
                 email,
                 password,
                 created_at,
                 role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user.name,
                    user.email,
                    hashed_password,
                    datetime.now().isoformat(),
                    user.role
                )
            )

            connection.commit()

            return {
                "message": "User registered successfully"
            }

        except Exception as e:

            return {
                "error": str(e)
            }

        finally:

            connection.close()
class LoginUser(BaseModel):

    email: EmailStr = Field(
        ...,
        description="Registered email address"
    )

    password: str = Field(
        ...,
        min_length=6,
        description="Account password"
    )

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
                "message": "Invalid email or password"
            }

        if not verify_password(
                user.password,
                db_user["password"]
        ):
            return {
                "message": "Invalid email or password"
            }

        access_token = create_access_token(
            {
                "sub": db_user["email"],
                "role": db_user["role"]
            }
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": db_user["id"],
                "name": db_user["name"],
                "email": db_user["email"],
                "role": db_user["role"]
            }
        }

@app.get("/me")
def get_profile(
    token: str = Depends(oauth2_scheme)
):

    email = get_current_user_email(token)

    if not email:
        return {
            "message": "Invalid or expired token"
        }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, email, role
        FROM auth_users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    if not user:
        return {
            "message": "User not found"
        }

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }
@app.get("/admin")
def admin_dashboard(
    token: str = Depends(oauth2_scheme)
):

    if not is_admin(token):
        return {
            "message": "Admin access required"
        }

    return {
        "message": "Welcome Admin",
        "access": "granted"
    }
@app.post("/users")
def create_user(
    user: User,
    token: str = Depends(oauth2_scheme)
):

    email = get_current_user_email(token)

    if not email:
        return {
            "message": "Invalid or expired token"
        }

    if not is_admin(token):
        return {
            "message": "Admin access required"
        }

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users(name, age, email)
            VALUES (?, ?, ?)
            """,
            (
                user.name,
                user.age,
                user.email
            )
        )

        connection.commit()

        return {
            "message": "User created successfully",
            "user": user
        }

    except Exception as e:

        return {
            "error": str(e)
        }

    finally:

        connection.close()
@app.get("/users")
def get_users(
    token: str = Depends(oauth2_scheme)
):

    email = get_current_user_email(token)

    if not email:
        return {
            "message": "Invalid or expired token"
        }

    if not is_admin(token):
        return {
            "message": "Admin access required"
        }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        """
    )

    users = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return users
@app.get("/users/{name}")
def search_user(name: str):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        WHERE LOWER(name) = LOWER(?)
        """,
        (name,)
    )

    user = cursor.fetchone()

    connection.close()

    if user:
        return dict(user)

    return {
        "message": "User not found"
    }
@app.delete("/users/{name}")
def delete_user(
    name: str,
    token: str = Depends(oauth2_scheme)
):

    email = get_current_user_email(token)

    if not email:
        return {
            "message": "Invalid or expired token"
        }

    if not is_admin(token):
        return {
            "message": "Admin access required"
        }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM users
        WHERE LOWER(name) = LOWER(?)
        """,
        (name,)
    )

    connection.commit()

    if cursor.rowcount == 0:

        connection.close()

        return {
            "message": "User not found"
        }

    connection.close()

    return {
        "message": "User deleted successfully"
    }

# DOCTOR MANAGEMENT
# =====================================================
@app.get("/doctors")
def get_doctors():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM doctors"
    )

    doctors = cursor.fetchall()

    connection.close()

    return [
        dict(doctor)
        for doctor in doctors
    ]
# APPOINTMENT MANAGEMENT
# =====================================================
class Doctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    experience: int = Field(..., ge=0, le=60)
    consultation_fee: int = Field(..., gt=0)
    available: bool = True
@app.get("/appointments")
def get_appointments(

):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM appointments"
    )

    appointments = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()
    print(appointments)
    return appointments

@app.post("/appointments")
def create_appointment(
            appointment: Appointment,
            token: str = Depends(oauth2_scheme)
    ):

        email = get_current_user_email(token)

        if not email:
            return {
                "message": "Invalid or expired token"
            }

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT consultation_fee
            FROM doctors
            WHERE name = ?
            """,
            (appointment.doctor,)
        )

        doctor = cursor.fetchone()

        if not doctor:
            connection.close()

            return {
                "message": "Doctor not found"
            }

        appointment_id = str(uuid.uuid4())

        fee = doctor["consultation_fee"]

        cursor.execute(
            """
            INSERT INTO appointments
            (id,
             patient,
             doctor,
             hospital,
             date,
             time,
             fee)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                appointment_id,
                email,
                appointment.doctor,
                appointment.hospital,
                appointment.date,
                appointment.time,
                fee
            )
        )

        connection.commit()
        connection.close()

        return {
            "message": "Appointment created successfully",
            "appointment_id": appointment_id,
            "patient": email,
            "doctor_fee": fee
        }



@app.put("/users/{name}")
def update_user(
    name: str,
    key: str,
    value: str,
    token: str = Depends(oauth2_scheme)
):

    email = get_current_user_email(token)

    if not email:
        return {
            "message": "Invalid or expired token"
        }

    if not is_admin(token):
        return {
            "message": "Admin access required"
        }

    allowed_fields = ["name", "age", "email"]

    if key not in allowed_fields:
        return {
            "message": "Invalid field"
        }

    connection = get_connection()
    cursor = connection.cursor()

    query = f"""
    UPDATE users
    SET {key} = ?
    WHERE LOWER(name) = LOWER(?)
    """

    cursor.execute(
        query,
        (value, name)
    )

    connection.commit()

    if cursor.rowcount == 0:

        connection.close()

        return {
            "message": "User not found"
        }

    connection.close()

    return {
        "message": "User updated successfully"
    }



# =====================================================
# ANALYTICS
# =====================================================
@app.get("/analytics")
def analytics(
    token: str = Depends(oauth2_scheme)
):

    email = get_current_user_email(token)

    if not email:
        return {
            "message": "Invalid or expired token"
        }

    if not is_admin(token):
        return {
            "message": "Admin access required"
        }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM doctors")
    total_doctors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COALESCE(SUM(fee), 0) FROM appointments"
    )
    total_revenue = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM doctors WHERE available = 1"
    )
    available_doctors = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM doctors WHERE available = 0"
    )
    unavailable_doctors = cursor.fetchone()[0]

    average_revenue = (
        total_revenue / total_appointments
        if total_appointments > 0
        else 0
    )

    connection.close()

    return {
        "total_users": total_users,
        "total_doctors": total_doctors,
        "available_doctors": available_doctors,
        "unavailable_doctors": unavailable_doctors,
        "total_appointments": total_appointments,
        "total_revenue": total_revenue,
        "average_revenue": round(
            average_revenue,
            2
        )
    }


# BMI CALCULATOR
# =====================================================
class HealthScoreRequest(BaseModel):
    age: int = Field(..., gt=0, le=120, description="Age in years")
    weight: float = Field(..., gt=0, description="Weight in KG")
    height: float = Field(..., gt=0, description="Height in CM")


class HealthScoreResponse(BaseModel):
    bmi: float
    bmi_category: str
    health_score: int
    risk_level: str
    recommendation: str
@app.post(
    "/bmi",
    response_model=BMIResponse,
    tags=["Health"]
)
def calculate_bmi(data: BMIRequest):

    bmi = data.weight / ((data.height / 100) ** 2)

    if bmi < 18.5:

        category = "Underweight"
        health_risk = "Moderate"
        recommendation = (
            "Increase calorie intake and focus on "
            "a balanced nutrient-rich diet."
        )

    elif bmi < 25:

        category = "Normal"
        health_risk = "Low"
        recommendation = (
            "Maintain your current lifestyle "
            "with regular exercise and healthy nutrition."
        )

    elif bmi < 30:

        category = "Overweight"
        health_risk = "Moderate"
        recommendation = (
            "Reduce processed foods, increase physical activity, "
            "and monitor calorie consumption."
        )

    else:

        category = "Obese"
        health_risk = "High"
        recommendation = (
            "Consult a healthcare professional and "
            "follow a structured weight management plan."
        )

    return BMIResponse(
        bmi=round(bmi, 2),
        category=category,
        health_risk=health_risk,
        recommendation=recommendation

    )
# =====================================================
# HEALTH SCORE
# =====================================================

@app.post(
    "/health-score",
    response_model=HealthScoreResponse,
    tags=["Health"]
)
def calculate_health_score(data: HealthScoreRequest):

    bmi = data.weight / ((data.height / 100) ** 2)
    bmi = round(bmi, 2)

    score = 100

    if bmi < 18.5:
        bmi_category = "Underweight"
        score -= 20

    elif bmi < 25:
        bmi_category = "Normal"

    elif bmi < 30:
        bmi_category = "Overweight"
        score -= 15

    else:
        bmi_category = "Obese"
        score -= 30

    if data.age >= 40:
        score -= 5

    if data.age >= 60:
        score -= 10

    score = max(score, 0)

    if score >= 90:
        risk_level = "Low"
        recommendation = (
            "Excellent health status. Continue your "
            "healthy lifestyle and regular exercise."
        )

    elif score >= 70:
        risk_level = "Moderate"
        recommendation = (
            "Good health condition. Focus on nutrition, "
            "sleep quality and physical activity."
        )

    elif score >= 50:
        risk_level = "High"
        recommendation = (
            "Health improvements recommended. Monitor BMI, "
            "exercise regularly and consult a nutrition expert."
        )

    else:
        risk_level = "Critical"
        recommendation = (
            "Immediate lifestyle intervention recommended. "
            "Consult a healthcare professional."
        )

    return HealthScoreResponse(
        bmi=bmi,
        bmi_category=bmi_category,
        health_score=score,
        risk_level=risk_level,
        recommendation=recommendation
    )
@app.post("/doctors")
def create_doctor(
    doctor: Doctor
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO doctors (
            name,
            specialization,
            experience,
            consultation_fee,
            available
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            doctor.name,
            doctor.specialization,
            doctor.experience,
            doctor.consultation_fee,
            int(doctor.available)
        )
    )

    connection.commit()
    connection.close()

    return {
        "message": "Doctor added successfully"
    }

@app.get("/doctors/{doctor_id}")
def get_doctor(
    doctor_id: int,
    token: str = Depends(oauth2_scheme)
):

    email = get_current_user_email(token)

    if not email:
        return {
            "message": "Invalid or expired token"
        }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM doctors
        WHERE id = ?
        """,
        (doctor_id,)
    )

    doctor = cursor.fetchone()

    connection.close()

    if not doctor:
        return {
            "message": "Doctor not found"
        }

    return dict(doctor)
@app.get("/doctors/search/{specialization}")
def search_doctors(
    specialization: str,
    token: str = Depends(oauth2_scheme)
):

    email = get_current_user_email(token)

    if not email:
        return {
            "message": "Invalid or expired token"
        }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM doctors
        WHERE LOWER(specialization) = LOWER(?)
        """,
        (specialization,)
    )

    doctors = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return doctors
@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM appointments WHERE id = ?",
        (appointment_id,)
    )

    connection.commit()

    if cursor.rowcount == 0:

        connection.close()

        return {
            "message": "Appointment not found"
        }

    connection.close()

    return {
        "message": "Appointment deleted successfully"
    }
@app.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: int,
    key: str,
    value: str,
    token: str = Depends(oauth2_scheme)
):

    email = get_current_user_email(token)

    if not email:
        return {
            "message": "Invalid or expired token"
        }

    if not is_admin(token):
        return {
            "message": "Admin access required"
        }

    allowed_fields = [
        "name",
        "specialization",
        "experience",
        "consultation_fee"
    ]

    if key not in allowed_fields:
        return {
            "message": "Invalid field"
        }

    connection = get_connection()
    cursor = connection.cursor()

    query = f"""
    UPDATE doctors
    SET {key} = ?
    WHERE id = ?
    """

    cursor.execute(
        query,
        (value, doctor_id)
    )

    connection.commit()

    if cursor.rowcount == 0:

        connection.close()

        return {
            "message": "Doctor not found"
        }

    connection.close()

    return {
        "message": "Doctor updated successfully"
    }
@app.get("/my-appointments")
def get_my_appointments(
    token: str = Depends(oauth2_scheme)
):

    email = get_current_user_email(token)

    if not email:
        return {
            "message": "Invalid or expired token"
        }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM appointments
        WHERE patient = ?
        """,
        (email,)
    )

    appointments = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return appointments
@app.delete("/appointments/{appointment_id}")
def cancel_appointment(
    appointment_id: str,
    token: str = Depends(oauth2_scheme)
):

    email = get_current_user_email(token)

    if not email:
        return {
            "message": "Invalid or expired token"
        }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM appointments
        WHERE id = ?
        AND patient = ?
        """,
        (
            appointment_id,
            email
        )
    )

    connection.commit()

    if cursor.rowcount == 0:

        connection.close()

        return {
            "message": "Appointment not found"
        }

    connection.close()

    return {
        "message": "Appointment cancelled successfully"
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

