import aiohttp
import asyncio
import logging
import sys

import songlen

logger = logging.getLogger(__name__)

def _unique(songs):
    return set(song['title'] for song in songs)

async def store_song_lengths(disco, db):
    artist = disco['artist']
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        for song in _unique(disco['songs']):
            res = await songlen.get_lyrics(artist['name'], song, session)

            if res is not None:
                db.store_song_length(artist['id'], song, res['length'], res['md5'])
            else:
                logger.warning(f"no lyrics found for: {artist['name']}/{song}")


def _db_rows(disco):
    artist = disco['artist']
    for song in disco['songs']:
        yield (song['title'], 
               artist['id'],
               artist['name'], 
               song['album'],
               song['year'],
               artist['area'],
               None, # length
               None) # md5sum

async def collect(artist):
    disco = await songlen.get_discography(artist)

    with songlen.dbase.DBase() as db:
        db.store_songs(_db_rows(disco))

        await store_song_lengths(disco, db)

async def main():
    from pprint import pprint
    for artist_id in sys.argv[1:]:
        name = songlen.get_artist(artist_id)['name']

        print(f'fetching {name}...', end='', flush=True)

        await collect(artist_id)

        with songlen.dbase.DBase() as db:
            song_lengths = db.song_lengths(artist_id)
            pprint(songlen.song_stats(artist_id))

if __name__=="__main__":
    logging.basicConfig(filename='collect.log')
    asyncio.run(main())
