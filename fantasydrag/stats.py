from django.db import models
from fantasydrag.models import (
    Participant,
    DragRace,
    Panel,
    Queen,
    Score,
    EpisodeDraft,
    WildCardQueen,
    WildCardAppearance
)


class Stats(models.Model):
    participant = models.ForeignKey(Participant, null=True, on_delete=models.CASCADE)
    drag_race = models.ForeignKey(DragRace, null=True, on_delete=models.CASCADE)
    panel = models.ForeignKey(Panel, null=True, on_delete=models.CASCADE)
    queen = models.ForeignKey(Queen, null=True, on_delete=models.CASCADE)
    primary_stat = models.DecimalField(
        default=0,
        max_digits=8,
        decimal_places=2,
        db_index=True
    )
    stat_type = models.CharField(
        max_length=100,
        choices=(
            # Scored queens for each episodedraft, for viewed episodes:
            ('cummulative_dragrace_drafts', 'cummulative_dragrace_drafts'),
            # Overall rank in draft for episodedrafts
            ('dragrace_rank', 'dragrace_rank'),
            # All scores for drag race for viewed episodes
            ('dragrace_panel_scores', 'dragrace_panel_scores'),
            # All panel scores for queens for viewed episodes
            ('participant_queen_scores', 'participant_queen_scores'),
            # All panel scores for queens for viewed episodes
            ('participant_wildqueen_scores', 'participant_wildqueen_scores'),
            # All scores for queen in drag race
            ('dragrace_queen_scores', 'dragrace_queen_scores'),
            # Master score stats for queen
            ('queen_scores', 'queen_scores'),
        ),
        db_index=True
    )
    data = models.JSONField(default=dict)

    def __str__(self):
        if self.participant and self.drag_race:
            return '{}: {} // {}'.format(self.stat_type, self.drag_race.display_name, self.participant.display_name)
        elif self.drag_race:
            return '{}: {} // {}'.format(self.stat_type, self.drag_race.display_name, self.queen.name)
        elif self.participant and self.queen:
            return '{}: {} // {}'.format(self.stat_type, self.queen.name, self.participant.name)
        else:
            return '{}: {}'.format(self.stat_type, self.queen.name)

    @classmethod
    def set_participant_queen_scores(cls, viewing_participant, drag_race=None, panel=None):
        if panel:
            drag_race = panel.drag_race

        participant_episodes = viewing_participant.episodes.filter(drag_race=drag_race).all()
        drag_race_queens = drag_race.queens.all()
        for queen in drag_race_queens:
            scores = Score.objects.filter(
                queen=queen,
                episode__in=participant_episodes
            ).all()

            if panel:
                stat_instance = cls.objects.filter(
                    participant=viewing_participant,
                    drag_race=panel.drag_race,
                    panel=panel,
                    queen=queen,
                    stat_type='participant_queen_scores',
                ).first()
                if not stat_instance:
                    stat_instance = cls(
                        participant=viewing_participant,
                        drag_race=panel.drag_race,
                        panel=panel,
                        queen=queen,
                        stat_type='participant_queen_scores',
                    )
            else:
                stat_instance = cls.objects.filter(
                    participant=viewing_participant,
                    drag_race=drag_race,
                    queen=queen,
                    panel=None,
                    stat_type='participant_queen_scores',
                ).first()
                if not stat_instance:
                    stat_instance = cls(
                        participant=viewing_participant,
                        drag_race=drag_race,
                        queen=queen,
                        panel=None,
                        stat_type='participant_queen_scores',
                    )

            stat_instance.primary_stat = 0
            stat_instance.save()
            stat_instance.primary_stat = 0
            if panel:
                queen_data = {
                    'episodes': {},
                    'drafts': [d.participant.name for d in queen.draft_set.filter(panel=panel)]
                }
            else:
                queen_data = {
                    'episodes': {}
                }

            for episode in participant_episodes:
                queen_data['episodes'][episode.pk] = {
                    'pk': episode.pk,
                    'number': episode.number,
                    'title': episode.title,
                    'total': 0,
                    'scores': []
                }

            for score in scores:
                stat_instance.primary_stat += score.rule.point_value
                queen_data['episodes'][score.episode.pk]['total'] += score.rule.point_value
                queen_data['episodes'][score.episode.pk]['scores'].append(
                    {
                        'rule': score.rule.name,
                        'value': score.rule.point_value
                    }
                )
            stat_instance.data = queen_data
            stat_instance.save()

    @classmethod
    def set_participant_wildqueen_scores(cls, viewing_participant, drag_race=None, panel=None):
        if panel:
            drag_race = panel.drag_race

        participant_episodes = viewing_participant.episodes.filter(drag_race=drag_race).all()
        drag_race_wildqueens = WildCardQueen.objects.filter(panel__drag_race=drag_race).all()
        for wq_queen in drag_race_wildqueens:
            appearances = WildCardAppearance.objects.filter(
                queen=wq_queen.queen,
                episode__in=participant_episodes
            ).all()

            if panel:
                stat_instance = cls.objects.filter(
                    participant=viewing_participant,
                    drag_race=panel.drag_race,
                    panel=panel,
                    queen=wq_queen.queen,
                    stat_type='participant_wildqueen_scores',
                ).first()
                if not stat_instance:
                    stat_instance = cls(
                        participant=viewing_participant,
                        drag_race=panel.drag_race,
                        panel=panel,
                        queen=wq_queen.queen,
                        stat_type='participant_wildqueen_scores',
                    )
            else:
                stat_instance = cls.objects.filter(
                    participant=viewing_participant,
                    drag_race=drag_race,
                    queen=wq_queen.queen,
                    panel=None,
                    stat_type='participant_wildqueen_scores',
                ).first()
                if not stat_instance:
                    stat_instance = cls(
                        participant=viewing_participant,
                        drag_race=drag_race,
                        queen=wq_queen.queen,
                        panel=None,
                        stat_type='participant_wildqueen_scores',
                    )

            stat_instance.primary_stat = 0
            stat_instance.save()
            stat_instance.primary_stat = 0
            if panel:
                queen_data = {
                    'episodes': {},
                    'draft': wq_queen.participant.name
                }
            else:
                queen_data = {
                    'episodes': {}
                }

            for episode in participant_episodes:
                queen_data['episodes'][episode.pk] = {
                    'pk': episode.pk,
                    'number': episode.number,
                    'title': episode.title,
                    'total': 0,
                    'scores': []
                }

            for appearance in appearances:
                stat_instance.primary_stat += appearance.appearance.point_value
                queen_data['episodes'][appearance.episode.pk]['total'] += float(appearance.appearance.point_value)
                queen_data['episodes'][appearance.episode.pk]['scores'].append(
                    {
                        'rule': appearance.appearance.name,
                        'value': float(appearance.appearance.point_value)
                    }
                )
            stat_instance.data = queen_data
            stat_instance.save()

    @classmethod
    def set_dragrace_panel_scores(cls, viewing_participant, panel):
        stat_instance = cls.objects.filter(
            participant=viewing_participant,
            drag_race=panel.drag_race,
            panel=panel,
            stat_type='dragrace_panel_scores',
        ).first()
        if not stat_instance:
            stat_instance = cls(
                participant=viewing_participant,
                drag_race=panel.drag_race,
                panel=panel,
                stat_type='dragrace_panel_scores',
            )
        stat_instance.primary_stat = 0
        stat_instance.save()
        data = []
        for participant in panel.participants.all():
            scores = participant.get_all_formatted_scores_for_panel(panel, viewing_participant)
            json_scores = {'total_score': str(scores['total_score'])}
            json_scores['draft_scores'] = [
                {
                    'pk': queen.pk,
                    'name': queen.name,
                    'score': str(points)
                } for queen, points in scores['draft_scores'].items()
            ]

            json_scores['wq_scores'] = [
                {
                    'pk': queen.pk,
                    'name': queen.name,
                    'score': str(points)
                } for queen, points in scores['wildcard_scores'].items()
            ]
            data.append(
                {
                    'participant': {'pk': participant.pk, 'name': participant.display_name},
                    'score': json_scores
                }
            )
        stat_instance.data = data
        stat_instance.save()

    @classmethod
    def set_dragrace_participant_ranks(cls, drag_race, participant):
        dragrace_drafts = EpisodeDraft.objects.filter(episode__drag_race=drag_race).all()
        unique_participants = []
        for draft in dragrace_drafts:
            if draft.participant not in unique_participants:
                unique_participants.append(draft.participant)
        for participant in unique_participants:
            stat_instance = cls.objects.filter(
                participant=participant,
                drag_race=drag_race,
                stat_type='dragrace_rank',
            ).first()
            if not stat_instance:
                stat_instance = cls(
                    participant=participant,
                    drag_race=drag_race,
                    stat_type='dragrace_rank',
                )
            stat_instance.primary_stat = 0
            stat_instance.save()

            rank_data = {
                'total_players': len(unique_participants),
                'participant_total': 0,
                'scores': [],
                'ranks': {},
            }
            participant_scores = {uparticipant: 0 for uparticipant in unique_participants}
            for draft in dragrace_drafts:
                episode_total = draft.total_score
                participant_scores[draft.participant] += episode_total
                if draft.participant == participant:
                    rank_data['participant_total'] += episode_total
            for scored_participant, score in participant_scores.items():
                rank_data['scores'].append(score)
            rank_data['scores'].sort(reverse=True)
            score_set = set(rank_data['scores'])

            placement = 1
            for unique_score in sorted(score_set, reverse=True):
                rank_data['ranks'][unique_score] = {'count': 0, 'place': placement}
                placement += 1

            for score in rank_data['scores']:
                rank_data['ranks'][score]['count'] += 1

            stat_instance.data = rank_data
            stat_instance.primary_stat = rank_data['ranks'][rank_data['participant_total']]['place']
            stat_instance.save()

    @classmethod
    def set_dragrace_draft_scores(cls, participant, drag_race):
        stat_instance = cls.objects.filter(
            participant=participant,
            drag_race=drag_race,
            stat_type='cummulative_dragrace_drafts',
        ).first()
        if not stat_instance:
            stat_instance = cls(
                participant=participant,
                drag_race=drag_race,
                stat_type='cummulative_dragrace_drafts',
            )
        stat_instance.save()

        viewed_episodes = drag_race.participant_episodes(participant)
        stat_instance.primary_stat = 0
        dragrace_draft_data = {
            'episodes': {episode.number: {} for episode in viewed_episodes}
        }
        for episode in viewed_episodes:
            episode_draft = EpisodeDraft.objects.filter(participant=participant, episode=episode).first()

            if episode_draft:
                episode_draft_data = {
                    'total': 0,
                    'queens': {queen.name: 0 for queen in episode_draft.queens.all()}
                }

                for queen in episode_draft.queens.all():
                    scores = Score.objects.filter(
                        queen=queen,
                        episode=episode,
                    )
                    for score in scores:
                        episode_draft_data['total'] += score.rule.point_value
                        episode_draft_data['queens'][queen.name] += score.rule.point_value
                        stat_instance.primary_stat += score.rule.point_value
                dragrace_draft_data['episodes'][episode.number] = episode_draft_data

        stat_instance.data = dragrace_draft_data
        stat_instance.save()

    @classmethod
    def set_queen_master_stats(cls, queen, viewing_participant):
        stat_instance = cls.objects.filter(
            queen=queen,
            participant=viewing_participant,
            stat_type='queen_scores',
        ).first()
        if not stat_instance:
            stat_instance = cls(
                queen=queen,
                participant=viewing_participant,
                stat_type='queen_scores',
            )
        stat_instance.save()

        participant_episodes = viewing_participant.episodes.all()
        scores = queen.score_set.filter(
            episode__in=participant_episodes,
            episode__is_scored=True
        ).order_by('episode__drag_race__season', 'episode__number').all()

        unique_drag_races = set([s.episode.drag_race for s in scores])

        formatted_scores = {
            'total': 0,
            'drag_races': {},
        }
        for drag_race in unique_drag_races:
            formatted_scores['drag_races'][drag_race.pk] = {
                'display_name': drag_race.display_name,
                'pk': drag_race.pk,
                'total': 0,
                'episodes': {}
            }
            for episode in drag_race.episode_set.filter(is_scored=True).all():
                formatted_scores['drag_races'][episode.drag_race.pk]['episodes'][episode.pk] = {
                    'pk': episode.pk,
                    'title': episode.title,
                    'number': episode.number,
                    'total': 0,
                    'scores': [],
                }

        unique_episodes = set([s.episode for s in scores])

        for score in scores:
            formatted_scores['total'] += score.rule.point_value
            drpk = score.episode.drag_race.pk
            epk = score.episode.pk
            formatted_scores['drag_races'][drpk]['episodes'][epk]['scores'].append(
                {'rule': score.rule.name, 'value': score.rule.point_value})
            formatted_scores['drag_races'][drpk]['total'] += score.rule.point_value
            formatted_scores['drag_races'][drpk]['episodes'][epk]['total'] += score.rule.point_value
        if len(unique_episodes) > 0:
            stat_instance.primary_stat = float(float(formatted_scores['total']) / float(len(unique_episodes)))
        stat_instance.data = formatted_scores
        stat_instance.save()

    @classmethod
    def set_dragrace_queen_stats(cls, drag_race):
        queens = drag_race.queens.all()
        for queen in queens:

            stat_instance = cls.objects.filter(
                queen=queen,
                drag_race=drag_race,
                stat_type='dragrace_queen_scores',
            ).first()
            if not stat_instance:
                stat_instance = cls(
                    queen=queen,
                    drag_race=drag_race,
                    stat_type='dragrace_queen_scores',
                )
            stat_instance.save()

            scores = queen.score_set.filter(episode__drag_race=drag_race).order_by('episode__number').all()
            unique_episodes = set([s.episode for s in scores])
            formatted_scores = {
                'total': 0,
                'episodes': {},
            }
            for episode in unique_episodes:
                formatted_scores['episodes'][episode.pk] = {
                    'pk': episode.pk,
                    'title': episode.title,
                    'number': episode.number,
                    'total': 0,
                    'scores': [],
                }
            for score in scores:
                formatted_scores['total'] += score.rule.point_value
                formatted_scores['episodes'][score.episode.pk]['scores'].append(
                    {'rule': score.rule.name, 'value': score.rule.point_value})
                formatted_scores['episodes'][score.episode.pk]['total'] += score.rule.point_value
                formatted_scores['total'] += score.rule.point_value
            if len(unique_episodes) > 0:
                stat_instance.primary_stat = float(float(formatted_scores['total']) / float(len(unique_episodes)))
            stat_instance.data = formatted_scores
            stat_instance.save()
