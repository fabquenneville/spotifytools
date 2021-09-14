#!/usr/bin/env python3
'''
    These are various tools related to the spotify api
'''

def get_user_liked_songs(spotify, limit = 50, cap = 5000, verbose = False):
    results = spotify.current_user_saved_tracks(limit=limit)
    tracks  = results['items']
    if verbose:
        print(len(tracks))
    while results["next"] and len(tracks) < cap:
        results = spotify.next(results)
        tracks.extend(results['items'])
        if verbose:
            print(len(tracks))

    print(f"Found {len(tracks)} liked songs.")
    return tracks

def get_user_playlists(spotify, limit = 50, cap = 250, verbose = False):
    results     = spotify.current_user_playlists(limit=limit)
    playlists   = results['items']
    if verbose:
        print(len(playlists))
    while results["next"] and len(playlists) < cap:
        results = spotify.next(results)
        playlists.extend(results['items'])
        if verbose:
            print(len(playlists))
    origlist = playlists
    playlists = list()
    nb_tracks = 0
    for playlist in origlist:
        pl = spotify.playlist(playlist['id'])
        pl["tracks"]["items"] = get_playlist_tracks(spotify, playlist['id'])
        playlists.append(pl)
        nb_tracks += len(pl["tracks"]["items"])
    print(f"Found {len(playlists)} playlists containing {nb_tracks} tracks.")
    return playlists

def get_playlist_tracks(spotify, id):
    results = spotify.playlist_items(id)
    tracks = results['items']
    while results['next']:
        results = spotify.next(results)
        tracks.extend(results['items'])
    return tracks

def empty_lists(spotify, arguments):
    for playlist in arguments["playlists"]:
        # Getting tracks to remove
        tracks = False
        playlistid = False
        if playlist.lower() in ["liked songs", "liked"]:
            tracks = get_user_liked_songs(spotify)
        else:
            result = spotify.search(q="playlist:" + playlist, type="playlist", limit=1)
            if len(result["playlists"]["items"]) < 1:
                continue
            if result["playlists"]["items"][0]["name"].lower() != playlist.lower():
                continue
            playlistid = result["playlists"]["items"][0]["id"]
            tracks = get_playlist_tracks(spotify, playlistid)
        tracklist = list()
        for track in tracks:
            tracklist.append(track["track"]["id"])
        if len(tracklist) < 1:
            continue
        # Removing tracks
        start = 0
        while start < len(tracklist):
            if playlist.lower() in ["liked songs", "liked"]:
                spotify.current_user_saved_tracks_delete(tracklist[start:start+100])
            else:
                spotify.playlist_remove_all_occurrences_of_items(playlistid, tracklist[start:start+100])
            start += 100
