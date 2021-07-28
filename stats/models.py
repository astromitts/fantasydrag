from django.db import models
from django.db.models import Sum

from fantasydrag.models import (
    Draft,
    DragRace,
    Episode,
    Panel,
    Participant,
    Queen,
    Score
)


class StatModelBase(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def get_or_create(cls, **kwargs):
        existing = cls.objects.filter(**kwargs)
        if existing.exists():
            instance = existing.first()
        else:
            instance = cls(**kwargs)
            instance.save()
        return instance

    @classmethod
    def destroy(cls, **kwargs):
        cls.objects.filter(**kwargs).delete()

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        instance.save()
        return instance


class QueenEpisodeScoreBase(StatModelBase):
    class Meta:
        abstract = True

    queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0, db_index=True)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)

    @property
    def episode_scores(self):
        return Score.objects.filter(episode=self.episode, queen=self.queen)

    def set_total_score(self):
        episode_sum = Score.objects.filter(
            episode=self.episode, queen=self.queen
        ).aggregate(Sum('default_rule__point_value'))
        if episode_sum['default_rule__point_value__sum'] is not None:
            self.total_score = episode_sum['default_rule__point_value__sum']
            self.save()
        else:
            self.delete()


class CanonicalQueenEpisodeScore(QueenEpisodeScoreBase):
    pass


class QueenEpisodeScore(QueenEpisodeScoreBase):
    viewing_participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name='viewingparticipant_queen_episode_score')


class QueenDragRaceScoreBase(StatModelBase):
    class Meta:
        abstract = True
    queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0, db_index=True)
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)

    @property
    def score_qs(self):
        return None

    @property
    def scores(self):
        return self.score_qs.all()

    def set_total_score(self):
        episode_sum = self.score_qs.aggregate(Sum('total_score'))
        if episode_sum['total_score__sum']:
            self.total_score = episode_sum['total_score__sum']
        else:
            self.total_score = 0
        self.save()


class CanonicalQueenDragRaceScore(QueenDragRaceScoreBase):

    @property
    def score_qs(self):
        return CanonicalQueenEpisodeScore.objects.filter(
            episode__drag_race=self.drag_race, queen=self.queen
        )


class QueenDragRaceScore(QueenDragRaceScoreBase):
    viewing_participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name='viewingparticipant_queen_dragrace_score')

    @property
    def score_qs(self):
        return QueenEpisodeScore.objects.filter(
            episode__drag_race=self.drag_race, queen=self.queen, viewing_participant=self.viewing_participant
        )


class PanelistEpisodeScore(StatModelBase):
    viewing_participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name='viewingparticipant_panelist_episode_score')
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)
    panelist = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name='targetparticipant_panelist_episode_score')
    total_score = models.IntegerField(default=0, db_index=True)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    @property
    def drafted_queens(self):
        drafts = Draft.objects.filter(
            participant=self.panelist,
            panel=self.panel
        )
        return [d.queen for d in drafts.all()]

    @property
    def scores(self):
        return QueenEpisodeScore.objects.filter(
            episode=self.episode,
            queen__in=self.drafted_queens,
            viewing_participant=self.viewing_participant
        ).all()

    def set_total_score(self):
        episode_sum = QueenEpisodeScore.objects.filter(
            episode=self.episode,
            queen__in=self.drafted_queens,
            viewing_participant=self.viewing_participant
        ).aggregate(Sum('total_score'))
        if episode_sum['total_score__sum']:
            self.total_score = episode_sum['total_score__sum']
        else:
            self.total_score = 0
        self.save()


class PanelistDragRaceScore(StatModelBase):
    viewing_participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name='viewingparticipant_panelist_dragrace_score')
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
    panelist = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name='targetparticipant_panelist_dragrace_score')
    total_score = models.IntegerField(default=0, db_index=True)

    def set_total_score(self):
        episode_sum = PanelistEpisodeScore.objects.filter(
            episode__drag_race=self.drag_race, panelist=self.panelist, viewing_participant=self.viewing_participant
        ).aggregate(Sum('total_score'))
        if episode_sum['total_score__sum']:
            self.total_score = episode_sum['total_score__sum']
        else:
            self.total_score = 0
        self.save()