import re



def validate_email(email: str) -> bool:
    # Regular expression pattern for basic email validation
    pattern = r'^[\w\.-]+[\w\.-]*@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(\.[a-zA-Z]{2,})?$'
    return re.match(pattern, email) is not None


# email-aaaamtj232gfdwwrcefmsdk7xa@axomium.slack.com