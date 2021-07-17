from django import template
from fantasydrag.models import Draft, Queen, Score

register = template.Library()


@register.filter(name='pdb')
def pdb(item):
    import pdb  # noqa
    pdb.set_trace()  # noqa


@register.filter(name='get')
def get(source, key):
    return source.get(key)


@register.filter(name='get_panelists_for_queen')
def get_panelists_for_queen(queen, panel):
    drafts = Draft.objects.filter(queen=queen, panel=panel).all()
    return ', '.join([d.participant.name for d in drafts])


@register.filter(name='wildcard_queens')
def wildcard_queens(participant, panel):
    return participant.wildcardqueen_set.filter(panel=panel).all()


@register.filter(name='wildcard_queens_for_episode')
def wildcard_queens_for_episode(episode):
    return episode.wildcardappearance_set.all()


@register.filter(name='available_wildcard_queens')
def available_wildcard_queens(participant, panel):
    this_season_queen_ids = [q.id for q in panel.drag_race.queens.all()]
    participant_wildcard_queen_ids = [q.id for q in participant.wildcardqueen_set.filter(panel=panel).all()]

    exclude_id_list = this_season_queen_ids + participant_wildcard_queen_ids

    return Queen.objects.exclude(id__in=exclude_id_list).all()


@register.filter(name='participant_drag_race_team')
def participant_drag_race_team(participant, drag_race):
    panel = participant.generalpanel_set.filter(drag_race=drag_race).first()
    return panel


@register.filter(name='formatted_general_draft')
def formatted_general_draft(generalpanel):
    general_draft = {
        'total': 0,
        'queens': {queen: 0 for queen in generalpanel.queens.all()}
    }
    for queen in generalpanel.queens.all():
        scores = Score.objects.filter(
            queen=queen,
            episode__in=generalpanel.drag_race.participant_episodes(generalpanel.participant),
        )
        for score in scores:
            general_draft['total'] += score.rule.point_value
            general_draft['queens'][queen] += score.rule.point_value
    return general_draft
