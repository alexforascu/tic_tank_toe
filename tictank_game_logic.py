from random import getrandbits, randint, shuffle
from tictank_db import create_connection, DATABASE_NAME

# Battle tiles
# DEBRIS_TILE = -1
# EMPTY_TILE = 0
# WAR_TILES (soldiers deployed) = 1, 2, 3, 4
PLAY_TILES = [-1, 0, 1, 2, 3, 4]

# number of player moves per turn
MAX_MOVES = 2


class GAME:
    def __init__(self, starting_board, player1, player2):
        """ Initialize parameters - the board, move history list, players and deployed troops history
        """
        self.board = starting_board
        self.move_history = []
        self.winner = None
        self.p1 = player1
        self.p2 = player2

        self.soldiers_deployed = {self.p1.marker: 0,
                                  self.p2.marker: 0}
        self.tanks_deployed = {self.p1.marker: 0,
                               self.p2.marker: 0}
        self.potential_moves = {self.p1.marker: 0,
                                self.p2.marker: 0}

    def get_available_moves(self):
        """ Returns the list of all available moves
        """

        moves = []
        for i, v in enumerate(self.board):
            if v not in [self.p1.marker, self.p2.marker]:
                moves.append(i)
        return moves

    def move(self, player_id, marker, pos):
        """ Deploys a soldier or a tank
        """

        if self.board[pos] < len(PLAY_TILES)-2:
            # place soldiers
            self.board[pos] += 1
            self.soldiers_deployed[marker] += 1
        else:
            # place tank
            self.board[pos] = marker
            self.tanks_deployed[marker] += 1
        self.potential_moves[marker] += 1
        self.move_history.append((player_id, pos, self.board[pos], marker))
        return marker

    def revert_last_move(self):
        """ Reverts the last move made
        """
        player_id, index, value, marker = self.move_history.pop()
        # downgrade tank to soldier
        if value not in PLAY_TILES:
            self.board[index] = PLAY_TILES[-1:][0]
            self.tanks_deployed[marker] -= 1
        # remove soldier
        else:
            self.board[index] = value - 1
            self.soldiers_deployed[marker] -= 1
        self.winner = None

    def is_gameover(self):
        """ Check if the game is over
        """

        # Tic tac toe winning positions
        win_positions = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6)
        ]

        # check tic-tac-toe winning condition
        for i, j, k in win_positions:
            if (self.board[i] == self.board[j] == self.board[k]
                    and self.board[i] in [self.p1.marker, self.p2.marker]):
                self.winner = self.board[i]
                return True
        # if no tic-tac-toe winner set winner the player with most tanks deployed
        p1_tanks = self.board.count(self.p1.marker)
        p2_tanks = self.board.count(self.p2.marker)
        if p1_tanks + p2_tanks == len(self.board):
            if p1_tanks > p2_tanks:
                self.winner = self.p1.marker
            else:
                self.winner = self.p2.marker
            return True

        return False

    def play(self):
        """Execute the game play with players
        """
        turn_player = 'turn_p1'
        while not self.is_gameover():
            # moves available for each player's turn
            turn_moves = MAX_MOVES

            while turn_moves > 0:
                if turn_player == 'turn_p1':
                    self.p1.move(self)
                else:
                    self.p2.move(self)
                # Do not perform remaining moves if the player already won
                if self.is_gameover():
                    break
                turn_moves -= 1
            # next player turn when current player is out of moves
            turn_player = 'turn_p1' if turn_player == 'turn_p2' else 'turn_p2'

        # GAME OVER
        return self.game_results()

    @staticmethod
    def add_battle_log(winner, loser, moves_count):
        connection = create_connection(DATABASE_NAME)
        cursor = connection.cursor()
        game_data = (winner['name'], winner['soldiers_deployed'], winner['tanks_deployed'],
                     winner['pot_moves'], winner['soldiers_deployed'] + winner['tanks_deployed'],
                     loser['name'], loser['soldiers_deployed'], loser['tanks_deployed'],
                     loser['pot_moves'], loser['soldiers_deployed'] + loser['tanks_deployed'],
                     moves_count)
        game_data_str = ','.join(["'{}'".format(element) for element in game_data])

        sql_script = "INSERT INTO battle_log " \
                     "(winner_name, winner_soldiers, winner_tanks, winner_pot_moves, winner_moves, " \
                     "loser_name, loser_soldiers, loser_tanks, loser_pot_moves, loser_moves, moves)" \
                     "VALUES ({})".format(game_data_str)
        cursor.executescript(sql_script)
        connection.close()

    def game_results(self):
        player_1 = {'name': self.p1.name,
                    'iq': self.p1.iq,
                    'tank': self.p1.marker,
                    'soldiers_deployed': self.soldiers_deployed[self.p1.marker],
                    'tanks_deployed': self.tanks_deployed[self.p1.marker],
                    'pot_moves': self.potential_moves[self.p1.marker]
                    }
        player_2 = {'name': self.p2.name,
                    'iq': self.p2.iq,
                    'tank': self.p2.marker,
                    'soldiers_deployed': self.soldiers_deployed[self.p2.marker],
                    'tanks_deployed': self.tanks_deployed[self.p2.marker],
                    'pot_moves': self.potential_moves[self.p2.marker]
                    }
        moves_count = len(self.move_history)
        moves_list = ''.join(str(e) for e in self.move_history)
        ending_board = '/'.join(str(e) for e in self.board)

        if self.p1.marker == self.winner:
            winner, loser = player_1, player_2
        else:
            winner, loser = player_2, player_1

        # Write battle results in the database
        self.add_battle_log(winner, loser, moves_count)

        return {'player_1': player_1,
                'player_2': player_2,
                'moves_list': moves_list,
                'moves_count': moves_count,
                'ending_board': ending_board,
                'winner': winner['name'],
                }


def get_starting_board(board_id):
    """ Return a starting board
        :param board_id: the board's id
    """
    DEBRIS_TILE, EMPTY_TILE, WAR1, WAR2, WAR3, WAR4 = PLAY_TILES
    boards = {
        1: [EMPTY_TILE] * 9,
        2: [WAR1] * 2 + [WAR2] * 2 + [WAR3] * 1 + [WAR4] * 4,
        3: [EMPTY_TILE] * 5 + [DEBRIS_TILE] * 4,
    }
    board = boards[board_id]
    # Randomize the board tiles order on the board
    shuffle(board)
    return board


def play_game(player1, player2):
    """ Play a game between two AI bot players
        :param player1: AIBot instance
        :param player2: AIBot instance
        :return Returns a dict with the game results

    """
    # select a random starting board
    starting_board = get_starting_board(randint(1, 3))
    data = dict()
    data['starting_board'] = '/'.join(str(e) for e in starting_board)

    # Randomize to have a random starting player
    if bool(getrandbits(1)):
        player1, player2 = player2, player1

    game = GAME(player1=player1,
                player2=player2,
                starting_board=starting_board)
    data.update(game.play())
    return data

