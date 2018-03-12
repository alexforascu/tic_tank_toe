#!/usr/bin/python
import logging
import sqlite3
import sys

from random import shuffle

DATABASE_NAME = "tic_tank.db"
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def create_connection(db_file):
    """ Create a database connection to the SQLite database specified by the ``db_file``
        :param db_file: database file
        :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return None


def create_tables(connection, sql_script):
    """ Creates the ai_bots and battle_log tables using the SQL script from ``sql_script`` param
        :param sql_script: SQL script to create the bots and history tables
    """
    create_tables = open(sql_script, "r").read()
    cursor = connection.cursor()
    try:
        cursor.executescript(create_tables)
    except sqlite3.OperationalError:
        logging.debug("The tables ai_bots and battle_log already exist")


def populate_bots_table(connection, sql_script):
    """ Populate the ai_bots table using the SQL script from ``sql_script`` param
        :param sql_script: SQL script to create the bots and history tables
    """
    populate_ai_bots = open(sql_script, "r").read()
    cursor = connection.cursor()
    try:
        cursor.executescript(populate_ai_bots)
    except sqlite3.OperationalError:
        logging.debug("The table ai_bots is already populated with default values")
        return
    cursor.execute("SELECT * FROM ai_bots")
    rows = cursor.fetchall()
    # Print to see all the AI bots from the table
    for row in rows:
        print(row)


def get_random_bots():
    """ Get two random bot players from the database
    """
    connection = create_connection(DATABASE_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT name, iq FROM ai_bots WHERE team=0")
    data_soviet = cursor.fetchall()
    cursor.execute("SELECT name, iq FROM ai_bots WHERE team=1")
    data_german = cursor.fetchall()
    connection.close()
    # Check if bots exist in the db table for both teams
    if not data_soviet or not data_german:
        logging.debug("Error: No bots found in the database")
        return
    # Randomize lists to get a random AI player
    shuffle(data_soviet)
    shuffle(data_german)
    p1, p2 = data_soviet[0], data_german[0]
    return p1, p2


def get_bots(p1_id, p2_id):
    """ Get two bots from the database
        :param p1_id: player 1 optional id
        :param p2_id: player 2 optional id
    """
    connection = create_connection(DATABASE_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT name, iq FROM ai_bots WHERE id={}".format(p1_id))
    p1 = cursor.fetchone()
    cursor.execute("SELECT name, iq FROM ai_bots WHERE id={}".format(p2_id))
    p2 = cursor.fetchone()
    connection.close()
    return p1, p2


if __name__ == '__main__':
    # Create the database with the tables ai_bots and battle_log and populates ai_bots
    connection = create_connection(DATABASE_NAME)
    create_tables(connection, "data/create_game_tables.sql")
    populate_bots_table(connection, "data/populate_ai_bots.sql")
    connection.close()
