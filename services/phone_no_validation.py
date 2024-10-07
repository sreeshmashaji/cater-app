

import re

def validate_phone_number(phone_number: str) -> str:
    pattern = r'^\d+$'
    if not re.match(pattern, phone_number):
        return "Invalid phone number format (only digits allowed)"

    return phone_number