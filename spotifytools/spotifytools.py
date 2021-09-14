#!/usr/bin/env python3

import os
import spotipy

# Normal import
try:
    from redbot.library.tools import load_arguments, load_config, create_tables, getdb, save_playlist, save_song, attach_liked_song, attach_playlist_song, run_backup, json_format
    from redbot.library.spotools import get_user_liked_songs, get_playlist_tracks
    from redbot.library.lastfmtools import lastfm_get
# Allow local import for development purposes
except ModuleNotFoundError:
    from library.tools import load_arguments, load_config, create_tables, getdb, save_playlist, save_song, attach_liked_song, attach_playlist_song, run_backup, json_format
    from library.spotools import get_user_liked_songs, get_playlist_tracks
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
        scope           = "user-library-read user-library-modify playlist-read-private playlist-modify-private",
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
        for source in arguments["in"]:
            tracks = False
            if source.lower() in ["liked songs", "liked"]:
                tracks = get_user_liked_songs(spotify)
            else:
                result = spotify.search(q="playlist:" + source, type="playlist", limit=1)
                if len(result["playlists"]["items"]) < 1:
                    continue
                if result["playlists"]["items"][0]["name"].lower() != source.lower():
                    continue
                playlist = spotify.playlist(result["playlists"]["items"][0]["id"])
                tracks = playlist["tracks"]["items"]
            tracklist = list()
            for track in tracks:
                tracklist.append(track["track"]["id"])
            if len(tracklist) < 1:
                continue
            
            for outlist in arguments["out"]:
                if outlist.lower() in ["liked songs", "liked"]:
                    spotify.current_user_saved_tracks_add(tracklist)
                else:
                    result = spotify.search(q="playlist:" + outlist, type="playlist", limit=1)
                    if len(result["playlists"]["items"]) < 1:
                        continue
                    spotify.playlist_add_items(result["playlists"]["items"][0]["id"], tracklist)




    elif arguments["action"] == "test":
        songs = get_user_liked_songs(spotify)
        for song in songs:
            payload = {
                'method'    : 'track.getInfo',
                'track'     : song["track"]["name"],
                'artist'    : song["track"]["artists"][0]["name"]
            }
            lastdata = lastfm_get(config, payload).json()
            print(lastdata["track"]["toptags"])
        #     # print(song)
        #     # album = spotify.album(song["track"]["album"]["id"])
        #     # print(album["genres"])
            # exit()


if __name__ == '__main__':
    main()
