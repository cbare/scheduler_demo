"""
Represent and manipulate calendar events
"""
import psycopg2
from psycopg2.extras import DictCursor
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA


class Event:
    def __init__(self, start_time, end_time, type, id=None, name=None, notes=None):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.name = name
        self.type = type
        self.notes = notes
        self.participants = []

    def __repr__(self):
        return "Event(start_time="+str(self.start_time)+\
                    ", end_time="+str(self.end_time)+\
                    ", type="+self.type+\
                    (", id="+str(self.id) if self.id else '')+\
                    (", name="+self.name if self.name else '')+\
                    (", notes="+self.notes if self.notes else '')+")"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def divide_into_blocks(event, block_len=timedelta(hours=1)):
    st = event.start_time
    et = st + block_len
    while et <= event.end_time:
        yield Event(start_time=st, end_time=et, name='Available', type='open slot')
        st = et
        et = st + block_len


def already_scheduled(event, events):
    for other_event in events:
        if other_event.type != 'schedulable' and \
           other_event.start_time < event.end_time and \
           other_event.end_time > event.start_time:
            return True
    return False


def appointments(events):
    blocks = [block for event in events if event.type=='schedulable'
                    for block in divide_into_blocks(event)]
    for block in blocks:
        if already_scheduled(block, events):
            block.name = 'Booked'
            block.type = 'unavailable slot'
    return blocks


class PostgresDataStore:
    """
    Layer that represents our data store
    """
    def __init__(self, connect_string):
        self.connect_string = connect_string

    def get_coaches(self):
        conn = None
        try:
            conn = psycopg2.connect(self.connect_string, cursor_factory=DictCursor)
            with conn:
                with conn.cursor() as curs:
                    query = """\
                        SELECT *
                        FROM person p
                        WHERE p.coach;"""
                    curs.execute(query)
                    return [dict(row) for row in curs]
        finally:
            if conn: conn.close()

    def get_events_between(self, person_id, start_time, end_time):
        conn = None
        try:
            conn = psycopg2.connect(self.connect_string, cursor_factory=DictCursor)
            with conn:
                with conn.cursor() as curs:
                    query = """\
                        SELECT e.id, e.type, e.start_time, e.end_time, e.name
                        FROM event e
                        JOIN participant p on e.id=p.event_id
                        WHERE p.person_id=%s
                        AND e.end_time>%s and e.start_time<%s
                        ORDER BY e.start_time;"""
                    curs.execute(query, (person_id, start_time, end_time))
                    return [Event(**e) for e in curs]
        finally:
            if conn: conn.close()

    def get_appointments(self, person_id, start_time, end_time):
        return appointments(self.get_events_between(person_id, start_time, end_time))




