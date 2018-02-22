# game.py

Class Game(object):
    '''A collection of players and a set of rules, then a series of rounds'''

    def __init__(rules, first_player):
        self.rounds = []
        self.players = [first_player]
        self.current_round = 0
        self.rules = rules
        self.isStarted = False

        # Create scoreboard, set scores to zero
        self.scoreboard = {p.name = 0}

    def __repr__():
        '''Return stats about game'''
        pass

    def __len__():
        ''' return players in game '''
        return len(self.players)

    def check_cards():
        pass

    def check_discards():
        pass

    def check_round_log():
        pass

    def check_rules():
        pass

    def check_score():
        pass

    def list_cards():
        pass

    def list_players():
        pass

    def list_rules():
        pass

    def make_decision(**kwargs):
        pass

    def start_game():
        pass

    def quit():
        pass
