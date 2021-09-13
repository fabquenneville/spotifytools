#!/usr/bin/env python3
'''
    These are various tools used by spotifycleanup
'''

import os
import sys
import configparser
import sqlite3


# Normal import
from library.spotools import get_user_liked_songs, get_user_playlists

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
        "resetdb"   : False
    }

    for arg in sys.argv:
        # Confirm with the user that he selected to delete found files
        if "-account:" in arg:
            arguments["account"] = arg[9:]
        elif "-action:" in arg:
            arguments["action"] = arg[8:]
        elif "-backup" in arg:
            arguments["backup"] = True
        elif "-resetdb" in arg:
            arguments["resetdb"] = True

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

def run_backup(spotify, arguments, config):
    # Setup backup database
    if arguments["resetdb"] and os.path.exists(config["main"]["backuppath"]):
        os.remove(config["main"]["backuppath"])
    sqliteb = getdb(config["main"]["backuppath"])

    # Saving liked songs
    likedsongs = get_user_liked_songs(spotify)
    for track in likedsongs:
        save_song(sqliteb, (track['track']['id'], track['track']['name'], track['track']['artists'][0]['name']))
        attach_liked_song(sqliteb, (track['track']['id'], ))
    # Saving playlists
    playlists = get_user_playlists(spotify)
    for playlist in playlists:
        save_playlist(sqliteb, (playlist['id'], playlist['name']))
        for track in playlist["tracks"]["items"]:
            save_song(sqliteb, (track['track']['id'], track['track']['name'], track['track']['artists'][0]['name']))
            attach_playlist_song(sqliteb, (playlist['id'], track['track']['id']))
