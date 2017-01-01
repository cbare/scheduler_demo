import json
import os
import psycopg2
import time
from psycopg2.extras import DictCursor
from flask import Flask, request, session, g, redirect, url_for, abort, \
                  render_template, jsonify, send_from_directory, send_file
from utils import week_window_to_show, ScheldulerJSONEncoder
from events import PostgresDataStore

app = Flask(__name__, static_url_path='/static/')
app.json_encoder = ScheldulerJSONEncoder


## read config file
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
with open(config_path) as f:
    config = json.loads(f.read())

## initialize DB connectivity
db = PostgresDataStore(config['db_connect'])


@app.before_request
def before_request():
    ## for rough render time; see https://gist.github.com/lost-theory/4521102
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


@app.route('/api/')
def api_root():
    return 'Welcome'

## hack for development purposes: serve static content via Flask
@app.route('/')
def root():
    print('index.html requested')
    return send_file('static/index.html')

## hack for development purposes: serve static content via Flask
@app.route('/js/<path:path>')
def send_js(path):
    print('%s requested'%path)
    return send_from_directory('static', path)


@app.route('/coaches/')
def api_coaches():
    coaches = db.get_coaches()
    print(coaches)
    return jsonify(coaches)


@app.route('/schedule/<coach_id>/')
def api_schedule(coach_id):
    """
    Client's view of a coach's schedule for browsing available appointments
    """
    s,e = week_window_to_show(request.args)
    return jsonify(db.get_appointments(coach_id, s, e))





## TODO
##   coach's view of schedule showing appointment names and details during a window
##   client's view of schedule showing blocks open during a window
##   create/read/update/delete event




if __name__ == "__main__":
    app.run(debug=True, use_debugger=True, use_reloader=True)

