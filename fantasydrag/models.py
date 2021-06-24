from django.contrib.auth.models import User
from django.db import models


class Queen(models.Model):
    name = models.CharField(max_length=100)

    @classmethod
    def get_formatted_scores_for_drag_race(cls, drag_race):
        scores = {q: 0 for q in drag_race.queens.all()}
        for episode in drag_race.episode_set.all():
            _scores = episode.score_set.all()
            for s in _scores:
                scores[s.queen] += s.rule.point_value
        return scores

    def get_episode_scores_for_drag_race(self, drag_race):
        episodes = {e: 0 for e in drag_race.episode_set.all()}
        _scores = Score.filter(queen=self, episode__in=list(episodes.keys())).all()
        for s in _scores:
            episodes[s.episode] += s.rule.point_value
        return episodes

    def __str__(self):
        return self.name


class DragRace(models.Model):
    season = models.IntegerField()
    race_type = models.CharField(
        max_length=25,
        choices=[
            ('standard', 'standard'),
            ('all star', 'all star')
        ]
    )
    queens = models.ManyToManyField(Queen)
    franchise = models.CharField(
        max_length=100,
        choices=[
            ('US', 'US'),
            ('Down Under', 'Down Under'),
            ('UK', 'UK'),
            ('Canada', 'Canada')
        ],
        default='US'
    )

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        display_name_parts = ['Drag Race', ]
        if self.franchise != 'US':
            display_name_parts.append(self.franchise)
        if self.race_type == 'all star':
            display_name_parts.append('All Stars')
        display_name_parts.append('{}'.format(self.season))
        return ' '.join(display_name_parts)

    def get_scores_by_episode(self):
        episodes = {e: {q: {'total': 0, 'rules': []} for q in self.queens.all()} for e in self.episode_set.all()}
        _scores = Score.objects.filter(episode__in=list(episodes.keys())).all()
        for s in _scores:
            episodes[s.episode][s.queen]['total'] += s.rule.point_value
            episodes[s.episode][s.queen]['rules'].append(s.rule)
        return episodes


class Episode(models.Model):
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
    number = models.IntegerField()

    def __str__(self):
        return '{} episode #{}'.format(self.drag_race, self.number)


class Rule(models.Model):
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField()
    point_value = models.IntegerField(default=1)

    def __str__(self):
        return '{}, "{}": ({} points) {}'.format(self.drag_race, self.name, self.point_value, self.description)


class Score(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)

    def __str__(self):
        return '{}: {} // {}'.format(self.queen, self.episode, self.rule)


class Participant(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def get_formatted_scores_for_panel(self, panel):
        drafts = Draft.objects.filter(participant=self, panel=panel).all()
        scores = {d.queen: 0 for d in drafts}
        for episode in panel.drag_race.episode_set.all():
            _scores = episode.score_set.filter(queen__in=list(scores.keys())).all()
            for s in _scores:
                scores[s.queen] += s.rule.point_value
        return scores

    def __str__(self):
        return self.name


class Panel(models.Model):
    name = models.CharField(max_length=250, unique=True)
    participants = models.ManyToManyField(Participant)
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
    queen_draft_allowance = models.IntegerField(
        default=1,
        help_text='The number of times a Queen can be drafted to a unique player'
    )

    def get_formatted_scores_for_panelists(self):
        queen_scores = Queen.get_formatted_scores_for_drag_race(self.drag_race)
        scores = {p: 0 for p in self.participants.all()}
        for participant in self.participants.all():
            drafts = Draft.objects.filter(
                queen__in=list(queen_scores.keys()), participant=participant)
            for draft in drafts:
                scores[participant] += queen_scores[draft.queen]
        return scores

    def __str__(self):
        return self.name


class Draft(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)

    def __str__(self):
        return '{}, {}::{}'.format(self.panel, self.participant, self.queen)
