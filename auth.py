from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, UTC

# =====================================================
# PASSWORD HASHING
# =====================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# =====================================================
# JWT CONFIG
# =====================================================

SECRET_KEY = "ailifeos_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# =====================================================
# PASSWORD FUNCTIONS
# =====================================================

def hash_password(password: str):

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )

# =====================================================
# JWT FUNCTIONS
# =====================================================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {"exp": expire}
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_token(token: str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        print("PAYLOAD:", payload)

        return payload

    except Exception as e:
        print("JWT ERROR:", e)
        return None
def get_current_user_email(token: str):

        payload = verify_token(token)

        if not payload:
            return None

        return payload.get("sub")

def get_current_user_role(token: str):

        payload = verify_token(token)

        if not payload:
            return None

        return payload.get("role")

def is_admin(token: str):

        role = get_current_user_role(token)

        return role == "admin"

def get_current_user_role(token: str):

    payload = verify_token(token)

    if not payload:
        return None

    return payload.get("role")


def is_admin(token: str):

    role = get_current_user_role(token)

    return role == "admin"
# =====================================================
# TESTING
# =====================================================

if __name__ == "__main__":

    token = create_access_token(
        {
            "sub": "ranveer"
        }
    )

    print("TOKEN:")
    print(token)

    print("\nPAYLOAD:")
    print(
        verify_token(token)
    )






