from django import template
from ..models import Champion

register = template.Library()

@register.filter
def cut_array(value, arg):
    return value[:arg]

@register.filter
def get_champion(value):
    return Champion.objects.get(champion_id = value).name