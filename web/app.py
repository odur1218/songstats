from flask import Flask, abort, jsonify

import base64
import enum
import os
import re
import subprocess 

import songlen

songlen.dbase.create_tables()

app = Flask(__name__, static_folder='static')
app.secret_key = '9evUvNQ2YeyfH25MxolNcA'

class Status(enum.Enum):
    NOT_STARTED = 'not started'
    PENDING = 'pending'
    FINISHED = 'finished'
    FAILED = 'failed'

processes = {}

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/api/search/<string:query>', methods=['GET'])
def suggests(query, rettype='json'):

    try:
        r = songlen.search_artist(query)
        return jsonify(r)

    except Exception as e:
        app.logger.error(f'query "{query}" failed: {e}')
        abort(500)

def _start_process(artist_id):
    if not re.match('^[\w-]{36}$', artist_id):
        raise ValueError('invalid artist id: {artist_id}')

    proc = subprocess.Popen(['python','collect.py', artist_id], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    processes[artist_id] = proc

def _proc_status(artist_id):
    if not artist_id in processes:
        return Status.NOT_STARTED

    rc = processes[artist_id].poll()
    if rc is None:
        return Status.PENDING

    return Status.FINISHED if rc == 0 else Status.FAILED

@app.route('/api/stats/<string:artist_id>', methods=['GET'])
def stats(artist_id, rettype='json'):
    try:
        ret = {'artist': songlen.get_artist(artist_id)}

        with songlen.dbase.DBase() as db:
            in_db = db.has_artist(artist_id)

        proc_status = _proc_status(artist_id)

        if not in_db and proc_status is Status.NOT_STARTED:
            _start_process(artist_id)
            ret['pending'] = True

        else:
            if in_db:
                ret['stats'] = songlen.song_stats(artist_id)

            if proc_status is Status.PENDING:
                ret['pending'] = True
            else:
                ret['pending'] = False
                _ = processes.pop(artist_id, None)

        return jsonify(ret)

    except ValueError:
        return 'invalid artist_id', 400

    except Exception as e:
        app.logger.error(f'stats failed for "{artist_id}": {e}')
        abort(500)
    
@app.route('/api/plot/<string:plot_type>/<string:b64ids>', methods=['GET'])
def plot(plot_type, b64ids, rettype='json'):
    try:
        fname = songlen.plot.fname(plot_type, b64ids)
    
        if not os.path.exists(os.path.join(app.static_folder, fname)):
            songlen.create_plot(plot_type, b64ids, app.static_folder)

        return jsonify({'img': f'/static/{fname}'})

    except ValueError as e:
        return str(e), 400

    except Exception as e:
        app.logger.error(f'plot failed for "{plot_type}/{b64ids}": {e}')
        abort(500)
     
if __name__ == '__main__':
    app.run(host='0.0.0.0')
