from random import shuffle
from tictank_db import get_bots, get_random_bots

# markers for player's tanks
TANK_P1 = 7
TANK_P2 = 8


def get_ai_players(p1_id=None, p2_id=None):
    """ Return two AIBot instances based on their ids
    If the player ids are not provided return random AI players
        :param p1_id: Player 1's id
        :param p2_id: Player 2's id
        :return: Two AIBot instances
    """
    if p1_id is None and p2_id is None:
        p1, p2 = get_random_bots()
    else:
        p1, p2 = get_bots(p1_id, p2_id)

    player1 = AIBot(marker=TANK_P1,
                    opponentmarker=TANK_P2,
                    name=p1[0],
                    iq=p1[1],
                    player_id='P1')
    player2 = AIBot(marker=TANK_P2,
                    opponentmarker=TANK_P1,
                    name=p2[0],
                    iq=p2[1],
                    player_id='P2')
    return player1, player2


class AIBot:
    """ Class for the Computer Player
    """

    def __init__(self, player_id, marker, opponentmarker, name, iq):
        self.player_id = player_id
        self.marker = marker
        self.opponentmarker = opponentmarker
        self.name = name
        self.iq = iq
        self.thinking_depth = self.get_thinking_depth(iq)

    @staticmethod
    def get_thinking_depth(iq):
        """ Return the thinking_depth used in minimax based on
        the AI iq from the database
            :param iq: integer bot iq value
        """
        if iq < 100:
            # No thinking depth, this player moves randomly
            return 0
        elif 100 <= iq < 110:
            # Greedy player, places tank if 4 soldiers available
            return 1
        elif 110 <= iq < 130:
            # Player that can calculate if he can place tank in his turn
            return 2
        elif 130 <= iq < 140:
            # Player that can also see what his opponent will move after his 2 moves
            return 3
        elif 140 <= iq < 170:
            return 4
        elif 170 <= iq < 190:
            return 5
        # The ultimate player with IQ 190 or greater
        return 6

    def move(self, gameinstance):
        """ Perform a troop or tank deployment on the board based on
        the bot iq level
        """

        if self.thinking_depth == 0:
            move_position = self.random_move(gameinstance)
        else:
            move_position = self.minimax(gameinstance, self.thinking_depth)
        gameinstance.move(self.player_id, self.marker, move_position)

    @staticmethod
    def random_move(gameinstance):
        """ Returns a valid random move position on the board
            :param gameinstance: The game instance
        """
        moves = gameinstance.get_available_moves()
        if not moves:
            return
        shuffle(moves)
        return moves[0]

    def minimax(self, gameinstance, depth):
        """ Minimax decision making AI to calculate the best move
        with a maximum depth
            :param gameinstance: The game instance
            :param depth: Maximum number of search in the tree before aborting
            :return The best available move
        """

        moves = gameinstance.get_available_moves()
        if not moves:
            return -1, -1
        # take the worst case initially
        best_current_score = float('-inf')
        self.best_current_move = moves[0]
        for m in moves:
            gameinstance.move(self.player_id, self.marker, m)
            # computer starts
            score = self.min_value(gameinstance, depth - 1)
            gameinstance.revert_last_move()
            if score > best_current_score:
                best_current_score = score
                self.best_current_move = m
        return self.best_current_move

    def min_value(self, gameinstance, depth):
        if depth == 0:
            return self.score(gameinstance)
        moves = gameinstance.get_available_moves()
        # start worst case for minimizing level
        best_current_score = float('inf')
        for m in moves:
            gameinstance.move(self.player_id, self.marker, m)
            score = self.max_value(gameinstance, depth - 1)
            gameinstance.revert_last_move()
            if score < best_current_score:
                best_current_score = score
        return best_current_score

    def max_value(self, gameinstance, depth):
        if depth == 0:
            return self.score(gameinstance)
        moves = gameinstance.get_available_moves()
        best_current_score = float('-inf')
        for m in moves:
            gameinstance.move(self.player_id, self.marker, m)
            score = self.max_value(gameinstance, depth - 1)
            gameinstance.revert_last_move()
            if score > best_current_score:
                best_current_score = score
        return best_current_score

    def score(self, game):
        if game.is_gameover():
            if game.winner == self.marker:
                return 1  # Won

            elif game.winner == self.opponentmarker:
                return -1  # Opponent won
        return 0  # Draw
