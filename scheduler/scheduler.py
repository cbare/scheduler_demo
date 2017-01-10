"""
Flask web service endpoints for the Scheduler app.
"""
import json
import os
import psycopg2
import time
from psycopg2.extras import DictCursor
from flask import Flask, request, session, g, redirect, url_for, abort, \
                  render_template, jsonify, send_from_directory, send_file
from utils import week_window_to_show, ScheldulerJSONEncoder
from events import PostgresDataStore, NonExistantIdError

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
@app.route('/', methods=['GET'])
def root():
    print('index.html requested')
    return send_file('static/index.html')

## hack for development purposes: serve static content via Flask
@app.route('/js/<path:path>', methods=['GET'])
def send_js(path):
    print('%s requested'%path)
    return send_from_directory('static', path)


@app.route('/coaches/', methods=['GET'])
def api_coaches():
    """
    Get the list of all coaches for populating menu
    """
    coaches = db.get_coaches()
    print(coaches)
    return jsonify(coaches)


@app.route('/participants/<int:event_id>/', methods=['GET'])
def api_participants(event_id):
    """
    Get the list of people participating in the given event
    """
    return jsonify(db.get_participants(event_id))


@app.route('/schedule/<int:coach_id>/', methods=['GET'])
def api_schedule(coach_id):
    """
    Generic view of a coach's schedule
    """
    s,e = week_window_to_show(request.args)
    return jsonify(db.get_appointments(coach_id, s, e))


@app.route('/calendar/<int:person_id>/<int:coach_id>/', methods=['GET'])
def api_schedule_with_coach(person_id, coach_id):
    """
    Client's view of a coach's schedule for browsing available appointments
    """
    s,e = week_window_to_show(request.args)
    return jsonify(db.get_calendar(person_id, coach_id, s, e))


@app.route('/event/', methods=['POST', 'PUT', 'DELETE'])
@app.route('/event/<int:event_id>/', methods=['GET', 'DELETE'])
def api_event(event_id=None):
    """
    CRUD for events.
    Post=book a new event, Put=update an existing event
    Delete can have a JSON body or just refer to an event by its ID in the URL
    """
    if request.method=='POST':
        ap_request = request.get_json()
        ap = db.create_event(**ap_request)
        return jsonify(ap)
    elif request.method=='GET':
        return jsonify(db.get_event(event_id))
    elif request.method=='PUT':
        ap_request = request.get_json()
        ap = db.update_event(**ap_request)
        return jsonify(ap)
    elif request.method=='DELETE':
        if not event_id:
            ap_request = request.get_json()
            event_id = ap_request['id']
        return jsonify(db.delete_event(event_id))
    else:
        raise ValueError('Unsupported method '+request.method)


@app.errorhandler(NonExistantIdError)
def handle_bad_request(ex):
    """
    Example of returning a proper HTTP error code and JSON error message
    """
    response = jsonify({'error-message':str(ex)})
    response.status_code = 404
    return response



if __name__ == "__main__":
    app.run(debug=True, use_debugger=True, use_reloader=True)

