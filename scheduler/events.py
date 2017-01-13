"""
Represent and manipulate calendar events
"""
import psycopg2
from psycopg2.extras import DictCursor
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA


class Event:
    """
    Represent a calendar event.

    Type should be one of a limited set of event type strings. The type
    'schedulable' signifies a block of time during which a coach is
    available for appointments.
    """

    def __init__(self, start_time, end_time, type, id=None, name=None, notes=None, participants=[]):
        """
        :param start_time: a datetime
        :param end_time: a datetime
        :param type: a string used to indicate event types that need special handling
        :param id: primary key from DB
        :param name: a string
        :param notes: free text description of event
        :param participants: IDs of people participating in the event
        """
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.name = name
        self.type = type
        self.notes = notes
        self.participants = participants

    def __repr__(self):
        return "Event(start_time="+str(self.start_time)+\
                    ", end_time="+str(self.end_time)+\
                    ", type="+self.type+\
                    (", id="+str(self.id) if self.id else '')+\
                    (", name="+self.name if self.name else '')+\
                    (", notes="+self.notes if self.notes else '')+\
                    (", participants="+str(self.participants) if self.participants else '')+")"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def divide_into_blocks(event, block_len=timedelta(hours=1)):
    """
    Given a schedulable time period, divide into 1 hour blocks and
    return generator of Event objects representing slots that can
    be offered to clients.

    :param event: a time period in which a coach is available for scheduling
    :param block_len: length of blocks into which the initial time period will be subdivided

    :type event: events.Event
    :type block_len: datetime.timedelta

    :return: a generator of Event objects
    """
    st = event.start_time
    et = st + block_len
    while et <= event.end_time:
        yield Event(start_time=st, end_time=et, name='Available', type='open slot')
        st = et
        et = st + block_len


def has_conflicts(event, events):
    """
    Detect the precence of conflicting events

    :param event: an event
    :param events: a list of events that potentially conflict with the first event
    """
    for other_event in events:
        if other_event.type != 'schedulable' and \
           other_event.start_time < event.end_time and \
           other_event.end_time > event.start_time:
            return True
    return False

def remove_conflicting(events, potential_conflicts):
    """
    Purge a list of events of those which have a conflict.
    """
    return [event for event in events if not has_conflicts(event, potential_conflicts)]

def appointments(events):
    """
    From the events of a coach's calendar, deduce the appointment slots
    that are available.
    """
    blocks = [block for event in events if event.type=='schedulable'
                    for block in divide_into_blocks(event)]
    for block in blocks:
        if has_conflicts(block, events):
            block.name = 'Booked'
            block.type = 'unavailable slot'
    return blocks


class NonExistantIdError(ValueError):
    pass


class PostgresCursor:
    """
    A context manager for Postgres cursors
    """
    def __init__(self, connect_string):
        self.connect_string = connect_string

    def __enter__(self):
        self.conn = psycopg2.connect(self.connect_string, cursor_factory=DictCursor)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            if self.conn:
                self.conn.commit()
        else:
            if self.conn:
                self.conn.rollback()
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        return False


