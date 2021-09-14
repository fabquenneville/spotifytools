#!/usr/bin/env python3
'''
    These are various tools related to the last.fm api
'''

import requests

def lastfm_get(config, payload):

    headers = {
        'user-agent': "Dataquest"
    }

    payload["api_key"]  = config["lastfm"]["key"]
    payload["format"]   = 'json'

    response = requests.get('https://ws.audioscrobbler.com/2.0/', headers=headers, params=payload)
    return response

