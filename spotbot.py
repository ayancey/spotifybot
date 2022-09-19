import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import requests
import time


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public playlist-modify-private playlist-read-private"))

discord = requests.session()
discord.headers.update({
    "Authorization": f"Bot {os.environ['DISCORD_BOT_TOKEN']}"
})


def extract_spotify_track(s):
    if "spotify.com/track/" in s:
        return s.split("spotify.com/track/")[-1].split("?")[0]
    if "spotify.com/album/" in s:
        # Return first track from album
        return sp.album_tracks(s.split("spotify.com/album/")[-1].split("?")[0])["items"][0]["id"]


def get_playlist_tracks(pid):
    return list(map(lambda t: t["track"]["href"].split("/")[-1], sp.playlist_items(pid, fields="items(track(href))")["items"]))


def sync_spotify_playlist(playlist_id, new_tracks, limit=20):
    # This ugly function synchronizes the Spotify tracks from Discord with the playlist.
    # We want to keep the date added intact. We don't want tracks to be constantly removed and re-added.

    current_playlist_tracks = get_playlist_tracks(playlist_id)

    print(current_playlist_tracks)

    offset = 0

    for n, tr in enumerate(new_tracks):

        need_to_add = False

        try:
            if current_playlist_tracks[n + offset] != tr:
                need_to_add = True
        except IndexError:
            # Initial run
            need_to_add = True

        if need_to_add:
            sp.playlist_add_items(playlist_id, [tr], position=n)
            offset -= 1
            print("adding")
        else:
            print("not adding")

    # Remove tracks after the n'th one
    new_new_tracks = get_playlist_tracks(playlist_id)

    if len(new_new_tracks) > limit:
        print(f"removing {len(new_new_tracks) - limit} tracks")

        tracks_to_remove = []

        for n, tr in enumerate(new_new_tracks[limit:]):
            tracks_to_remove.append({
                "uri": tr,
                "positions": [n + limit]
            })

        sp.playlist_remove_specific_occurrences_of_items(playlist_id, tracks_to_remove)


def get_channel_messages(channel_id, limit):
    # This is a stupid method and will probably break if there are under <limit> messages in the channel.

    before = None

    messages = []

    while len(messages) < limit:
        params = {
            "limit": 100
        }
        if before:
            params["before"] = before

        r = discord.get(f"https://discord.com/api/channels/{channel_id}/messages", params=params)
        if r.status_code == 429:
            print("rate limited, waiting...")
            time.sleep(2)
        time.sleep(1)

        messages.extend(r.json())

        before = r.json()[-1]["id"]

    return messages


if __name__ == "__main__":
    spotify_messages = get_channel_messages(***REMOVED***, 1000)

    # Extract the Spotify links from each message, if there is one.
    spotify_track_ids = list(filter(lambda item: item is not None, map(lambda msg: extract_spotify_track(msg["content"]), spotify_messages)))

    # Synchronize the last 20 tracks
    sync_spotify_playlist("***REMOVED***", spotify_track_ids[:20])

    print("done")
