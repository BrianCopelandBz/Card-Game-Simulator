# Card-Game-Simulator
Simulate a card game inspired by Alderac Entertainment Group's card game "Love Letter". I (and fellow contributors) are curious if winning strategies are possible, or if equivalent strategies result in a random selection of winner.

# Reference
Most of the rules in v1 of this game are outlined on [AEG's website](https://www.alderacsite.com/wp-content/uploads/2017/11/Love_Letter_Rules_Final.pdf).

To the best of my knowledge, I'm following guidance from [Board Game Geek's thread](https://boardgamegeek.com/thread/493249/mythbusting-game-design-and-copyright-trademarks-a) on fair use.


# Current Status
The end goal of this is to be a server that runs a game that allows clients to connect. As of 2/19, the individual round portion of the game is complete, but not super pythonic - there are some improvements to make to the Round.py stack:

- Turn player into a class (as opposed to the dictionary)
- Turn the log into an object (as opposed to an array of tuples)
- Clean up and make modular each card's actions
- clean up card Objects
  - I hoped to have each card be referenced as a string and print the name, and referenced as an int to print the strength, but that didn't work so well. I should change those to attributes
  - But then, the actions required are attributes of a card, so maybe include them too??

Also to do:

- Implement game using flask_restful
- Have game properly handle authentication (instead of round)
- Create a client that listens and responds to a game
- Test driven development, yo. Lots of tests need to be added. 
