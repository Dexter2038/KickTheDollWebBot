from typing import List


def calculate_hand_value(hand: List[str]) -> int:
    hand_value = sum(parse_card(card) for card in hand)
    hand_value = adjust_for_ace(hand, hand_value)
    return hand_value


def parse_card(card: str) -> int:
    rank = card.split('_')[0]
    if rank == 'a':
        return 11
    elif rank in ['k', 'q', 'j']:
        return 10
    else:
        return int(rank)


def adjust_for_ace(hand: List[str], hand_value: int) -> int:
    aces = [card for card in hand if card.startswith('a')]
    while hand_value > 21 and aces:
        hand_value -= 10
        aces.pop()
    return hand_value


__all__ = ["calculate_hand_value", "parse_card", "adjust_for_ace"]
