import aiohttp
import asyncio
import hashlib
import logging
import lxml.etree
import os
import re
import sys
import urllib.parse

logger = logging.getLogger(__name__)

__all__ = ['get_lyrics']

def _length(lyrics):
    words = re.findall('\w+', lyrics, re.I)
    return len(words)

def _md5(lyrics):
    return hashlib.md5(lyrics.encode()).hexdigest()
    
def _pack(artist, song, lyrics, source):
    return {'artist': artist,
            'song': song,
            'lyrics': lyrics,
            'length': _length(lyrics),
            'md5': _md5(lyrics),
            'source': source}
     
def _url(f_url, artist, song):
    return f_url.format(artist=urllib.parse.quote(artist), song=urllib.parse.quote(song))

async def lyrics_ovh(artist, song, session):
    url = _url('https://api.lyrics.ovh/v1/{artist}/{song}', artist, song)
    result = await session.get(url, headers={'Referer':'https://lyrics.ovh'})
    logger.debug(f'lyrics_ovh {artist}/{song}: {result}')

    json = await result.json()

    if json.get('lyrics'):
        return _pack(artist, song, json['lyrics'], 'lyrics_ovh')

async def chartlyrics(artist, song, session):
    url = _url(f'http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?artist={artist}&song={song}', artist, song)
    logger.debug(f'chartlyrics {artist}/{song}')
    result = await session.get(url)
    logger.debug(f'chartlyrics result: {result}')

    tree = lxml.etree.fromstring(await result.read())
    elem = tree.find('.//Lyric', tree.nsmap)

    if elem is not None and elem.text:
        return _pack(artist, song, elem.text, 'chartlyrics')

def _remove_instrumental(lyrics):
    if re.match('.?Instrumental.?', lyrics['lyrics']):
        lyrics.update(length = 0, lyrics='')

async def get_lyrics(artist, song, session):
    aws = [lyrics_ovh(artist, song, session),
           chartlyrics(artist, song, session)]

    for coro in asyncio.as_completed(aws):
        try:
            lyrics = await coro

            if lyrics is not None:
                _remove_instrumental(lyrics)
                return lyrics

        except aiohttp.client_exceptions.ClientError as err:
            logger.warning(f'error getting lyrics for "{artist}" "{song}": {err}')

async def main():
    from pprint import pprint
    assert len(sys.argv) == 3, "args should be: artist song"
    artist, song = sys.argv[1:]
    async with aiohttp.ClientSession() as session:
        pprint(await get_lyrics(artist, song, session))

if __name__=="__main__":
    asyncio.run(main())
