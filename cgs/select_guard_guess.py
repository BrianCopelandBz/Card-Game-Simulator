# select_guard_guess.py
#
# Part of Round class

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
