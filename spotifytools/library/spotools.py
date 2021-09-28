#!/usr/bin/env python3
'''
    These are various tools related to the spotify api
'''

import os
import random
from spotipy.exceptions import SpotifyException

from .tools import attach_liked_song, attach_playlist_song, getdb, save_playlist, save_song

def get_user_liked_songs(spotify, limit = 50):
    results = spotify.current_user_saved_tracks(limit=limit)
    tracks  = results['items']
    while results["next"]:
        results = spotify.next(results)
        tracks.extend(results['items'])

    print(f"Found {len(tracks)} liked songs.")
    return tracks

def get_user_playlists(spotify, username, tracks = False):
    results     = spotify.user_playlists(username)
    playlists   = results['items']
    while results["next"]:
        results = spotify.next(results)
        playlists.extend(results['items'])
    origlist = playlists
    playlists = list()
    nb_tracks = 0
    for playlist in origlist:
        if playlist["owner"]["id"] != username:
            continue
        pl = spotify.playlist(playlist['id'])
        if tracks:
            pl["tracks"]["items"] = get_playlist_tracks(spotify, playlist['id'])
            nb_tracks += len(pl["tracks"]["items"])
        playlists.append(pl)
    if tracks:
        print(f"Found {len(playlists)} playlists containing {nb_tracks} tracks.")
    else:
        print(f"Found {len(playlists)} playlists.")
    return playlists

def get_playlist_tracks(spotify, id):
    results = spotify.playlist_items(id)
    tracks = results['items']
    while results['next']:
        results = spotify.next(results)
        tracks.extend(results['items'])
    return tracks

def empty_list(spotify, username, listname, tracks = False):
    # Getting tracks to remove
    playlistid = False
    if listname.lower() not in ["liked songs", "liked"]:
        playlistid = get_user_playlist_id(spotify, username, listname)

    tracklist = list()
    if not tracks:
        if listname.lower() in ["liked songs", "liked"]:
            tracklist = get_user_liked_songs(spotify)
        else:
            tracklist = get_playlist_tracks(spotify, playlistid)
    else:
        tracklist = tracks
    tracks = list()
    for track in tracklist:
        if isinstance(track, dict):
            tracks.append(track["track"]["id"])

    if len(tracks) < 1:
        return False
    # Removing tracks
    start = 0
    jumps = 100
    if listname.lower() in ["liked songs", "liked"]:
        jumps = 20
    while start < len(tracks):
        if listname.lower() in ["liked songs", "liked"]:
            spotify.current_user_saved_tracks_delete(tracks[start:start+jumps])
        else:
            spotify.playlist_remove_all_occurrences_of_items(playlistid, tracks[start:start+jumps])
        start += jumps

def add_to_list(spotify, username, listname, tracks):
    listid = False
    if listname.lower() not in ["liked songs", "liked"]:
        listid = get_user_playlist_id(spotify, username, listname)
    start = 0
    jumps = 100
    if listname.lower() in ["liked songs", "liked"]:
        jumps = 20

    # Handle raw spotify results > extract id's
    tracklist = tracks
    tracks = list()
    for track in tracklist:
        if isinstance(track, dict):
            tracks.append(track["track"]["id"])
        else:
            tracks.append(track)
    
    while start < len(tracks):
        if listname.lower() in ["liked songs", "liked"]:
            spotify.current_user_saved_tracks_add(tracks[start:start+jumps])
        else:
            spotify.playlist_add_items(listid, tracks[start:start+jumps])
        start += jumps

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
    playlists = get_user_playlists(spotify, config["main"]["account"], True)
    for playlist in playlists:
        save_playlist(sqliteb, (playlist['id'], playlist['name']))
        for track in playlist["tracks"]["items"]:
            if not track['track']:
                continue
            save_song(sqliteb, (track['track']['id'], track['track']['name'], track['track']['artists'][0]['name']))
            attach_playlist_song(sqliteb, (playlist['id'], track['track']['id']))
    

def auto_unlike(spotify, username):
    likedsongs          = get_user_liked_songs(spotify)
    likedsongsids       = list()
    playlists           = get_user_playlists(spotify, username, True)
    playlistsongsids    = list()
    unlikeids           = list()

    for playlist in playlists:
        for track in playlist["tracks"]["items"]:
            if not track['track']:
                continue
            playlistsongsids.append(track['track']['id'])

    for track in likedsongs:
        if track['track']['id'] in playlistsongsids:
            unlikeids.append(track['track']['id'])
    
    # Removing tracks
    start = 0
    jumps = 20
    while start < len(unlikeids):
        spotify.current_user_saved_tracks_delete(unlikeids[start:start+jumps])
        start += jumps
    print(f"Unliked {len(unlikeids)} songs")

def copy_playlists(spotify, username, innames, outnames, delete = False):
    for source in innames:
        tracks = False
        if source.lower() in ["liked songs", "liked"]:
            tracks = get_user_liked_songs(spotify)
        else:
            # result = spotify.search(q="playlist:" + source, type="playlist", limit=1)
            # if len(result["playlists"]["items"]) < 1:
            #     continue
            # if result["playlists"]["items"][0]["name"].lower() != source.lower():
            #     continue
            # tracks = get_playlist_tracks(spotify, result["playlists"]["items"][0]["id"])
            listid = False
            listid = get_user_playlist_id(spotify, username, source)
            if listid:
                tracks = get_playlist_tracks(spotify, listid)
        tracklist = list()
        for track in tracks:
            tracklist.append(track["track"]["id"])
        if len(tracklist) < 1:
            continue
        print(f"Found {len(tracklist)} tracks.")
        for listname in outnames:
            add_to_list(spotify, username, listname, tracklist)
        if delete:
            empty_list(spotify, username, source)

def get_user_playlist_id(spotify, username, listname):
    playlists = get_user_playlists(spotify, username)
    for playlist in playlists:
        if listname.lower() == playlist['name'].lower():
            return playlist['id']
    return False

def shuffle_list(spotify, username, listname):
    listid = False
    tracks = list()
    if listname.lower() not in ["liked songs", "liked"]:
        listid = get_user_playlist_id(spotify, username, listname)
        if listid:
            tracks = get_playlist_tracks(spotify, listid)
    else:
        tracks = get_user_liked_songs(spotify)
    if tracks:
        empty_list(spotify, username, listname, tracks)
        random.shuffle(tracks)
        add_to_list(spotify, username, listname, tracks)
