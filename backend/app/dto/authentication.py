import re

from pydantic import BaseModel, Field, field_validator

POPULAR_EMAIL_DOMAINS = {
    "gmail.com",
    "googlemail.com",
    "outlook.com",
    "hotmail.com",
    "live.com",
    "yahoo.com",
    "yahoo.in",
    "icloud.com",
    "proton.me",
    "protonmail.com"
}

class RegistrationData(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: str

    contact: str

    password: str = Field(
        ...,
        min_length=5
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):

        value = value.strip()

        if not re.fullmatch(
            r"[A-Za-z ]+",
            value
        ):
            raise ValueError(
                "Name can contain only letters and spaces"
            )

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):

        value = value.strip().lower()

        pattern = (
            r"^[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        )

        if not re.fullmatch(
            pattern,
            value
        ):
            raise ValueError(
                "Invalid email address"
            )

        domain = value.split("@")[1]

        if domain not in POPULAR_EMAIL_DOMAINS:
            raise ValueError(
                "Use a popular email provider such as "
                "Gmail, Outlook, Yahoo, Hotmail, "
                "iCloud or ProtonMail"
            )

        return value

    
    @field_validator("contact")
    @classmethod
    def validate_contact(cls, value):

        value = value.strip()

        # Exactly 10 digits.
        # First digit must be 6, 7, 8 or 9.
        if not re.fullmatch(
            r"[6-9][0-9]{9}",
            value
        ):
            raise ValueError(
                "Mobile number must be exactly "
                "10 digits and start with 6, 7, 8 or 9"
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        if len(value) < 5:
            raise ValueError(
                "Password must contain at least 5 characters"
            )

        return value

class LoginData(BaseModel):

    email_or_mobile: str = Field(
        ...,
        min_length=1
    )

    password: str = Field(
        ...,
        min_length=5
    )


class RegistrationPayload(BaseModel):
    registration: RegistrationData


class RegistrationRequest(BaseModel):
    message: str = Field(default="Registration")
    data: RegistrationPayload

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Registration",
                "data": {
                    "registration": {
                        "name": "John Doe",
                        "email": "john@example.com",
                        "contact": "9876543210",
                        "password": "Password@123"
                    }
                }
            }
        }
    }


class LoginPayload(BaseModel):
    login: LoginData


class LoginRequest(BaseModel):
    message: str = Field(default="Login")
    data: LoginPayload

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Login",
                "data": {
                    "login": {
                        "email_or_mobile": "john@example.com",
                        "password": "Password@123"
                    }
                }
            }
        }
    }
