from stats.models import (
    PanelistEpisodeScore,
    PanelistDragRaceScore,
    QueenEpisodeScore,
    QueenDragRaceScore
)


def set_viewing_participant_queen_scores(vp, drag_race):
    vp_panels = vp.panel_set.filter(drag_race=drag_race)
    vp_episodes = vp.episodes.filter(drag_race=drag_race).all()
    queens = drag_race.queens.all()

    for queen in queens:
        for episode in vp_episodes:
            vp_queen_episode = QueenEpisodeScore.get_or_create(
                vp, queen, episode
            )
            vp_queen_episode.set_total_score()
        vp_drag_race_score = QueenDragRaceScore.get_or_create(vp, queen, drag_race)
        vp_drag_race_score.set_total_score()
