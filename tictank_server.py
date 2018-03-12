#!/usr/bin/python
import logging
import sys
import tornado.web
import tictank_game_logic

from tornado.options import define, options

from tictank_ai_logic import get_ai_players
from tictank_db import create_connection, DATABASE_NAME

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
define("port", default=8888, type=int)


class RandomGameHandler(tornado.web.RequestHandler):
    def get(self):
        """ Get the game result between 2 random AI player bots
        """
        player1, player2 = get_ai_players()
        game_results = tictank_game_logic.play_game(player1, player2)
        logging.debug("Random game played between bots: {} and {}".format(player1.name, player2.name))
        self.write(game_results)


class GameHandler(tornado.web.RequestHandler):
    def get_params(self):
        """ Get the p1_id and p2_id user input params and check if they're valid ids
            :return: List of valid player ids
        """
        p1 = self.get_arguments("p1_id")
        p2 = self.get_arguments("p2_id")
        try:
            p1_id = int(p1[0])
            p2_id = int(p2[0])
        # Not both player id params have been provided
        except IndexError:
            self.write("Error: Missing Parameters")
            return
        # Not both player id params are numbers
        except ValueError:
            self.write("Error: Invalid Parameter Types")
            return
        connection = create_connection(DATABASE_NAME)
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT team FROM ai_bots WHERE id={}".format(p1_id))
            p1_team = cursor.fetchone()
            cursor.execute("SELECT team FROM ai_bots WHERE id={}".format(p2_id))
            p2_team = cursor.fetchone()
        # Provided player ids not in the database
        except TypeError:
            self.write("Error: No bots in database for provided Parameters")
            return
        finally:
            # close the db connection
            connection.close()
        if p1_team == p2_team:
            self.write("Error: Provided player ids are in the same team")
            return
        return [p1_id, p2_id]

    def get(self):
        """ Get the game result between the 2 selected AI player bots
        """
        params = self.get_params()
        if params is None:
            return
        player1, player2 = get_ai_players(p1_id=params[0],
                                          p2_id=params[1])
        game_results = tictank_game_logic.play_game(player1, player2)
        logging.debug("Custom game played between bots: {} and {}".format(player1.name, player2.name))
        self.write(game_results)


class BotsHandler(tornado.web.RequestHandler):
    def get(self):
        """ Get the bots defined in the ai_bots database
        """
        connection = create_connection(DATABASE_NAME)
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, team, iq FROM ai_bots")
        bots = cursor.fetchall()
        bot_dict = {'soviet_ai': {},
                    'german_ai': {}}
        for id, name, team, iq in bots:
            bot_data = {'name': name, 'iq': iq}
            if team == 0:
                bot_dict['soviet_ai'][id] = bot_data
            else:
                bot_dict['german_ai'][id] = bot_data
        logging.debug("Bot information requested")
        self.write(bot_dict)


class CheckHandler(tornado.web.RequestHandler):
    def get(self):
        """ Get a confirmation message for connecting to the server
        """
        logging.debug("Client connected to the server")
        self.write({"connected": True})


game_server = tornado.web.Application([
    (r"/play_random", RandomGameHandler),
    (r"/play_game", GameHandler),
    (r"/get_bots", BotsHandler),
    (r"/", CheckHandler),
])


def print_server_start():
    """ Prints the server start info, just getting these prints out of
    the way of more relevant stuff :)
    """
    print 60 * "-"
    print("Tic Tank Toe server running...\n")
    print(" !      /-----\============@  -  -  -  -  -  >")
    print(" |_____/_______\_____")
    print("/____________________\\")
    print(" \+__+__+__+__+__+__*/")
    print("\nDeveloped by Alexandru Forascu (alexforascu@gmail.com)")
    print("Press CTRL+C to close")
    print 60 * "-"


if __name__ == '__main__':
    # Start the game server
    logging.debug("Server started")
    print_server_start()
    game_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
