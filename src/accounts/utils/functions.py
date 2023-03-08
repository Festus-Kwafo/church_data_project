from django.utils.html import strip_tags

def get_errors_from_form(forms):
    error =[]
    for field, er in forms.errors.items():
        title = field.title().replace("_", " ")
        error.append(f"{title}: {strip_tags(er)}")
        return "".join(error)