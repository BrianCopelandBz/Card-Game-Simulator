# select_player.py
#
# Part of Round class

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
