BEGIN;

-- Create table to store AI Bots information
-- The team can either be 0 (Soviet) or 1(German)
-- AI bot iq must be a positive integer, max 200
CREATE TABLE ai_bots(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    team INT NOT NULL CHECK (team = 0 OR team = 1),
    iq UNSIGNED INT NOT NULL CHECK (iq>=0 AND iq <= 200)
);

-- Create table to store battle results
CREATE TABLE battle_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    winner_name VARCHAR(200) NOT NULL,
    winner_soldiers INT NOT NULL,
    winner_tanks INT NOT NULL,
    winner_pot_moves INT NOT NULL,
    winner_moves INT NOT NULL,
    loser_name VARCHAR(200) NOT NULL,
    loser_soldiers INT NOT NULL,
    loser_tanks INT NOT NULL,
    loser_pot_moves INT NOT NULL,
    loser_moves INT NOT NULL,
    moves INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

END;
