# Card.py

class Card(object):
    """ Every card has a name, a strength level, and action indicators

    pick_player is boolean, indicates if playing this card requires
    the game to await a player decision.
    prompt - string message to send to player about decision
    """

    def __init__(self, name, strength, pick_player, prompt):
        self.name = name
        self.strength = strength
        self.pick_player = pick_player
        self.prompt = prompt

    def __str__(self):
        return self.name

    def __int__(self):
        return self.strength

    def __lt__(self, other_card):
        return self.strength < other_card

    def __le__(self, other_card):
        return self.strength <= other_card

    def __gt__(self, other_card):
        return self.strength > other_card

    def __ge__(self, other_card):
        return self.strength >= other_card

    def __eq__(self, other_card):
        return self.name == other_card
