#!/usr/bin/env python3

import os
import spotipy

# Normal import
try:
    from redbot.library.tools import load_arguments, load_config, create_tables, getdb, save_playlist, save_song, attach_liked_song, attach_playlist_song, run_backup
# Allow local import for development purposes
except ModuleNotFoundError:
    from library.tools import load_arguments, load_config, create_tables, getdb, save_playlist, save_song, attach_liked_song, attach_playlist_song, run_backup

def main():
    arguments   = load_arguments()
    config      = load_config("config.ini")
    account     = config["main"]["account"]

    if arguments["account"]:
        account = arguments["account"]

    # Establish API connection
    token = spotipy.util.prompt_for_user_token(
        username        = account,
        scope           = "user-library-read user-library-modify playlist-read-private",
        client_id       = config[account]["id"],
        client_secret   = config[account]["secret"],
        redirect_uri    = config[account]["redirect_uri"]
    )
    spotify = spotipy.Spotify(auth=token)

    # Setup database
    if arguments["resetdb"] and os.path.exists(config["main"]["dbpath"]):
        os.remove(config["main"]["dbpath"])
    sqlite = getdb(config["main"]["dbpath"])

    # Backup spotify lists to backup database
    if arguments["backup"]:
        run_backup(spotify, arguments, config)

if __name__ == '__main__':
    main()
