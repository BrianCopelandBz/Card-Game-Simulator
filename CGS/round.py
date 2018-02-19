# Round
#
# Called by: Game
#
# Parameters:
#
# - players: array of a tuples, in format of (name, key),
#            where both name and key are strings
# -- name: string representing the players name
# -- key: string which is the code that a player uses to authenticate
#
# - burn_cards: integer representing how many cards to discard
#               at beginning of round

from src.deck import Deck

class Round(object):
    """Handle the deck and turns of a game

    Init starts the game. Afterwards, the game is driven
    by players using pick_card_to_play, pick_player, and guess.

    Round depends on clients checking the round and
    notifying players when to act via API, handled by game.
    """

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



    def pick_card_to_play(self, secret_key, card):
        ''' Check that the secret key matches the
            current player, then log and process
            Else, 404
            Card should be 0 or 1, 0 for current card, 1 for new card played
        '''
        if self.status != 0:
            abort(404, message="Not waiting on card decision")
        elif self.players[self.current_player]['key'] != secret_key:
            abort(404, message="Not your turn")
        elif card < 0 or card > 1:
            abort(404, message="Not a valid card choice")
        else:

            if card == 0:
                # The player played their current card

                # First, set round variable
                self.current_played_card = self.players[self.current_player]['current_card']

                # Add played card to discarded list for this player
                self.players[self.current_player]['discarded'].append(self.current_played_card)

                # Set players hole card to new card
                self.players[self.current_player]['current_card'] = self.current_new_card

            elif card == 1:
                # the player played the newly drawn card

                # Set round variable
                self.current_played_card = self.current_new_card

                # Add new card to current player's discard list
                self.players[self.current_player]['discarded'].append(self.current_new_card)

            # Clear current_new_card, it's in current player's hand
            self.current_new_card = None

            # log the decision:
            self.log.append(('all', 2, 'Player ' + self.players[self.current_player]['name']
                             + ' played ' + str(self.current_played_card)))

            # Check if player decision is needed:
            if self.current_played_card.pick_player:
                self.log.append((self.players[self.current_player]['key'], 1, self.current_played_card.prompt))
                self.log.append(('all', 1, 'Waiting for ' + self.players[self.current_player]['name'] + ' to pick a player'))
                self.status = 1

            elif self.current_played_card == 'Handmaid':
                # Protect the player:
                self.players[self.current_player]['protected'] = True
                # Log the action
                self.log.append(('all', 4, self.players[self.current_player]['name'] + ' is now protected against card effects.'))
                # Clear current played card, its done
                self.current_played_card = None
                # Play next card
                self.play_next_card()
            elif self.current_played_card == 'Countess':
                ''' It's worth noting that cheating is permitted here.
                This program shall not be doing any checking if this
                is a valid move. Basically, do nothing here.
                '''
                # Clear current played card, its done
                self.current_played_card = None
                # Play next card
                self.play_next_card()
            elif self.current_played_card == 'Princess':
                # Eliminate the player
                self.players[self.current_player]['eliminated'] = True
                self.non_eliminated_players -= 1
                # Log the action
                self.log.append(('all', 3, self.players[self.current_player]['name'] + ' was eliminated for discarding the Princess.'))
                # Since they're eliminated, this player also discards their hand card
                # Log the discarded card for all to see (per love letter rules page 11)
                self.log.append(('all', 7, self.players[self.current_player]['name'] + ' discards ' + str(self.players[self.current_player]['current_card']) + '.'))
                # Move current player's card to discard
                self.players[self.current_player]['discarded'].append(self.players[self.current_player]['current_card'])
                self.players[self.current_player]['current_card'] = None
                # Clear current played card, its done
                self.current_played_card = None
                # Play next card
                self.play_next_card()
            else:
                raise Exception('Card played not expected')




    def select_player(self, secret_key, selected_player):
        ''' Check that the secret key matches the
            current player, check that player is in game,
            then log and process
            Else, 404
            player should be 0 thru len(players),
            players are expected use get_player_list() to get
            proper indices
        '''
        if self.status != 1:
            abort(404, message="Not waiting on player decision")
        elif self.players[self.current_player]['key'] != secret_key:
            abort(404, message="Not your turn")
        elif selected_player < 0 or selected_player > len(self.players):
            abort(404, message="Not a valid player choice")
        elif self.players[selected_player]['eliminated']:
            abort(404, message="Player is eliminated, pick again")
        elif self.players[selected_player]['protected']:
            # Log the Selection and attempt
            self.log.append(('all', 1, self.players[selected_player]['name'] + ' was selected, but they are protected. Pick Again - it may have to be you.'))
        elif self.current_played_card == 'Guard':
            if self.current_player == selected_player:
                self.log.append(('all', 2, self.players[self.current_player]['name']
                                 + ' has picked themselves, which does nothing.'))
                # end guard
                self.current_played_card = None
                self.play_next_card()
            else:
                # Log the guard person pick:
                self.log.append(('all', 7, self.players[self.current_player]['name']
                                     + ' has picked ' + self.players[selected_player]['name']
                                     + ' and now must guess their card. Guard guesses are string name of card.'))
                self.status = 2
                self.guard_person_picked = selected_player
        elif self.current_played_card == 'Priest':
            # Tell the current player about the selected player:
            self.log.append((self.players[self.current_player]['key'], 7, self.players[selected_player]['name']
                                 + ' has a ' + str(self.players[selected_player]['current_card']) + '.'))
            # Log current players pick
            self.log.append(('all', 7, self.players[self.current_player]['name'] + ' viewed '
                + self.players[selected_player]['name'] + '\'s hand.'))
            # End Priest compares, move on
            self.current_played_card = None
            self.play_next_card()
        elif self.current_played_card == 'Baron':
            # Compare players cards
            if self.players[self.current_player]['current_card'] > self.players[selected_player]['current_card']:
                # Eliminate selected player
                self.players[selected_player]['eliminated'] = True
                self.non_eliminated_players -= 1
                # Log the action
                self.log.append(('all', 3, self.players[selected_player]['name']
                                 + ' was eliminated in a Baron comparison for having the lower card.'))
                # Log the discarded card for all to see (per love letter rules page 11)
                self.log.append(('all', 7, self.players[selected_player]['name'] + ' discards '
                                 + str(self.players[selected_player]['current_card']) + '.'))
                # Move the current card to discard for the selected player
                self.players[selected_player]['discarded'].append(self.players[selected_player]['current_card'])
                self.players[selected_player]['current_card'] = None
            elif self.players[self.current_player]['current_card'] < self.players[selected_player]['current_card']:
                # Eliminate the current_player - they made a bad baron decision!
                self.players[self.current_player]['eliminated'] = True
                self.non_eliminated_players -= 1
                # Log the action
                self.log.append(('all', 3, self.players[self.current_player]['name']
                                 + ' was eliminated in a Baron comparison for having the lower card.'))
                # Log the discarded card for all to see (per love letter rules page 11)
                self.log.append(('all', 7, self.players[self.current_player]['name'] + ' discards '
                                 + str(self.players[self.current_player]['current_card']) + '.'))
                # Move the current card to discard for the selected player
                self.players[self.current_player]['discarded'].append(self.players[selected_player]['current_card'])
                self.players[self.current_player]['current_card'] = None
            else:
                # The players matched, nothing happens. Log it!
                self.log.append(('all', 3, self.players[self.current_player]['name']
                                 + ' and ' + self.players[selected_player]['name']
                                 + ' compared hands and tied.'))
                # Tell each player what the opponent had, even if it's the same.
                self.log.append((self.players[self.current_player]['key'], 7, self.players[selected_player]['name']
                                 + ' had a ' + str(self.players[selected_player]['current_card'])
                                 + ' which tied you in the Baron compare.'))
                self.log.append((self.players[selected_player]['key'], 7, self.players[self.current_player]['name']
                                 + ' had a ' + str(self.players[self.current_player]['current_card'])
                                 + ' which tied you in the Baron compare.'))
            # End baron compares, move on
            self.current_played_card = None
            self.play_next_card()
        elif self.current_played_card == 'Prince':
            # Move selected_player's current_card to discard
            self.players[selected_player]['discarded'].append(self.players[selected_player]['current_card'])
            # Log the action publically
            self.log.append(('all', 2, self.players[selected_player]['name'] + ' discarded their hand.'))
            # Check for princess discard:
            if self.players[selected_player]['current_card'] == 'Princess':
                # Eliminate the player
                self.players[selected_player]['eliminated'] = True
                self.non_eliminated_players -= 1
                # Log the action
                self.log.append(('all', 3, self.players[selected_player]['name'] + ' was eliminated for discarding the Princess.'))
                # Move selected_player's card to discard
                self.players[selected_player]['discarded'].append(self.players[selected_player]['current_card'])
                self.players[selected_player]['current_card'] = None
                # Clear current played card, its done
                self.current_played_card = None
                # Play next card
                self.play_next_card()
            else:
                if len(self.deck) > 0:
                    # Draw New Card
                    self.players[selected_player]['current_card'] = self.deck.draw_a_card()
                    # print new cards privately
                    self.log.append((self.players[selected_player]['key'], 7, 'You now have the ' + str(self.players[selected_player]['current_card'])))
                    # Clear current played card, its done
                    self.current_played_card = None
                    # Play next card
                    self.play_next_card()
                else:
                    # No more card left - give them the top burn card:
                    self.players[selected_player]['current_card'] = self.burn_cards.pop()
                    # Warn everyone:
                    self.log.append(('all', 7, self.players[selected_player]['name'] + ' was given the top card from the burn pile, triggering end game.'))
                    # start end game comparison
                    end_game_comparison()
        elif self.current_played_card == 'King':
            # Swap hands - hold current_player's card in temp
            temp_card = self.players[self.current_player]['current_card']
            # Give current player the selected players card
            self.players[self.current_player]['current_card'] = self.players[selected_player]['current_card']
            # give the selected player the temp card
            self.players[selected_player]['current_card'] = temp_card
            # Log the action publically
            self.log.append(('all', 2, self.players[self.current_player]['name'] + ' swapped hands with ' +
                            self.players[selected_player]['name']))
            # print new cards privately
            self.log.append((self.players[self.current_player]['key'], 7, 'You now have the ' + str(self.players[self.current_player]['current_card'])))
            self.log.append((self.players[selected_player]['key'], 7, 'You now have the ' + str(self.players[selected_player]['current_card'])))
            # Clear current played card, its done
            self.current_played_card = None
            # Play next card
            self.play_next_card()


    def select_guard_guess(self, secret_key, selected_card):
        ''' Check that the secret key matches the
            current player, check that player is in game,
            then log and process
            Else, 404
            selected card can either be text string, or power of card guess,
        '''
        proper_str = ['guard', 'priest', 'baron', 'handmaid', 'prince', 'king', 'countess', 'princess']
        if self.status != 2:
            abort(404, message="Not waiting on a Guard guess")
        elif self.players[self.current_player]['key'] != secret_key:
            abort(404, message="Not your turn")
        elif selected_card.lower().strip() not in proper_str:
            abort(404, message="Not a valid card, did you typo?")
        else:
            # perform comparison
            if selected_card.lower().strip() == str(self.players[self.guard_person_picked]['current_card']).lower():
                # Log the Selection and attempt
                self.log.append(('all', 2, self.players[self.current_player]['name'] + ' guessed that '
                                 + self.players[self.guard_person_picked]['name'] + ' had a '
                                 + str(self.players[self.guard_person_picked]['current_card'])
                                 + ' and was right! ' + self.players[self.guard_person_picked]['name']
                                 + ' is now eliminated.'))
                self.players[self.guard_person_picked]['eliminated'] = True
                self.non_eliminated_players -= 1
                # Move selected_player's card to discard
                self.players[self.guard_person_picked]['discarded'].append(self.players[self.guard_person_picked]['current_card'])
                self.players[self.guard_person_picked]['current_card'] = None
                # Clear current played card, its done
                self.current_played_card = None
                # Clear the guard_selected_person, it's done too
                self.guard_person_picked = None
                # Play next card
                self.play_next_card()
            else:
                # Guard guess was wrong
                self.log.append(('all', 2, self.players[self.current_player]['name'] + ' guessed that '
                                 + self.players[self.guard_person_picked]['name'] + ' had a '
                                 + selected_card
                                 + ' and was wrong.'))
                # Clear current played card, its done
                self.current_played_card = None
                # Clear the guard_selected_person, it's done too
                self.guard_person_picked = None
                # Play next card
                self.play_next_card()


    def play_next_card(self):
        ''' Next players turn

        -1) Check for game over
        0) Increment play counter
        1) Change players
        2) check for effects to cancel
        3) Draw a new card
        4) log it
        5) set the status

        '''
        if self.non_eliminated_players < 2:
            self.end_game_comparison()
        elif len(self.deck) == 0:
            self.end_game_comparison()
        else:
            self.plays += 1

            # 1) Change Players
            playerChanged = False
            while not playerChanged:
                self.current_player += 1
                if self.current_player == len(self.players):
                    self.current_player = 0
                if not self.players[self.current_player]['eliminated']:
                    playerChanged = True


            # 2) Check for status change
            if self.players[self.current_player]['protected']:
                # Cancel status
                self.players[self.current_player]['protected'] = False
                # Log status change
                self.log.append(('all', 5, self.players[self.current_player]['name'] + ' is no longer protected against card effects.'))


            # 3) Draw New card
            self.current_new_card = self.deck.draw_a_card()

           # Prompt all players that next player is up
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
