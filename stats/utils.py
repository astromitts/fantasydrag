from stats.models import (
    PanelistEpisodeScore,
    PanelistDragRaceScore,
    QueenEpisodeScore,
    QueenDragRaceScore
)


def set_viewing_participant_scores(viewing_participant, drag_race):
    queens = drag_race.queens.all()
    vp = viewing_participant
    panels = vp.panel_set.filter(drag_race=drag_race)
    for panel in panels:
        target_participants = panel.participants.all()
        PanelistEpisodeScore.destroy(
            viewing_participant=vp,
            panel=panel,
        )
        for queen in queens:
            QueenEpisodeScore.destroy(
                queen=queen,
                viewing_participant=vp
            )
            for episode in vp.episodes.filter(drag_race=drag_race).all():
                queen_ep_score = QueenEpisodeScore.get_or_create(
                    queen=queen,
                    episode=episode,
                    viewing_participant=vp
                )
                queen_ep_score.set_total_score()

                for panelist in target_participants:
                    panelist_ep_score = PanelistEpisodeScore.get_or_create(
                        viewing_participant=vp,
                        panel=panel,
                        panelist=panelist,
                        episode=episode
                    )
                    panelist_ep_score.set_total_score()

            queen_dr_score = QueenDragRaceScore.get_or_create(
                queen=queen,
                drag_race=drag_race,
                viewing_participant=vp
            )
            queen_dr_score.set_total_score()

        for panelist in target_participants:
            panelist_dr_score = PanelistDragRaceScore.get_or_create(
                viewing_participant=vp,
                panel=panel,
                panelist=panelist,
                drag_race=drag_race
            )
            panelist_dr_score.set_total_score()
