import datetime
import logging
import spotbot

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run(event, context):
    import os

    if not os.path.exists(".cache"):
        print("writing cache file")
        with open(".cache", "w") as f:
            f.write("""{"access_token": "***REMOVED***", "token_type": "Bearer", "expires_in": 3600, "scope": "playlist-modify-public playlist-modify-private playlist-read-private", "expires_at": 1665083306, "refresh_token": "***REMOVED***vzLSNnv8us"}""")

    current_time = datetime.datetime.now().time()
    name = context.function_name

    spotify_messages = spotbot.get_channel_messages(***REMOVED***, 1000)

    # Extract the Spotify links from each message, if there is one.
    spotify_track_ids = list(filter(lambda item: item is not None, map(lambda msg: spotbot.extract_spotify_track(msg["content"]), spotify_messages)))

    # Synchronize the last 20 tracks
    spotbot.sync_spotify_playlist("***REMOVED***", spotify_track_ids[:20])

    print("done")

    logger.info("Your cron function " + name + " ran at " + str(current_time))
