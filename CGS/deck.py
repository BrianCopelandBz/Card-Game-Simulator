import random
import itertools
from src.card import Card

class Deck(object):
    def __init__(self):
        ''' Create deck definition

        Each card is a name and strength tuple, along with
        the card count.
        '''
        card_counts = [
            (('Guard', 1, True, 'Pick a player to guess their hand'), 5),
            (('Priest', 2, True, 'Pick a player to examine their hand'), 2),
            (('Baron', 3, True, 'Pick a player to compare with'),  2),
            (('Handmaid', 4, False, 'Protection until next turn'), 2),
            (('Prince', 5, True, 'Pick a player to discard their hand'), 2),
            (('King', 6, True, 'Pick a player to trade hands with'), 1),
            (('Countess', 7, False, 'Discard Countess if holding Prince or King'), 1),
            (('Princess', 8, False, 'Lose if discarded'), 1),
        ]
        self.game_deck = []
        for card_type, count in card_counts:
            for card in ([card_type] * count):
                # passing tuple to Card class and appending
                # newly-created card to deck
                self.game_deck.append(Card(*card))
        random.shuffle(self.game_deck)


    def __str__(self):
        result = ""
        for card in self.game_deck:
            result += "\t{0}\n".format(card)
        return result

    def __len__(self):
        return len(self.game_deck)

    def draw_a_card(self):
        if len(self.game_deck) == 0:
            return None
        drawn_card = self.game_deck.pop()
        # print(self.game_deck)
        # print("You drew a {}".format(drawn_card))
        return drawn_card
