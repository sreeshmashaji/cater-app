
from fastapi import HTTPException
import re

def validate_password(password: str):
    # Check if password contains at least one capital letter
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one capital letter"
    # Check if password contains at least one special symbol
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special symbol"
    # Check if password contains at least one number
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"