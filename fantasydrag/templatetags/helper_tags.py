from django import template

register = template.Library()


@register.filter(name='get')
def get(source, key):
    return source.get(key)
