from datetime import timedelta
from django.utils.timezone import now
from fantasydrag.models import Panel


def set_test_panels(time_now):
    test_panel_pks = [3, 2, 6]
    Panel.objects.filter(pk__in=test_panel_pks).update(status='open')

    near_panel = Panel.objects.get(pk=3)
    near_panel.status = 'open'
    near_panel.draft_time = time_now - timedelta(minutes=1)
    near_panel.save()

    future_panel = Panel.objects.get(pk=2)
    future_panel.draft_time = time_now + timedelta(minutes=6)
    future_panel.save()

    on_the_dot_panel = Panel.objects.get(pk=6)
    on_the_dot_panel.draft_time = time_now + timedelta(minutes=5)
    on_the_dot_panel.save()


def start_drafts(testing=False):
    time_now = now()
    if testing:
        set_test_panels(time_now)

    near_panels = Panel.objects.filter(
        draft_time__gte=time_now
    ).all()
    for panel in near_panels:
        panel.start_draft()
    return near_panels
