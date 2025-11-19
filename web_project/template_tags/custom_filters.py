from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get a dictionary value by key.
    Usage: {{ dictionary|get_item:key }}
    """
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)
