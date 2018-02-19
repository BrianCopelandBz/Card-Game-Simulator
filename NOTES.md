# Design

## High level description

In Object Oriented Programming, you're supposed to write out a paragraph describing what everything does. This is that:

A server instance is started that waits for players to connect and begin a game when enough players have connected. When one of the players initiates the game, the game is initialized with scores for each player and determining the ruleset (how many cards to discard, how many points each game is playing until).


## Objects

### Server

**Game**

- Connected players (waiting room)
- Game Started
-- ruleset
-- Game win conditions
-- cards to discard per round
-- first player determined by...
- Game log
- Game id


### Client

Attributes:

- Current server
- Current game
-- Provided by server using id
- Current hand
- cards on table
- Current game score
- display
