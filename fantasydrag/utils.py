import math


DRAFT_CAPS = {
    2: 1,
    3: 1,
    4: 2,
    5: 2,
    6: 2,
    7: 2,
    8: 3,
    9: 3,
    10: 4,
    11: 4,
    12: 4,
    13: 4,
    14: 5,
    15: 5,
    16: 5,
    17: 6,
    18: 6,
    19: 6,
    20: 7,
}


def calculate_draft_data(panel=None, participant_count=None, queen_count=None):
    if panel:
        participant_count = panel.participants.count()
        queen_count = panel.drag_race.queens.count()

    queen_draft_allowance = DRAFT_CAPS.get(participant_count)

    total_drafts = queen_draft_allowance * queen_count
    num_drafts = math.floor(
        total_drafts / participant_count
    )
    remaining_drafts = total_drafts % participant_count
    if remaining_drafts:
        num_drafts += 1

    draft_dict = {}
    draft_panel_list = {}
    draft_count = 0
    for draft_index in range(0 + num_drafts):
        draft_round = draft_index + 1
        draft_dict[draft_round] = {}
        draft_panel_list[draft_round] = []
        if draft_round == 2 and remaining_drafts:
            for participant in range(0, participant_count):
                if participant >= (participant_count - remaining_drafts):
                    draft_dict[draft_round][participant] = True
                    draft_count += 1
                    draft_panel_list[draft_round].append(participant)
                else:
                    draft_dict[draft_round][participant] = False
        else:
            for participant in range(0, participant_count):
                draft_dict[draft_round][participant] = True
                draft_panel_list[draft_round].append(participant)
                draft_count += 1

    if panel:
        panel.draft_rounds = draft_dict
        panel.participant_drafts = draft_panel_list
        panel.total_drafts = num_drafts
        panel.save()

    return {
        'queen_draft_allowance': queen_draft_allowance,
        'total_drafts': total_drafts,
        'draft_count': draft_count,
        'draft_dict': draft_dict,
        'participant_drafts': draft_panel_list,
    }
