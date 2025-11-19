from django import template

register = template.Library()

@register.filter
def get_progress_color(counter):
    colors = ['#5a8dee', '#50cd89', '#f1416c', '#7239ea', '#ffc700']
    return colors[counter % len(colors)]