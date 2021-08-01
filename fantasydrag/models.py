import math
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.urls import reverse

from fantasydrag.utils import (
    DRAFT_CAPS,
    calculate_draft_data,
    refresh_dragrace_stats_for_participant
)

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User, dispatch_uid="create_user_participant")
def add_participant(sender, instance, **kwargs):
    try:
        instance.participant
    except Participant.DoesNotExist:
        new_participant = Participant(
            user=instance
        )
        new_participant.save()


class Queen(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    normalized_name = models.CharField(
        max_length=250,
        unique=True,
        db_index=True,
        blank=True,
        null=True,
    )
    main_franchise = models.CharField(
        max_length=100,
        choices=[
            ('US', 'US'),
            ('Australia', 'Down Under'),
            ('UK', 'UK'),
            ('Canada', 'Canada')
        ],
        default='US',
        db_index=True,
    )
    tier_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        db_index=True
    )
    score_data = models.JSONField(default=dict)
    total_score = models.IntegerField(default=0, db_index=True)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        replace_map = {
            "'": '',
            'é': 'e',
            '.': '',
            '/': '',
            ' ': '',
            'ó': 'o',
            '-': '',
        }
        self.normalized_name = self.name
        for bad_char, replace_char in replace_map.items():
            self.normalized_name = self.normalized_name.lower().replace(bad_char, replace_char)
        super(Queen, self).save(*args, **kwargs)

    @property
    def formatted_stats(self):
        scores = self.score_set.order_by('episode__drag_race_season', 'episode__number').all()
        formatted_scores = {
            'total': 0,
            'drag_races': {},
            'average': 0
        }
        distinct_episodes = []
        for score in scores:
            season = score.episode.drag_race
            this_season = formatted_scores['drag_races'].get(
                season,
                {
                    'total': 0,
                    'episodes': {}
                }
            )
            this_episode = this_season['episodes'].get(score.episode, {'total': 0, 'scores': []})
            formatted_scores['total'] += score.rule.point_value
            this_season['total'] += score.rule.point_value
            this_episode['total'] += score.rule.point_value
            this_episode['scores'].append(score)

            this_season['episodes'][score.episode] = this_episode

            formatted_scores['drag_races'][season] = this_season
            if score.episode not in distinct_episodes:
                distinct_episodes.append(score.episode)
        if distinct_episodes:
            formatted_scores['average'] = float(float(formatted_scores['total']) / float(len(distinct_episodes)))
        return formatted_scores

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


class DragRaceType(models.Model):
    name = models.CharField(primary_key=True, max_length=25)

    def __str__(self):
        return self.name


class DragRace(models.Model):
    season = models.IntegerField()
    drag_race_type = models.ForeignKey(DragRaceType, null=True, on_delete=models.CASCADE)
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
    premier_date = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=False, db_index=True)
    ''' status
        open: season has not yet started and people can create and join panels
              should remain open for 3 episodes?
        active: season is ongoing, people cannot start new panels
        closed: season is over and people cannot start new panels but can see all stats
    '''
    status = models.CharField(
        max_length=25,
        choices=[
            ('pending', 'pending'),  # drag races that have been created but not yet scored
            ('open', 'open'),  # drag races that are upcoming and open for drafts
            # scores from this drag race should come from active stats models
            ('active', 'active'),  # a currently airing drag race
            ('scoring', 'scoring'),  # an old drag race that admin is currently backfilling with scores
            ('archived', 'archived'),  # a drag race that has been completely scored and closed.
            # scores from this drag race should come from the canonical stats models
        ],
        default='open',
        db_index=True
    )

    class Meta:
        unique_together = ('season', 'drag_race_type', 'franchise')

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        display_name_parts = ['Drag Race', ]
        if self.franchise != 'US':
            display_name_parts.append(self.franchise)
        if self.drag_race_type.name == 'all star':
            display_name_parts.append('All Stars')
        display_name_parts.append('{}'.format(self.season))
        return ' '.join(display_name_parts)

    @property
    def drag_race_type_name(self):
        return self.drag_race_type.name

    @property
    def rules_url(self):
        return reverse('dragrace_rules', kwargs={'drag_race_type': self.drag_race_type_name})

    @property
    def detail_url(self):
        return reverse('dragrace_stats', kwargs={'dragrace_id': self.pk})

    @property
    def edit_url(self):
        return reverse('drag_race_edit', kwargs={'dragrace_id': self.pk})

    @property
    def new_panel_url(self):
        return reverse('panel_create', kwargs={'dragrace_id': self.pk})

    @property
    def public_panels_url(self):
        return reverse('panel_list', kwargs={'dragrace_id': self.pk})

    @property
    def rule_set(self):
        return self.drag_race_type.defaultrule_set.all()

    @property
    def general_draft_allowance(self):
        return math.floor(.4 * self.queens.count())

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

    @property
    def next_episode(self):
        return self.episode_set.filter(has_aired=False).order_by('-number').first()


