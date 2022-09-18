import discord
from discord.ext import tasks
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public playlist-modify-private playlist-read-private"))


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


class MyClient(discord.Client):
    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.my_background_task.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(seconds=300)  # task runs every 5 minutes
    async def my_background_task(self):
        ch = self.get_channel(***REMOVED***)

        spotify_messages = []

        # Messages come in out of order, so we need to sort them after the fact
        async for message in ch.history(limit=1000):
            if "spotify.com" in message.content:
                spotify_messages.append(message)

        # Ugly oneliner to get Spotify track IDs from messages, newest to oldest.
        spotify_track_ids = list(filter(lambda item: item is not None, map(lambda msg: extract_spotify_track(msg.content), sorted(spotify_messages, key=lambda m: m.created_at, reverse=True))))

        # Synchronize the last 20 tracks
        sync_spotify_playlist("***REMOVED***", spotify_track_ids[:20])

        print("done")

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(os.environ["DISCORD_BOT_TOKEN"])
