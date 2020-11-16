import asyncio
import dateutil.parser
import logging 
import musicbrainzngs as mbz
import sys

logger = logging.getLogger(__name__)

mbz.set_useragent('altt', 1.0)

__all__=['search_artist', 'get_artist', 'get_discography']

def search_artist(query):
    r = mbz.search_artists(query, limit=5)

    artists = [{k:artist[k] for k in ('name',
                                      'disambiguation',
                                      'id') if k in artist}
                for artist in r['artist-list']]

    return {'query': query,
            'artists': artists}
    
def get_artist(artist_id):
    try:
        artist = mbz.get_artist_by_id(artist_id)['artist']
    except musicbrainzngs.musicbrainz.ResponseError:
        raise ValueError('invalid artist_id: {artist_id}')

    assert artist_id == artist['id'], f"id mismatch: {artist_id}, {artist['id']}"

    return {'id': artist_id,
            'name': artist['name'],
            'area': artist.get('area',{}).get('name')}

def _year(date):
    if date is not None:
        try:
            return dateutil.parser.parse(date).year
        except TypeError as e:
            logger.warning(f'unable to parse date {date}: {e}')

def _songs(releases):
    for release in releases:
        for medium in release['medium-list']:
            for track in medium['track-list']:
                album = release.get('title')
                title = track['recording']['title'].lower()
                year = _year(release.get('date'))

                if album is not None:
                    album = album.lower()

                yield (album, title, year)

def _unique(songs):
    # remove duplicate (album, title) pairs, keeping minimum year
    years = {}

    for (album, title, year) in songs:
        k = (album, title)
        if years.get(k) is None or years[k] > year:
            years[k] = year

    return [{'album':k[0], 
             'title':k[1], 
             'year':v}  for k,v in years.items()]


async def _releases(artist_id, offset=0):
    return mbz.browse_releases(artist=artist_id, release_type=['album','single'], 
                               includes='recordings', offset=offset, limit=100)

async def _get_songs(artist_id):
    r = await _releases(artist_id)
    songs = set(_songs(r['release-list']))
    aws = [_releases(artist_id, i) for i in range(r['release-count'] // 100 + 1)]
    for coro in asyncio.as_completed(aws):
        r = await coro
        songs.update(_songs(r['release-list']))

    songs = _unique(songs)

    return songs

async def get_discography(artist_id):
    artist = get_artist(artist_id)

    songs = await _get_songs(artist_id)

    return {'artist': artist,
            'songs': songs}

async def main():
    assert len(sys.argv) == 2, "args should be: artist_id"
    from pprint import pprint
    artist_id = sys.argv[1]
    pprint(await get_discography(artist_id))

if __name__=="__main__":
    asyncio.run(main())
