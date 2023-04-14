from django.core.exceptions import ValidationError
import re


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) <= 5:
            raise ValidationError("Password must be more than 5 characters.")

        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number.")

        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")

    def get_help_text(self):
        return "Password must be more than 5 characters, contain at least one number and one uppercase letter."
