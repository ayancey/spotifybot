import datetime
import logging
import spotbot

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name

    spotify_messages = spotbot.get_channel_messages(***REMOVED***, 1000)

    # Extract the Spotify links from each message, if there is one.
    spotify_track_ids = list(filter(lambda item: item is not None, map(lambda msg: spotbot.extract_spotify_track(msg["content"]), spotify_messages)))

    # Synchronize the last 20 tracks
    spotbot.sync_spotify_playlist("***REMOVED***", spotify_track_ids[:20])

    print("done")

    logger.info("Your cron function " + name + " ran at " + str(current_time))
