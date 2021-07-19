from django import template
from fantasydrag.models import (
    Draft,
    Stats,
    Queen,
)

register = template.Library()


@register.filter(name='pdb')
def pdb(item, item2=None):
    import pdb  # noqa
    pdb.set_trace()  # noqa


@register.filter(name='get')
def get(sourcedict, key):
    return sourcedict.get(key)


@register.filter(name='get_as_str')
def get_as_str(sourcedict, key):
    return sourcedict.get(str(key))


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


@register.filter(name='episode_drag_race_draft')
def episode_drag_race_draft(participant, drag_race):
    panel = participant.episodedraft_set.filter(episode=drag_race.next_episode).first()
    return panel


@register.filter(name='episode_draft')
def episode_draft(participant, episode):
    episode_draft = participant.episodedraft_set.filter(episode=episode).first()
    return episode_draft


@register.filter(name='participant_drag_race_stats')
def participant_drag_race_stats(participant, drag_race):
    pstats = Stats.objects.filter(
        participant=participant,
        drag_race=drag_race,
        stat_type='cummulative_dragrace_drafts'
    ).first()
    if pstats:
        return pstats
    else:
        return None


@register.filter(name='participant_drag_race_rank')
def participant_drag_race_rank(participant, drag_race):
    pstats = Stats.objects.filter(
        participant=participant,
        drag_race=drag_race,
        stat_type='dragrace_rank'
    ).first()
    if pstats:
        return pstats
    else:
        return None


@register.filter(name='number')
def number(float_value):
    if float_value == 0:
        return 0
    if float_value:
        if float_value % 1 == 0:
            return int(float_value)
    return float_value
