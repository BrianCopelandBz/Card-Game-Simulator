# pick_card.py
#
# Part of Round class

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
