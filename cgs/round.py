# Round.py

from cgs.deck import Deck

class Round(object):
    """Handle the deck and turns of a game

    Init starts the game. Afterwards, the game is driven
    by players using pick_card_to_play, pick_player, and guess.

    Round depends on clients checking the round and
    notifying players when to act via API, handled by game.
    """

    from play_next_card import play_next_card
    from select_player import select_player
    from pick_card import pick_card_to_play
    from select_guard_guess import select_guard_guess


    def __init__(self, game, players, num_cards_to_burn):
        """ Get a deck, prep rules, start game

        Preconditions:

        players: array of a tuples, in format of (name, key),
            where both name and key are strings
        name: string representing the players name
        key: string which is the code that a player uses to
            authenticate
        num_cards_to_burn: integer representing how many cards to discard
            at beginning of round

        Pseudocode:
        0) Define round variables
        1) Create log and start logging
        2) Burn cards
        3) Handle players and distribute hole cards
        4) Draw card for first player

        Postcondition: Game is set, waiting
         on the first players card decision
        """

        # 0) Define round variables
        self.deck = Deck()
        self.burn_cards = []
        self.plays = 1


        '''Players is an array of current players and

        a dictionary of their status
        { 'key':, 'name':, 'current_card':,
          'discarded': [cards in discarded order],
          'protected': bool,
          'eliminated': bool}
        '''
        self.players = []
        self.non_eliminated_players = 0
        self.current_player = 0

        self.current_new_card = None
        self.current_played_card = None

        self.guard_person_picked = None

        ''' Status code for error checking
        0 - Waiting on next player to pick card
        1 - waiting on current player to pick person
        2 - waiting on current player to pick guard guess
        3 - game over
        '''
        self.status = None


        # 1) Create log and start logging
        self.log = [('all', 0,'Initializing')]
        # See Log class definition below for info


        # 2) Burn Cards

        for i in range(num_cards_to_burn):
            self.log.append(('all', 0, 'Burning Card'))
            self.burn_cards.append(self.deck.draw_a_card())


        # 3) Handle players and distribute cards

        # input players is a tuple of (name, key)
        for p in players:
            self.log.append(('all', 0, 'Dealing ' + p[0] + ' a card'))
            self.players.append({'key':p[1],
                'name': p[0],
                'current_card': self.deck.draw_a_card(),
                'discarded': [],
                'protected': False,
                'eliminated': False
                })
            self.log.append((p[1], 0, 'Dealt ' + str(self.players[-1]['current_card'])))
            self.non_eliminated_players += 1 # drives whether a round is still running



        # 4) Draw card for first player

        self.current_new_card = self.deck.draw_a_card()

        # Prompt all players that first player is up
        self.log.append(('all', 0, 'Dealing ' + self.players[self.current_player]['name'] + ' a card'))

        # prompt current player of option via log
        self.log.append((self.players[self.current_player]['key'], 1, 'New card: ' + str(self.current_new_card)))

        # at this point, the log is up, just waiting for client of current player to respond, and hope other players are watching the log for their turn
        self.status = 0



    def end_game_comparison(self):
        ''' End of game, let's see who wins!

        1) Reveal each player's current card
        2) Print the winner
        '''
        # Get non eliminated players:
        remaining_players = [p for p in self.players if not p['eliminated']]
        # Find top remaining player:
        current_winner_strength = 0
        current_winner = None
        current_tied_player = None
        for p in remaining_players:
            self.log.append(('all', 7, p['name'] + ' is still in with a ' + str(p['current_card'])
                             + ', strength ' + str(int(p['current_card']))))
            if int(p['current_card']) > current_winner_strength:
                current_winner = p
                # drop tied player, if exists
                current_tied_player = None
            elif int(p['current_card']) == current_winner_strength:
                # Calculate sum of strength of discarded cards for p:
                p_sum = 0
                for card in p.discarded:
                    p_sum += card
                current_winner_sum = 0
                for card in current_winner.discarded:
                    current_winner_sum += card
                if p_sum > current_winner_sum:
                    self.log.append(('all', 7, p['name'] + ' had ' + p_sum + ' total discarded, '
                                     + current_winner['name'] + ' had ' + current_winner_sum
                                     + ' total discarded, ' + p['name'] + ' wins tie.'))
                    current_winner = p
                elif p_sum < current_winner_sum:
                    self.log.append(('all', 7, p['name'] + ' had ' + p_sum + ' total discarded, '
                                     + current_winner['name'] + ' had ' + current_winner_sum
                                     + ' total discarded, ' + current_winner_sum['name'] + ' wins tie.'))
                else:
                    self.log.append(('all', 7, p['name'] + ' and ' + current_winner['name'] + ' had '
                                     + current_winner_sum + ' total discarded, and are currently tied.'))
                    current_tied_player = p
        # Game over log message
        if current_tied_player == None:
            self.log.append(('all', 6, 'Winner: ' + current_winner['name'] + ' in ' +
                str(self.plays) + ' plays.'))
        else:
            self.log.append(('all', 6, 'Tie: ' + current_winner['name'] + ' and ' + current_tied_player['name']
                             + ' in ' + str(self.plays) + ' plays.'))
        # Print burn cards to log message
        burn_card_list = ''
        for b in self.burn_cards:
            burn_card_list += str(b) + ' '
        if len(self.burn_cards) > 1:
            self.log.append(('all', 6, burn_card_list + 'were burnt.'))
        else:
            self.log.append(('all', 6, burn_card_list + 'was burnt'))
        self.status = 3


    def abort_if_not_authorized(self, secret_key):
        if secret_key not in [d['key'] for d in self.players]:
            abort(404, message="You are not in this game")

    def abort_if_not_current_turn(self, secret_key):
        if secret_key != self.players[self.current_player]['key']:
            abort(404, message="It is not your turn")


    def get_current_card(self, secret_key):
        ''' Look up player by secret key
            if secret key isn't in list, abort
            otherwise, return current card
        '''
        for p in self.players:
            if p['key'] == secret_key:
                return p['current_card']
        # if we didnt find the player, return error
        abort(404, message="You are not in this game")

    def get_new_card(self, secret_key):
        ''' Check that the secret key matches the
            current player. If so, return the
            current new card.
            Else, 404
        '''
        if self.players[self.current_player]['key'] == secret_key:
            return self.current_new_card
        else:
            abort(404, message="Not your turn")



    def get_player_log(self, event_id, secret_key):
        ''' return the game log from event_id onward,
        but only
        '''

    def get_player_list(self):
        player_list = ''
        for i in range(len(self.players)):
            player_list += str(i) + ') ' + self.players[i]['name'] + '\n'
        return player_list

    def get_players_cards(self, player):
        cards_played = 'Starting with their first play: \n'
        for idx, val in enumerate(self.players[player]['discarded']):
            cards_played += str(idx + 1) + ') ' + val + '\n'
        return cards_played
