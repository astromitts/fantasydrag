from django import template
from fantasydrag.models import Draft

register = template.Library()


@register.filter(name='get')
def get(source, key):
    return source.get(key)


@register.filter(name='get_panelists_for_queen')
def get_panelists_for_queen(queen, panel):
    drafts = Draft.objects.filter(queen=queen, panel=panel).all()
    return ', '.join([d.participant.name for d in drafts])
