from django.db import models
from django.db.models import Sum

from fantasydrag.models import (
    Draft,
    DragRace,
    Episode,
    EpisodeDraft,
    Panel,
    Participant,
    Queen,
    Score,
    WildCardQueen,
    WildCardAppearance
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


class ParticipantEpisodeDraftScoreBase(StatModelBase):
    class Meta:
        abstract = True
    total_score = models.IntegerField(default=0)
    rank_tier = models.IntegerField(default=0)
    total_participants = models.IntegerField(default=0)


class EpisodeDraftScores(ParticipantEpisodeDraftScoreBase):
    episodedraft = models.ForeignKey(EpisodeDraft, on_delete=models.CASCADE)
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='episode_draftscore_target_participant'

    )

    @classmethod
    def set_episode_scores(cls):
        pass

    def set_total_score(self):
        episode_sum = Score.objects.filter(
            episode=self.episodedraft.episode,
            queen__in=self.episodedraft.queens.all()
        ).aggregate(Sum('default_rule__point_value'))
        if episode_sum['default_rule__point_value__sum'] is not None:
            self.score = episode_sum['default_rule__point_value__sum']
            self.save()
        else:
            self.delete()


class DragRaceDraftScores(ParticipantEpisodeDraftScoreBase):
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='dragrace_draftscore_target_participant'

    )

    @property
    def participant_draft_qs(self):
        return EpisodeDraft.objects.filter(
            episode__in=self.drag_race.episode,
            participant=self.viewing_participant
        )

    @property
    def all_draft_qs(self):
        return EpisodeDraft.objects.filter(
            episode__in=self.drag_race.episode
        )

    def set_total_score(self):
        draft_sum = self.participant_draft_qs.aggregate(Sum('score'))
        if draft_sum['score__sum'] is not None:
            self.total_score = draft_sum['score__sum']
            self.save()
        else:
            self.total_score = 0


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
    total_score = models.FloatField(
        default=0,
        db_index=True
    )
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    @property
    def drafted_queens(self):
        drafts = Draft.objects.filter(
            participant=self.panelist,
            panel=self.panel
        )
        return [d.queen for d in drafts.all()]

    @property
    def wildcard_queens(self):
        wildcard_drafts = WildCardQueen.objects.filter(
            participant=self.panelist,
            panel=self.panel
        )
        return [d.queen for d in wildcard_drafts.all()]

    @property
    def scores(self):
        return QueenEpisodeScore.objects.filter(
            episode=self.episode,
            queen__in=self.drafted_queens,
            viewing_participant=self.viewing_participant
        ).all()

    @property
    def wildcard_scores(self):
        return WildCardAppearance.objects.filter(
            episode=self.episode,
            queen__in=self.wildcard_queens
        ).all()

    def set_total_score(self):
        episode_sum = QueenEpisodeScore.objects.filter(
            episode=self.episode,
            queen__in=self.drafted_queens,
            viewing_participant=self.viewing_participant
        ).aggregate(Sum('total_score'))

        wildcard_sum = 0
        for wqa in self.wildcard_scores:
            wildcard_sum += wqa.appearance.point_value

        if episode_sum['total_score__sum']:
            self.total_score = float(episode_sum['total_score__sum'])
        else:
            self.total_score = 0
        self.total_score += float(wildcard_sum)
        self.save()


class PanelistDragRaceScore(StatModelBase):
    viewing_participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name='viewingparticipant_panelist_dragrace_score')
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
    panelist = models.ForeignKey(
        Participant, on_delete=models.CASCADE, related_name='targetparticipant_panelist_dragrace_score')
    total_score = models.FloatField(
        default=0,
        db_index=True
    )

    def set_total_score(self):
        episode_sum = PanelistEpisodeScore.objects.filter(
            episode__drag_race=self.drag_race, panelist=self.panelist, viewing_participant=self.viewing_participant
        ).aggregate(Sum('total_score'))
        if episode_sum['total_score__sum']:
            self.total_score = float(episode_sum['total_score__sum'])
        else:
            self.total_score = 0
        self.save()
