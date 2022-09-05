#!/usr/bin/env python3

import os
import spotipy

# Normal import
try:
    from spotifytools.library.tools import load_arguments, load_config, create_tables, getdb, save_playlist, save_song, attach_liked_song, attach_playlist_song, json_print
    from spotifytools.library.spotools import get_user_liked_songs, empty_list, run_backup, get_user_playlists, auto_unlike, shuffle_list, copy_playlists, get_user_playlist_id, get_playlist_tracks
    from spotifytools.library.lastfmtools import lastfm_get
# Allow local import for development purposes
except ModuleNotFoundError:
    from library.tools import load_arguments, load_config, create_tables, getdb, save_playlist, save_song, attach_liked_song, attach_playlist_song, json_print
    from library.spotools import get_user_liked_songs, empty_list, run_backup, get_user_playlists, auto_unlike, shuffle_list, copy_playlists, get_user_playlist_id, get_playlist_tracks
    from library.lastfmtools import lastfm_get

def main():
    arguments   = load_arguments()
    config      = load_config("config.ini")
    account     = config["main"]["account"]

    if arguments["account"]:
        account = arguments["account"]

    # Establish API connection
    token = spotipy.util.prompt_for_user_token(
        username        = account,
        scope           = "user-library-read user-library-modify playlist-read-private playlist-modify-private playlist-modify-public",
        client_id       = config["spotify"]["id"],
        client_secret   = config["spotify"]["secret"],
        redirect_uri    = config["spotify"]["redirect_uri"]
    )
    spotify = spotipy.Spotify(auth=token)

    # Setup database
    if arguments["resetdb"] and os.path.exists(config["main"]["dbpath"]):
        os.remove(config["main"]["dbpath"])
    sqlite = getdb(config["main"]["dbpath"])

    # Backup spotify lists to backup database
    if arguments["backup"]:
        run_backup(spotify, arguments, config)
    if arguments["action"] in ["copy", "transfer"]:
        delete = False
        if arguments["action"] == "transfer":
            delete = True
        copy_playlists(
            spotify = spotify,
            username = config["main"]["account"], 
            innames = arguments["in"],
            outnames = arguments["out"],
            delete = delete)
    elif arguments["action"] == "autounlike":
        auto_unlike(spotify, config["main"]["account"])
    elif arguments["action"] == "empty":
        for listname in arguments["playlists"]:
            empty_list(
                spotify = spotify,
                username = config["main"]["account"],
                listname = listname
            )
    elif arguments["action"] == "shuffle":
        if not arguments["playlists"]:
            playlists = get_user_playlists(spotify, config["main"]["account"])
            ids= [playlist["id"] for playlist in playlists]
            print("Here1")
            shuffle_list(
                spotify = spotify,
                username = config["main"]["account"],
                listname = "liked songs"
            )
            for id in ids:
                print("Here2")
                shuffle_list(
                    spotify = spotify,
                    username = config["main"]["account"],
                    id = id
                )
        for listname in arguments["playlists"]:
            shuffle_list(spotify, config["main"]["account"], listname)

if __name__ == '__main__':
    main()
