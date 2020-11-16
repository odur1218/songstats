import os
import sqlite3

DBASE = 'db/dbase.sqlite'

def _create_tables(db):
    c = db.conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS songs
                 (title TEXT NOT NULL,
                  artist_id TEXT NOT NULL,
                  artist TEXT NOT NULL,
                  album TEXT,
                  year INT,
                  area TEXT,
                  length INT,
                  md5sum TEXT,
                  UNIQUE(title, artist_id, album) ON CONFLICT IGNORE)''')

    db.conn.commit()

def _mkdirs():
    p = os.path.abspath(DBASE)
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)

def create_tables():
    _mkdirs()
    with DBase() as db:
        _create_tables(db)

class DBase:
    def __init__(self):
        self.conn = sqlite3.connect(DBASE)

    def __del__(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def store_songs(self, songs):
        c = self.conn.cursor()
        c.executemany("INSERT INTO songs VALUES (?,?,?,?,?,?,?,?)", songs)
        self.conn.commit()

    def store_song_length(self, artist_id, song, length, md5sum):
        c = self.conn.cursor()
        c.execute("UPDATE songs SET length=?, md5sum=? WHERE artist_id=? AND title=?", (length, md5sum, artist_id, song))
        self.conn.commit()

    def artists(self):
        c = self.conn.cursor()
        c.execute("SELECT DISTINCT artist, artist_id FROM songs")
        return [dict(zip(('name','id'), r)) for r in c]

    def has_artist(self, artist_id):
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM songs WHERE artist_id=?", (artist_id,))
        return bool(c.fetchone())

    def song_lengths(self, artist_id):
        """drops songs with same lyrics (ie. equal md5sum and lenght>0)
           length=0 means instrumental, length=None no lyrics found"""
        c = self.conn.cursor()

        c.execute('SELECT length FROM Songs WHERE artist_id=? AND length IS NUll OR length==0', (artist_id,))
        lengths = list(c)

        c.execute('SELECT length FROM songs WHERE artist_id=? AND length>0 GROUP BY md5sum', (artist_id,))
        lengths += list(c)

        return [l[0] for l in lengths]

    def songs(self, artist_ids=[]):
        c = self.conn.cursor()
        q = "SELECT artist, title, album, area, year, length, md5sum FROM songs"
        if artist_ids:
            q += " WHERE artist_id in (" +  ','.join(['?'] * len(artist_ids)) + ")"

        c.execute(q, artist_ids)

        return [dict(zip(('artist', 'title', 'album', 'area', 'year', 'length', 'md5sum'), r)) for r in c]
