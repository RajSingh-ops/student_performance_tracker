from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key, "")
    except:
        return ""
@register.filter
def get_subject_value(obj, subject):
    """Get the value of a subject field from entry object"""
    try:
        field_name = f'{subject}_description'
        return getattr(obj, field_name, "") if obj else ""
    except:
        return ""