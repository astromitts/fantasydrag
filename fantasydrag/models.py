from django.contrib.auth.models import User
from django.db import models
import math


class Queen(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ('name', )

    @classmethod
    def get_formatted_scores_for_drag_race(cls, drag_race, participant):
        scores = {q: 0 for q in drag_race.queens.all()}
        for episode in drag_race.participant_episodes(participant):
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

    @property
    def scored_episodes(self):
        return self.episode_set.filter(is_scored=True).all()

    def participant_episodes(self, participant):
        participant_episode_ids = [e.id for e in participant.episodes.all()]
        return self.episode_set.filter(id__in=participant_episode_ids).all()

    def get_scores_by_episode(self, participant):
        episodes = {e: {q: {'total': 0, 'rules': []} for q in self.queens.all()} for e in self.participant_episodes(participant)} # noqa
        _scores = Score.objects.filter(episode__in=list(episodes.keys())).all()
        for s in _scores:
            episodes[s.episode][s.queen]['total'] += s.rule.point_value
            episodes[s.episode][s.queen]['rules'].append(s.rule)
        return episodes


class Episode(models.Model):
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
    number = models.IntegerField()
    is_scored = models.BooleanField(default=False)

    class Meta:
        ordering = ('number', )

    def __str__(self):
        return '{} episode #{}'.format(self.drag_race, self.number)


class Rule(models.Model):
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField()
    point_value = models.IntegerField(default=1)

    class Meta:
        ordering = ('point_value', 'name')

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
    site_admin = models.BooleanField(default=False)
    episodes = models.ManyToManyField(Episode)

    def get_formatted_scores_for_panel(self, panel, viewing_participant):
        drafts = Draft.objects.filter(participant=self, panel=panel).all()
        scores = {d.queen: 0 for d in drafts}
        panel_episodes = panel.drag_race.participant_episodes(viewing_participant)

        for episode in panel.drag_race.episode_set.filter(id__in=[e.id for e in panel_episodes]).all():
            _scores = episode.score_set.filter(queen__in=[k for k, v in scores.items()]).all()
            for s in _scores:
                scores[s.queen] += s.rule.point_value
        return scores

    def __str__(self):
        return self.name


class Panel(models.Model):
    name = models.CharField(max_length=250, unique=True)
    participants = models.ManyToManyField(Participant)
    captains = models.ManyToManyField(Participant, related_name='panelcaptains')
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
    queen_draft_allowance = models.IntegerField(
        default=1,
        help_text='The number of times a Queen can be drafted to a unique player'
    )
    draft_data = models.JSONField(default=dict, blank=True, null=True)
    status = models.CharField(
        max_length=25,
        choices=[
            ('open', 'open'),
            ('in draft', 'in draft'),
            ('active', 'active'),
            ('closed', 'closed'),
        ],
        default='open'
    )

    def set_random_drafts(self):
        self.draft_set.all().delete()
        self.draft_data = {}
        random_order_participants = self.participants.order_by('?').all()
        max_team_size = math.ceil(
            self.drag_race.queens.count() * self.queen_draft_allowance / self.participants.count()
        )

        assigned_queens_counts = {queen: 0 for queen in self.drag_race.queens.all()}
        player_assignments = {p.name: [] for p in self.participants.all()}

        for x in range(1, max_team_size + 1):
            self.draft_data['loop {}'.format(x)] = {}
            y = 1
            for participant in random_order_participants:
                self.draft_data['loop {}'.format(x)]['participant {}'.format(y)] = {}
                maxed_out_queens = []
                for queen, count in assigned_queens_counts.items():
                    if count >= self.queen_draft_allowance:
                        maxed_out_queens.append(queen.pk)

                if len(maxed_out_queens) == self.drag_race.queens.count():
                    assigned_queens_counts = {queen: 1 for queen in self.drag_race.queens.all()}
                    maxed_out_queens = []

                existing_drafts_for_participant = Draft.objects.filter(participant=participant, panel=self).all()
                existing_queens_for_participant = [draft.queen.pk for draft in existing_drafts_for_participant]
                exclude_queens = list(set(existing_queens_for_participant + maxed_out_queens))
                random_queen = self.drag_race.queens.exclude(pk__in=exclude_queens).order_by('?').first()

                new_draft = Draft(
                    participant=participant,
                    queen=random_queen,
                    panel=self,
                    round_selected=x
                )
                new_draft.save()
                assigned_queens_counts[random_queen] = assigned_queens_counts.get(random_queen, 0)
                assigned_queens_counts[random_queen] += 1
                player_assignments[participant.name].append(random_queen.name)
                self.draft_data['loop {}'.format(x)]['participant {}'.format(y)]['participant'] = participant.name
                self.draft_data['loop {}'.format(x)]['participant {}'.format(y)]['queen'] = random_queen.name
                y += 1
                self.save()

        self.status = 'active'
        self.save()

    @property
    def default_draft_data(self):
        return {
            'participant_order': [],
            'current_participant': None,
            'draft_index': 1,
            'can_go_to_next_round': False,
            'can_end_draft': False,
            'round 1': []
        }

    @property
    def ordered_participants(self):
        participants = []
        for participant_pk in self.draft_data['participant_order']:
            participants.append(self.participants.get(pk=participant_pk))
        return participants

    def start_draft(self):
        self.draft_set.all().delete()
        self.draft_data = self.default_draft_data
        self.status = 'in draft'

        random_order_participants = self.participants.order_by('?').all()
        i = 1
        for p in random_order_participants:
            self.draft_data['participant_order'].append(p.pk)
            if i == 1:
                self.draft_data['current_participant'] = p.pk

            i += 1
        self.save()

    def advance_draft(self):
        if self.draft_data['current_participant'] == self.draft_data['participant_order'][-1]:
            self.draft_data['current_participant'] = self.draft_data['participant_order'][0]
        else:
            current_index = self.draft_data['participant_order'].index(self.draft_data['current_participant'])
            self.draft_data['current_participant'] = self.draft_data['participant_order'][current_index + 1]
        self.save()

    def end_draft(self):
        self.status = 'active'
        self.save()

    def advance_round(self):
        self.draft_data['draft_index'] += 1
        roundkey = 'round {}'.format(self.draft_data['draft_index'])
        self.draft_data[roundkey] = []
        self.draft_data['can_go_to_next_round'] = False
        self.save()

    def check_round_status(self):
        can_advance = True
        roundkey = 'round {}'.format(self.draft_data['draft_index'])
        this_round = self.draft_data[roundkey] = self.draft_data.get(roundkey, [])
        for participant in self.participants.all():
            if participant.pk not in this_round:
                can_advance = False
        if can_advance:
            self.draft_data['can_go_to_next_round'] = True
            self.draft_data['can_end_draft'] = True
            self.save()

    def save_player_draft(self, participant, queen):
        new_draft = Draft(
            participant=participant,
            queen=queen,
            panel=self,
            round_selected=self.draft_data['draft_index']
        )
        new_draft.save()
        roundkey = 'round {}'.format(self.draft_data['draft_index'])
        self.draft_data[roundkey] = self.draft_data.get(roundkey, [])
        if participant.pk not in self.draft_data[roundkey]:
            self.draft_data[roundkey].append(participant.pk)
        self.save()
        self.check_round_status()

    @property
    def current_draft_player(self):
        if self.status == 'in draft':
            return self.participants.get(pk=self.draft_data['current_participant'])

    def get_formatted_scores_for_panelists(self, participant):
        queen_scores = Queen.get_formatted_scores_for_drag_race(self.drag_race, participant)
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
    round_selected = models.IntegerField(default=1)

    def __str__(self):
        return '{}, {}::{}'.format(self.panel, self.participant, self.queen)


class WildCardQueen(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)

    def __str__(self):
        return '{}, {}::{}'.format(self.panel, self.participant, self.queen)


class WildCardAppearance(models.Model):
    queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.queen, self.episode)
