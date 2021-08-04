# from fantasydrag.models import EpisodeDraft
from stats.models import (
    DragRaceDraftScore,
    EpisodeDraftScore,
    PanelistEpisodeScore,
    PanelistDragRaceScore,
    QueenEpisodeScore,
    QueenDragRaceScore,
)


def set_viewing_participant_scores(viewing_participant, drag_race, debug=False):
    vp = viewing_participant
    if debug:
        print("Setting stats on {} for {}".format(drag_race.display_name, vp.user.username))
    queens = drag_race.queens.all()
    panels = vp.panel_set.filter(drag_race=drag_race)
    PanelistEpisodeScore.destroy(episode__drag_race=drag_race, viewing_participant=vp)
    PanelistDragRaceScore.destroy(drag_race=drag_race, viewing_participant=vp)
    QueenDragRaceScore.destroy(drag_race=drag_race, viewing_participant=vp)
    QueenEpisodeScore.destroy(episode__drag_race=drag_race, viewing_participant=vp)

    vp_episodes = vp.episodes.filter(drag_race=drag_race)

    if debug:
        print("Setting queen episode scores: {} * {}".format(queens, vp_episodes))

    for episode in vp_episodes:
        for queen in queens:
            queen_episode_score = QueenEpisodeScore.create(
                viewing_participant=vp,
                episode=episode,
                queen=queen,
                drag_race=drag_race
            )
            queen_episode_score.set_total_score()

    if debug:
        print("Setting queen drag race scores: {} * {}".format(drag_race.display_name, vp_episodes))

    for queen in queens:
        queen_dr_score = QueenDragRaceScore.create(
            viewing_participant=vp,
            queen=queen,
            drag_race=drag_race
        )
        queen_dr_score.set_total_score()

    for panel in panels:
        panelists = panel.participants.all()
        if debug:
            print("setting scores for {} (vp: {})".format(panel.name, vp.user.username))
        for episode in vp_episodes:
            print("setting episde {} * {}".format(episode, panelists))
            for panelist in panelists:
                panelist_ep_score = PanelistEpisodeScore.create(
                    viewing_participant=vp,
                    panel=panel,
                    panelist=panelist,
                    episode=episode,
                )
                panelist_ep_score.set_total_score()
        for panelist in panelists:
            if debug:
                print(
                    "setting panelist drag race score vp {} for {}".format(vp.user.username, panelist.user.username)
                )
            panelist_dr_score = PanelistDragRaceScore.create(
                viewing_participant=vp,
                panel=panel,
                panelist=panelist,
                drag_race=drag_race
            )
            panelist_dr_score.set_total_score()


def set_episode_draft_scores(episode):
    drafts = episode.episodedraft_set.all()
    scores = []
    for draft in drafts:
        episode_draft_score = EpisodeDraftScore.reset_or_create(
            episodedraft=draft,
            participant=draft.participant
        )
        episode_draft_score.set_total_score()
        scores.append(episode_draft_score.total_score)
    scores.sort(reverse=True)
    if scores:
        current_rank_score = scores[0]
        rank_tier = 1
        rank_tier_count = 1
        EpisodeDraftScore.objects.filter(episodedraft__episode=episode).update(total_participants=len(scores))
        for score in scores:
            if score == current_rank_score:
                pass
            else:
                rank_tier = rank_tier_count

            EpisodeDraftScore.objects.filter(
                episodedraft__episode=episode, total_score=score).update(rank_tier=rank_tier)
            rank_tier_count += 1
            current_rank_score = score


def set_dragrace_draft_scores(drag_race):
    episode_scores = EpisodeDraftScore.objects.filter(episodedraft__episode__drag_race=drag_race).all()
    participant_scores = {}
    for episode_score in episode_scores:
        participant_total_score = participant_scores.get(episode_score.participant, 0)
        participant_scores[episode_score.participant] = participant_total_score + episode_score.total_score
    scores = [v for k, v in participant_scores.items()]
    scores.sort(reverse=True)

    if scores:
        for participant, total_score in participant_scores.items():
            draft_score = DragRaceDraftScore.reset_or_create(
                drag_race=drag_race,
                participant=participant
            )
            draft_score.total_score = total_score
            draft_score.save()

        current_rank_score = scores[0]
        rank_tier = 1
        rank_tier_count = 1
        DragRaceDraftScore.objects.filter(drag_race=drag_race).update(total_participants=len(participant_scores))
        for score in scores:
            if score == current_rank_score:
                pass
            else:
                rank_tier = rank_tier_count

            DragRaceDraftScore.objects.filter(
                drag_race=drag_race, total_score=score).update(rank_tier=rank_tier)
            rank_tier_count += 1
            current_rank_score = score
