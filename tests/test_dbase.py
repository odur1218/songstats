import unittest
from unittest import mock

from songlen import dbase
dbase.DBASE = ":memory:"

SONG0 = ('title1','artistid1', 'artist1', 'album1', 1, 'area1', None, None)
SONG1 = ('title1','artistid1', 'artist1', 'album1', 1, 'area1', 1, 'md5sum1')
SONG2 = ('title2','artistid2', 'artist2', 'album2', 2, 'area2', 2, 'md5sum2')
SONG3 = ('title3','artistid2', 'artist2', 'album3', 3, 'area3', 3, 'md5sum3') #same artist
SONG4 = ('title4','artistid2', 'artist2', 'album4', 4, 'area4', 3, 'md5sum3') #same md5sum

class TestDBase(unittest.TestCase):
    def setUp(self):
        self.db = dbase.DBase()
        dbase._create_tables(self.db)

    def test_create(self):
        tables = self.db.conn.execute("PRAGMA table_info('songs')").fetchall()
        tables = {t[1]:t[2] for t in tables}
        self.assertEqual(tables.get('title'), 'TEXT')
        self.assertEqual(tables.get('artist_id'), 'TEXT')
        self.assertEqual(tables.get('artist'), 'TEXT')
        self.assertEqual(tables.get('album'), 'TEXT')
        self.assertEqual(tables.get('year'), 'INT')
        self.assertEqual(tables.get('area'), 'TEXT')
        self.assertEqual(tables.get('length'), 'INT')
        self.assertEqual(tables.get('md5sum'), 'TEXT')
    
    def test_store_songs(self):
        songs = [SONG1]
        self.db.store_songs(songs)
        self.assertEqual(list(self.db.conn.execute('select * from songs')), songs)

    def test_store_song_length(self):
        songs = [SONG0]
        self.db.store_songs(songs)
        self.assertEqual(list(self.db.conn.execute('select length,md5sum from songs where artist="artist1"')), [(None, None)])
        
        self.db.store_song_length('artistid1','title1',1,'md5')
        self.assertEqual(list(self.db.conn.execute('select length,md5sum from songs')), [(1,'md5')])
        
    def test_artists(self):
        self.assertEqual(self.db.artists(), [])
        songs = [SONG0,SONG1,SONG2,SONG3,SONG4] 
        self.db.store_songs(songs)
        self.assertEqual(self.db.artists(), [{'id':'artistid1', 'name':'artist1'},{'id':'artistid2', 'name':'artist2'}])

    def test_has_artist(self):
        self.assertFalse(self.db.has_artist('artistid1'))
        self.assertFalse(self.db.has_artist('artistid2'))
        self.db.store_songs([SONG1])
        self.assertTrue(self.db.has_artist('artistid1'))
        self.assertFalse(self.db.has_artist('artistid2'))
        self.db.store_songs([SONG2])
        self.assertTrue(self.db.has_artist('artistid2'))

    def test_song_lengths(self):
        self.assertEqual(self.db.song_lengths('artistid1'), [])
        self.db.store_songs([SONG1])
        self.assertEqual(self.db.song_lengths('artistid1'), [1])
        self.db.store_songs([SONG2])
        self.assertEqual(self.db.song_lengths('artistid1'), [1])
        self.assertEqual(self.db.song_lengths('artistid2'), [2])
        self.db.store_songs([SONG3])
        self.assertEqual(self.db.song_lengths('artistid2'), [2,3])
        self.db.store_songs([SONG4])
        self.assertEqual(self.db.song_lengths('artistid2'), [2,3])

    def test_songs(self):
        def _dict(song):
            song = dict(zip(('title','artistid','artist','album','year','area','length','md5sum'), song))
            del song['artistid']
            return song

        DSONG0, DSONG1, DSONG2, DSONG3, DSONG4 = [_dict(s) for s in (SONG0, SONG1, SONG2, SONG3, SONG4)]

        self.assertEqual(self.db.songs(), [])
        self.assertEqual(self.db.songs(['artistid1']), [])
        self.db.store_songs([SONG1])
        self.assertEqual(self.db.songs(), [DSONG1])
        self.assertEqual(self.db.songs(['artistid1']), [DSONG1])
        self.db.store_songs([SONG0,SONG1,SONG2,SONG3,SONG4])
        self.assertEqual(self.db.songs(), [DSONG1,DSONG2,DSONG3,DSONG4])
        self.assertEqual(self.db.songs(['artistid1']), [DSONG1])
        self.assertEqual(self.db.songs(['artistid2']), [DSONG2,DSONG3,DSONG4])


