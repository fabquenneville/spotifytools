#!/usr/bin/env python3
'''
    These are various tools used by spotifycleanup
'''

import configparser
import json
import os
import sqlite3
import sys

def load_arguments():
    '''Get/load command parameters 

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    arguments = {
        "account"   : str(),
        "action"    : False,
        "backup"    : False,
        "resetdb"   : False,
        "test"      : False,
        "in"        : list(),
        "out"       : list(),
        "playlists" : list()
    }
    for arg in sys.argv:
        if "-account:" in arg:
            arguments["account"]    = arg[9:]
        elif "-action:" in arg:
            arguments["action"]     = arg[8:]
        elif "-backup" in arg:
            arguments["backup"]     = True
        elif "-resetdb" in arg:
            arguments["resetdb"]    = True
        elif "-test" in arg:
            arguments["test"]       = True
        elif "-in:" in arg:
            arguments["in"]         += arg[4:].split(",")
        elif "-out:" in arg:
            arguments["out"]        += arg[5:].split(",")
        elif "-playlists:" in arg:
            arguments["playlists"]  += arg[11:].split(",")
    return arguments

def load_config(filepath):
    '''Get/load command parameters 

    Args:

    Returns:
        arguments: A dictionary of lists of the options passed by the user
    '''
    config = configparser.ConfigParser()
    config.read(filepath)
    return config._sections

def create_tables(sqlite):
    cursor = sqlite.cursor()
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            artist TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlists (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlist_songs (
            playlist_id TEXT NOT NULL,
            song_id TEXT NOT NULL,
            PRIMARY KEY(playlist_id, song_id),
            FOREIGN KEY(playlist_id) REFERENCES playlists(id),
            FOREIGN KEY(song_id) REFERENCES songs(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS liked_songs (
            song_id TEXT PRIMARY KEY,
            FOREIGN KEY(song_id) REFERENCES songs(id)
        )
    ''')
    sqlite.commit()

def getdb(path):
    sqlite     = sqlite3.connect(path, detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    sqlite.row_factory = sqlite3.Row
    create_tables(sqlite)
    return sqlite

def save_song(sqlite, song):
    cursor = sqlite.cursor()
    sql = ''' INSERT OR IGNORE INTO songs(id,name,artist)
              VALUES(?,?,?) '''
    cursor.execute(sql, song)
    sqlite.commit()
    return cursor.lastrowid

def save_playlist(sqlite, playlist):
    cursor = sqlite.cursor()
    sql = ''' INSERT OR IGNORE INTO playlists(id,name)
              VALUES(?,?) '''
    cursor.execute(sql, playlist)
    sqlite.commit()
    return cursor.lastrowid

def attach_liked_song(sqlite, data):
    cursor = sqlite.cursor()
    sql = ''' INSERT OR IGNORE INTO liked_songs(song_id)
              VALUES(?) '''
    cursor.execute(sql, data)
    sqlite.commit()
    return cursor.lastrowid

def attach_playlist_song(sqlite, data):
    cursor = sqlite.cursor()
    sql = ''' INSERT OR IGNORE INTO playlist_songs(playlist_id,song_id)
              VALUES(?,?) '''
    cursor.execute(sql, data)
    sqlite.commit()
    return cursor.lastrowid

def json_print(data):
    print(json.dumps(data.json(), sort_keys=True, indent=4))