class PostgresDataStore:
    """
    Layer that represents our data store
    """
    def __init__(self, connect_string):
        self.connect_string = connect_string

    def get_coaches(self):
        """
        Return a list of dict's each representing a coach
        """
        with PostgresCursor(self.connect_string) as curs:
            query = """\
                SELECT *
                FROM person p
                WHERE p.coach;"""
            curs.execute(query)
            return [dict(row) for row in curs]

    def get_participants(self, event_id):
        with PostgresCursor(self.connect_string) as curs:
            query = """\
                SELECT person.*
                FROM person
                JOIN participant on person.id=participant.person_id
                WHERE participant.event_id=%s"""
            curs.execute(query, (event_id,))
            if curs.rowcount < 1:
                raise NonExistantIdError("no participants for event id %s" % event_id)
            return [dict(row) for row in curs]

    def get_events_between(self, person_id, start_time, end_time):
        with PostgresCursor(self.connect_string) as curs:
            query = """\
                SELECT e.id, e.type, e.start_time, e.end_time, e.name, e.notes
                FROM event e
                JOIN participant p on e.id=p.event_id
                WHERE p.person_id=%s
                AND e.end_time>%s and e.start_time<%s
                ORDER BY e.start_time;"""
            curs.execute(query, (person_id, start_time, end_time))
            events = [Event(**e) for e in curs]
            for event in events:
                curs.execute("SELECT person_id FROM participant WHERE event_id=%s", (event.id,))
                event.participants = [row['person_id'] for row in curs]
            return events

    def get_appointments(self, person_id, start_time, end_time):
        return appointments(self.get_events_between(person_id, start_time, end_time))

    def get_calendar(self, person_id, coach_id, start_time, end_time):
        """
        For scheduling coaching sessions, we provide a view of all events within
        a window for both the coach and the client, including slots available
        for coaching sessions.
        """
        user_events = self.get_events_between(person_id, start_time, end_time)
        coach_appointments = remove_conflicting(self.get_appointments(coach_id, start_time, end_time), user_events)
        return coach_appointments + user_events

    def create_event(self, start_time, end_time, name=None, notes=None, type='event', participants=[]):
        with PostgresCursor(self.connect_string) as curs:
            query = """\
                INSERT INTO event
                (start_time, end_time, name, notes, type)
                VALUES
                (%s, %s, %s, %s, %s)
                RETURNING id;"""
            curs.execute(query, (start_time, end_time, name, notes, type))
            event_id = curs.fetchone()[0]
            for participant_id in participants:
                curs.execute("INSERT INTO participant (event_id, person_id) VALUES (%s, %s);", (event_id, participant_id))
            return Event(id=event_id,
                         start_time=start_time,
                         end_time=end_time,
                         name=name,
                         notes=notes,
                         type=type,
                         participants=participants)

    def update_event(self, id, start_time, end_time, name, notes, type, participants=None):
        with PostgresCursor(self.connect_string) as curs:
            query = """\
                UPDATE event
                SET (start_time, end_time, name, notes, type) = (%s,%s,%s,%s,%s)
                WHERE id=%s"""
            curs.execute(query, (start_time, end_time, name, notes, type, id))

            ## update participants by adding or deleting participants as necessary
            if participants is not None:
                curs.execute("SELECT person_id FROM participant WHERE event_id=%s", (id,))
                current_participants = [row[0] for row in curs.fetchall()]
                for participant_id in participants:
                    if participant_id not in current_participants:
                        curs.execute("INSERT INTO participant (event_id, person_id) VALUES (%s, %s);", (id, participant_id))
                for participant_id in current_participants:
                    if participant_id not in participants:
                        curs.execute("DELETE FROM participant WHERE event_id=%s and person_id=%s;", (id, participant_id))

            ## construct newly modified event from database
            curs.execute("SELECT person_id FROM participant WHERE event_id=%s", (id,))
            new_participants = [row[0] for row in curs.fetchall()]
            curs.execute("SELECT * FROM event WHERE id=%s", (id,))
            if curs.rowcount < 1:
                raise NonExistantIdError("no event exists with id %s" % id)
            return Event(participants=new_participants, **curs.fetchone())

    def delete_event(self, id):
        with PostgresCursor(self.connect_string) as curs:
            ## return deleted event
            curs.execute("SELECT person_id FROM participant WHERE event_id=%s", (id,))
            participants = [row[0] for row in curs.fetchall()]
            curs.execute("SELECT * FROM event WHERE id=%s", (id,))
            event = Event(participants=participants, **curs.fetchone())

            ## delete
            curs.execute("DELETE FROM event WHERE id=%s", (id,))
            return event

    def get_event(self, id):
        with PostgresCursor(self.connect_string) as curs:
            curs.execute("SELECT person_id FROM participant WHERE event_id=%s", (id,))
            participants = [row[0] for row in curs.fetchall()]
            curs.execute("SELECT * FROM event WHERE id=%s", (id,))
            if curs.rowcount < 1:
                raise NonExistantIdError("no event exists with id %s" % id)
            return Event(participants=participants, **curs.fetchone())


