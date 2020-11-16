import numpy as np

import songlen

__all__ = ['song_stats']

def _wordcount(lyrics_lengths, n_songs, n_instrumental):
    n_lyrics = len(lyrics_lengths)

    #assumption: proportion of instrumental is equal in failed
    pop_size = n_songs * n_lyrics / (n_instrumental + n_lyrics)

    wordcount = {'min': min(lyrics_lengths),
                 'max': max(lyrics_lengths),
                 'avg': np.mean(lyrics_lengths),
                 'std': np.std(lyrics_lengths)}


    return wordcount

def song_stats(artist_id):
    with songlen.dbase.DBase() as db:
        song_lengths = db.song_lengths(artist_id)

    lyrics_lengths = [l for l in song_lengths if l]

    n_songs = len(song_lengths)
    n_lyrics = len(lyrics_lengths)
    n_instrumental = song_lengths.count(0)
    
    stats = {'nsongs': n_songs,
             'ninstrumental': n_instrumental,
             'nlyrics': n_lyrics}
             
    if n_lyrics > 0:
        stats['wordcount'] = _wordcount(lyrics_lengths, n_songs, n_instrumental)

    return stats
