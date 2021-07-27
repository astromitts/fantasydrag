# from fantasydrag.models import EpisodeDraft
from stats.models import (
    PanelistEpisodeScore,
    PanelistDragRaceScore,
    QueenEpisodeScore,
    QueenDragRaceScore
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