class Episode(models.Model):
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
    number = models.IntegerField(db_index=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    is_scored = models.BooleanField(default=False)
    has_aired = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ('number', )
        unique_together = ('drag_race', 'number')

    def __str__(self):
        return '{} episode #{}'.format(self.drag_race, self.number)

    @property
    def edit_draft_url(self):
        return reverse('set_episode_draft', kwargs={'episode_id': self.pk})

    @property
    def detail_url(self):
        return reverse('episode_detail', kwargs={'episode_id': self.pk})


class DefaultRule(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    point_value = models.IntegerField(default=1)
    score_type = models.CharField(
        max_length=10,
        choices=(
            ('episode', 'episode'),
            ('season', 'season')
        )
    )
    drag_race_types = models.ManyToManyField(DragRaceType)
    score_class = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        choices=(
            ('elimination', 'elimination'),
            ('lipsync_win', 'lipsync_win'),
            ('stay', 'stay'),
            ('main_win', 'main_win'),
            ('mini_win', 'mini_win'),
            ('safe', 'safe'),
            ('champion', 'champion'),
            ('runnerup', 'runnerup'),
            ('misscongeniality', 'misscongeniality'),
        ),
        db_index=True
    )

    class Meta:
        ordering = ('score_type', 'point_value', 'name')

    @property
    def drag_race_types_list(self):
        return [drt.name for drt in self.drag_race_types.all()]

    def __str__(self):
        return '"{}": ({} points) {}'.format(self.name, self.point_value, self.description)


class Score(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
    default_rule = models.ForeignKey(DefaultRule, null=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-pk', )

    @property
    def rule(self):
        return self.default_rule

    def __str__(self):
        return '{}: {} // {}'.format(self.queen, self.episode, self.rule)


class Participant(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.SET_NULL)
    site_admin = models.BooleanField(default=False)
    episodes = models.ManyToManyField(Episode, blank=True)

    @property
    def name(self):
        return self.user.username

    @property
    def display_name(self):
        return self.user.username

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    def get_formatted_scores_for_panel(self, panel, viewing_participant):
        drafts = Draft.objects.filter(participant=self, panel=panel).all()
        scores = {d.queen: 0 for d in drafts}
        panel_episodes = panel.drag_race.participant_episodes(viewing_participant)

        for episode in panel.drag_race.episode_set.filter(id__in=[e.id for e in panel_episodes]).all():
            _scores = episode.score_set.filter(queen__in=[k for k, v in scores.items()]).all()
            for s in _scores:
                scores[s.queen] += s.rule.point_value
        return scores

    def get_formatted_wildcard_scores_for_panel(self, panel, viewing_participant):
        wq_drafts = WildCardQueen.objects.filter(participant=self, panel=panel).all()
        scores = {d.queen: 0 for d in wq_drafts}
        panel_episodes = panel.drag_race.participant_episodes(viewing_participant)
        wildcard_appearances = WildCardAppearance.objects.filter(
            episode__in=[e for e in panel_episodes],
            queen__in=[wq.queen for wq in wq_drafts]
        ).all()
        for _score in wildcard_appearances:
            scores[_score.queen] += _score.appearance.point_value
        return scores

    def get_all_formatted_scores_for_panel(self, panel, viewing_participant):
        result = {
            'draft_scores': self.get_formatted_scores_for_panel(panel, viewing_participant),
            'wildcard_scores': self.get_formatted_wildcard_scores_for_panel(panel, viewing_participant),
            'total_score': 0,
        }
        total_formal_score = sum([v for d, v in result['draft_scores'].items()])
        total_wq_score = sum([v for d, v in result['wildcard_scores'].items()])
        result['total_score'] = total_formal_score + total_wq_score
        return result

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.user.username = self.display_name.lower()
        self.user.save()
        if not self.pk:
            set_episodes = True
        else:
            set_episodes = False
        super(Participant, self).save(*args, **kwargs)
        if set_episodes:
            # for new participant, reveal all episodes of past seasons and set up stats datas
            for drag_race in DragRace.objects.exclude(status__in=['pending', 'active']).all():
                for episode in drag_race.episode_set.all():
                    self.episodes.add(episode)
                refresh_dragrace_stats_for_participant(self, drag_race)
            self.save(*args, **kwargs)


class EpisodeDraft(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, null=True, on_delete=models.SET_NULL)
    score = models.IntegerField(default=0)
    rank_tier = models.IntegerField(default=0)
    total_participants = models.IntegerField(default=0)
    queens = models.ManyToManyField(Queen)

    class Meta:
        unique_together = ['episode', 'participant']

    def set_total_score(self):
        episode_sum = Score.objects.filter(
            episode=self.episode,
            queen__in=self.queens.all()
        ).aggregate(Sum('default_rule__point_value'))
        if episode_sum['default_rule__point_value__sum']:
            self.score = episode_sum['default_rule__point_value__sum']
        else:
            self.score = 0
        self.save()


class Panel(models.Model):
    code = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=250, unique=True)
    normalized_name = models.CharField(max_length=250, unique=True)
    participants = models.ManyToManyField(Participant)
    captains = models.ManyToManyField(Participant, related_name='panelcaptains')
    drag_race = models.ForeignKey(DragRace, on_delete=models.CASCADE)
    panel_type = models.CharField(
        max_length=25,
        choices=[
            ('private', 'Private'),
            ('public', 'Public')
        ],
        default='private'
    )
    wildcard_allowance = models.IntegerField(
        default=0,
        help_text='The number of wildcard queens each player can draft'
    )
    participant_limit = models.IntegerField(default=1)
    draft_time = models.DateTimeField(blank=True, null=True)
    draft_order = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text='A random order list (0-participants.count) for draft selection. Abstracted from participant IDs.'
    )
    draft_rounds = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text='A dictionary detailing which ordered participants get to select in each draft. Populated by utils.calculate_draft_data.'  # noqa
    )
    participant_drafts = models.JSONField(default=dict, blank=True, null=True)
    current_round = models.IntegerField(default=1)
    current_participant = models.IntegerField(
        default=0,
        help_text='PK of participant whos turn it is right now in the draft'
    )
    total_drafts = models.IntegerField(
        default=0,
        help_text='Total number of draft rounds that there will be in the main draft. Populated by utils.calculate_draft_data.'  # noqa
    )
    status = models.CharField(
        max_length=25,
        choices=[
            ('pending', 'pending'),
            ('open', 'open'),
            ('in draft', 'in draft'),
            ('active', 'active'),
            ('wildcards', 'wildcards'),
            ('closed', 'closed'),
        ],
        default='pending'
    )

    def __str__(self):
        return self.name

    @property
    def display_draft_time(self):
        if self.draft_time:
            return self.draft_time.strftime('%m/%d/%Y %I:%M %p')

    @property
    def detail_url(self):
        return reverse('panel_stats', kwargs={'panel_id': self.pk})

    @property
    def draft_url(self):
        return reverse('panel_set_drafts', kwargs={'panel_id': self.pk})

    @property
    def queen_draft_allowance(self):
        return DRAFT_CAPS.get(self.participants.count())

    @property
    def available_slots(self):
        return self.participant_limit - self.participants.count()

    def get_join_link(self, request):
        return '{}://{}/panel/invite/{}/'.format(request.scheme, request.get_host(), self.code)

    def save(self, *args, **kwargs):
        self.normalized_name = self.name.lower().replace(' ', '')
        super(Panel, self).save(*args, **kwargs)

    def set_draft_rules(self):
        '''Set the following properties in order to automate draft logic:
            draft_rounds: dictionary of which players draft in each round
            total_drafts: total number of draft rounds to do
            participant_drafts: dictionary of which participants draft for each round
        '''
        calculate_draft_data(panel=self)

    def set_random_draft_order(self):
        participants = self.participants.order_by('?').all()
        self.draft_order = []
        for participant in participants:
            self.draft_order.append(participant.pk)

    @property
    def ordered_participants(self):
        participants = []
        for participant_pk in self.draft_order:
            participants.append(self.participants.get(pk=participant_pk))
        return participants

    def start_draft(self):
        self.reset_draft()
        self.set_random_draft_order()
        self.current_participant = self.draft_order[0]
        self.status = 'in draft'
        self.save()

    def reset_draft(self):
        self.participant_drafts = []
        self.draft_order = []
        self.draft_rounds = {}
        self.draft_set.all().delete()
        self.wildcardqueen_set.all().delete()
        self.set_draft_rules()
        self.current_participant = 0
        self.current_round = 1
        self.status = 'open'
        self.save()

    def advance_draft(self):
        def get_participant_order_for_round(draft_index):
            if self.status == 'wildcards':
                current_round = "1"
            else:
                current_round = str(draft_index)
            participant_drafts = self.participant_drafts.get(current_round)
            round_drafts = []
            i = 0
            for p in self.draft_order:
                if i in participant_drafts:
                    round_drafts.append(p)
                i += 1
            return round_drafts

        def check_wq_next_round():
            fully_selected = True
            participant_wq_counts = {p.pk: 0 for p in self.participants.all()}
            wq_drafts = self.wildcardqueen_set.all()
            for wq in wq_drafts:
                participant_wq_counts[wq.participant.pk] += 1
            for p, count in participant_wq_counts.items():
                if count < self.wildcard_allowance:
                    fully_selected = False
            return not fully_selected

        this_round_order = get_participant_order_for_round(self.current_round)
        if self.current_participant == this_round_order[-1]:
            # the last participant who went is the last player for this round
            # so, we need to advance the draft to the next round and the first player
            # in the next round
            if self.status == 'wildcards':
                # if we are in the wildcard draft phase, the order is the same as
                # the first round for every round
                # check if everyone has reached the wildcard allowance yet
                # if not, there is another round
                next_round_index = "1"
                next_round = check_wq_next_round()
            else:
                # find the count index for the next round if there is one
                next_round_index = str(self.current_round + 1)
                next_round = self.draft_rounds.get(next_round_index)
            if next_round:
                # there is another round of drafts to do, so move to the next round
                next_round_order = get_participant_order_for_round(next_round_index)
                self.current_participant = next_round_order[0]
                self.current_round += 1
            else:
                # we reached the last player of the last draft
                # if the panel has a wildcard queen allowance, move the draft
                # to the wildcard phase if it isn't already there
                # else, end the draft
                if self.status == 'in draft' and self.wildcard_allowance > 0:
                    next_round_order = get_participant_order_for_round(1)
                    self.current_participant = next_round_order[0]
                    self.status = 'wildcards'
                else:
                    self.end_draft()
        else:
            # this is somewhere in the middle of a draft round, so just advance
            # to the next participant
            current_index = self.draft_order.index(self.current_participant)
            self.current_participant = self.draft_order[current_index + 1]

        self.save()

    def close_draft(self):
        self.status = 'wildcards'
        self.save()

    def end_draft(self):
        self.status = 'active'
        self.save()

    def save_wildcard_draft(self, participant, queen):
        new_draft = WildCardQueen(
            participant=participant,
            queen=queen,
            panel=self,
        )
        new_draft.save()
        self.save()
        wq_drafts = self.wildcardqueen_set.all()
        drafts = {p: 0 for p in self.participants.all()}
        for draft in wq_drafts:
            drafts[draft.participant] += 1

        fully_selected = True
        for p, count in drafts.items():
            if count < self.wildcard_allowance:
                fully_selected = False
        if fully_selected:
            self.end_draft()

    def save_player_draft(self, participant, queen):
        new_draft = Draft(
            participant=participant,
            queen=queen,
            panel=self,
            round_selected=self.current_round
        )
        new_draft.save()
        self.save()

    @property
    def current_draft_player(self):
        try:
            return self.participants.get(pk=self.current_participant)
        except Participant.DoesNotExist:
            return None

    def get_formatted_scores_for_panelists(self, participant):
        scores = {p: 0 for p in self.participants.all()}
        for _participant in self.participants.all():
            scores[_participant] = _participant.get_all_formatted_scores_for_panel(self, participant)
        return scores


class Draft(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)
    round_selected = models.IntegerField(default=1)

    class Meta:
        unique_together = ('panel', 'participant', 'queen')

    def __str__(self):
        return '{}, {}::{}'.format(self.panel, self.participant, self.queen)


class WildCardQueen(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE)

    def __str__(self):
        return '{}, {}::{}'.format(self.panel, self.participant, self.queen)


class AppearanceType(models.Model):
    name = models.CharField(max_length=50)
    point_value = models.DecimalField(max_digits=2, decimal_places=1)
    description = models.TextField()

    def __str__(self):
        return self.name


class WildCardAppearance(models.Model):
    queen = models.ForeignKey(Queen, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    appearance = models.ForeignKey(AppearanceType, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{} {}'.format(self.queen, self.episode)
