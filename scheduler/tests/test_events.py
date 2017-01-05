"""
Test CRUD on Events
"""
import os
import json
from events import Event, PostgresDataStore
from datetime import datetime, timedelta

db = None

def setup():
    global db
    ## read config file
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.json')
    with open(config_path) as f:
        config = json.loads(f.read())

    ## initialize DB connectivity
    db = PostgresDataStore(config['db_connect'])

def test_event():
    print("\ntest_event")
    event = db.create_event(start_time=datetime(2017,4,28,12,00),
                            end_time=datetime(2017,4,28,14,00),
                            name="Chris's Birthday Party",
                            notes="Serious Pie Westlake, Seattle WA",
                            type='event',
                            participants=[1,2,3,4,5,6,7,8])
    print("created:", event)

    event2 = db.get_event(event.id)
    print("got:", event)
    assert event2==event

    event.participants.remove(8)
    event.participants.remove(7)
    event.participants.append(9)
    event.participants.append(10)
    event.notes = "Pizza and beer at Serious Pie Westlake, Seattle WA"
    event.name  = "Chris's Huge Birthday Party"

    event3 = db.update_event(**event.__dict__)
    print("updated:", event)
    assert event3.name == "Chris's Huge Birthday Party"
    assert event3.notes == "Pizza and beer at Serious Pie Westlake, Seattle WA"
    assert event3.participants == [1,2,3,4,5,6,9,10]

    event = db.delete_event(event.id)
    print("deleted:", event)

    try:
        event = db.get_event(event.id)
        assert False, "Should have raised ValueError"
    except ValueError as ve:
        print("it's gone:", event)


