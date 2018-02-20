# play_next_card.py
#
# Part of the Round class

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
