import numpy as np

import base64
import enum
import logging
import os
import re
import pandas as pd
import matplotlib.pyplot as plt

import songlen

logger = logging.getLogger(__name__)

__all__ = ['fname', 'create_plot']

class PlotType(enum.Enum):
    HISTO = 'histogram'
    PYEAR = 'peryear'
    PALBUM = 'peralbum'
    PAREA = 'perarea'

def fname(plot_type, b64ids):
    _ = PlotType(plot_type)

    return f'{plot_type}.{b64ids}.png'

def _ids(b64ids):
    ids = base64.urlsafe_b64decode(b64ids).decode().split(',')

    for aid in ids:
        if not re.match('^[\w-]{36}$', aid):
            raise ValueError('invalid artist id: {artist_id}')

    return ids

def _df(b64ids):
    ids = _ids(b64ids)

    with songlen.dbase.DBase() as db:
        df = pd.DataFrame(db.songs(ids))
        
    return df[df.length > 0]

def create_plot(plot_type, b64ids, path):
    ptype = PlotType(plot_type)

    df = _df(b64ids) 
    path = os.path.join(path, fname(plot_type, b64ids))

    fig, ax = plt.subplots(tight_layout=True)

    if ptype is PlotType.HISTO:
        plot_histogram(df, ax)

    elif ptype is PlotType.PYEAR:
        plot_per_year(df, ax)

    elif ptype is PlotType.PALBUM:
        plot_per_album(df, ax)  

    elif ptype is PlotType.PAREA:
        plot_per_area(df, ax)

    logger.debug(f'safe plot to {path}')

    fig.savefig(path)

def plot_histogram(df, ax):
    artists = df.artist.unique()
    lengths = [df.loc[(df.artist == a), 'length'] for a in artists]
    ax.hist(lengths, bins=50, label=artists)
    ax.set_xlabel('avg. number of words in song')
    ax.legend()

def plot_per_album(df, ax):
    df = df.groupby('album').length.mean().reset_index()
    plt.barh(df.album, df.length)
    ax.set_xlabel('avg. number of words in song')

def plot_per_year(df, ax):
    df = df.groupby(['year','md5sum']).first()
    df = df.groupby('year').mean().reset_index()
    ax.bar(df.year, df.length)
    ax.set_ylabel('avg. number of words in song')

def plot_per_area(df, ax):
    df = df.groupby(['area','md5sum']).first()
    df = df.groupby('area').mean().reset_index()
    ax.bar(df.area, df.length)
    ax.set_ylabel('avg. number of words in song')
