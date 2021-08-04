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
    WildCardAppearance,
    ScoreClass
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
    total_score = models.IntegerField(default=0, db_index=True)
    rank_tier = models.IntegerField(default=0)
    total_participants = models.IntegerField(default=0)

    @classmethod
    def reset_or_create(cls, **kwargs):
        existing = cls.objects.filter(**kwargs)
        if existing.exists():
            instance = existing.first()
            instance.total_score = 0
            instance.rank_tier = 0
            instance.total_participants = 0
            instance.save()
        else:
            instance = cls(**kwargs)
            instance.save()
        return instance


class EpisodeDraftScore(ParticipantEpisodeDraftScoreBase):
    episodedraft = models.ForeignKey(EpisodeDraft, on_delete=models.CASCADE)
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='episode_draftscore_target_participant'

    )

    @property
    def episode(self):
        return self.episodedraft.episode

    @property
    def drag_race(self):
        return self.episodedraft.drag_race

    @property
    def drafted_queens(self):
        return self.episodedraft.queens

    def set_total_score(self):
        episode_sum = Score.objects.filter(
            episode=self.episode,
            queen__in=self.drafted_queens.all()
        ).aggregate(Sum('default_rule__point_value'))
        if episode_sum['default_rule__point_value__sum'] is not None:
            self.total_score = episode_sum['default_rule__point_value__sum']
        else:
            self.total_score = 0
        self.save()


class DragRaceDraftScore(ParticipantEpisodeDraftScoreBase):
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
        draft_sum = self.participant_draft_qs.aggregate(Sum('total_score'))
        if draft_sum['total_score__sum'] is not None:
            self.total_score = draft_sum['total_score__sum']
        else:
            self.total_score = 0
        self.save()


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
    main_wins = models.IntegerField(default=0)
    mini_wins = models.IntegerField(default=0)
    lipsync_wins = models.IntegerField(default=0)
    safe_count = models.IntegerField(default=0)
    eliminated_count = models.IntegerField(default=0)
    bottom_count = models.IntegerField(default=0)

    @property
    def score_qs(self):
        return None

    @property
    def score_class_map(self):
        return {
            ScoreClass.objects.get(name='main_win'): 'main_wins',
            ScoreClass.objects.get(name='mini_win'): 'mini_wins',
            ScoreClass.objects.get(name='lipsync_win'): 'lipsync_wins',
            ScoreClass.objects.get(name='safe'): 'safe_count',
            ScoreClass.objects.get(name='elimination'): 'eliminated_count',
            ScoreClass.objects.get(name='bottom'): 'bottom_count',
            ScoreClass.objects.get(name='stay'): 'bottom_count',
        }

    @property
    def scores(self):
        return self.score_qs.all()

    @property
    def episodes(self):
        return self.viewing_participant.episodes.filter(drag_race=self.drag_race).all()

    @property
    def queen_scores(self):
        return Score.objects.filter(
            episode__in=self.episodes,
            queen=self.queen
        ).all()

    def set_total_score(self):
        episode_sum = self.score_qs.aggregate(Sum('total_score'))
        if episode_sum['total_score__sum']:
            self.total_score = episode_sum['total_score__sum']
        else:
            self.total_score = 0
        self.save()
        self.set_total_stats()

    def set_total_stats(self):
        self.main_wins = 0
        self.mini_wins = 0
        self.lipsync_wins = 0
        self.safe_count = 0
        self.eliminated_count = 0
        self.bottom_count = 0

        score_class_map = self.score_class_map
        for score in self.queen_scores:
            for score_class in score.rule.score_classes.all():
                if score_class in score_class_map:
                    current_count = getattr(self, score_class_map[score_class])
                    setattr(self, score_class_map[score_class], current_count + 1)
        self.save()


class CanonicalQueenDragRaceScore(QueenDragRaceScoreBase):

    @property
    def score_qs(self):
        return CanonicalQueenEpisodeScore.objects.filter(
            episode__drag_race=self.drag_race, queen=self.queen
        )

    @property
    def queen_scores(self):
        return Score.objects.filter(
            episode__drag_race=self.drag_race,
            queen=self.queen
        ).all()


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
