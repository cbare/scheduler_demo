# -*- coding: utf-8 -*-
"""
Create ridiculous fake scheduling data
"""
import dateutil
import json
import os
import psycopg2
import random
from psycopg2.extras import NamedTupleCursor
from itertools import product
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA
from dateutil.parser import parse

## read config file
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
with open(config_path) as f:
    config = json.loads(f.read())


coaches = [
    'Devonté Hynes',
    'Kendrick Lamar',
    'Beyoncé Giselle Knowles',
    'Kanye West',
    'Taylor Swift',
    'John Coltrane',
    'Bill Evans',
    'Paul Chambers']

## thanks http://listofrandomnames.com/
clients = [
    'Lindsey Lamphere', 'Alanna Atherton', 'Pearl Pedigo', 'Virgil Venable',
    'Rebbeca Rowser', 'Sharri Shirkey', 'Rea Roosa', 'Felecia Feuerstein',
    'Malika Mclendon', 'Gene Gatewood', 'Denisse Downie', 'Tyrell Tedesco',
    'Emogene Ericsson', 'Bernadette Banner', 'Beverley Boothe', 'Cheri Conway',
    'Milagros Martines', 'Evon Eriksen', 'Rayford Rolland', 'Mazie Mossey',
    'Melynda Main', 'Angle Ahmed', 'Rozella Rohlfing', 'Bea Brandis',
    'Thao Turbeville', 'Wanetta Whitmire', 'Cathleen Clagon', 'Cheyenne Casto',
    'Nakia Nolte', 'Fernanda Fava', 'Lai Lowy', 'Chiquita Charboneau',
    'Glayds Gettinger', 'Sherrie Sebree', 'Eliana Ezell', 'Chad Cabell',
    'Stanton Sturdevant', 'Hugo Hugh', 'Caroline Crossman', 'Candie Collard',
    'Tawny Toenjes', 'Cristin Crutcher', 'Tien Turcotte', 'Rina Rabon',
    'Thaddeus Thurmon', 'Iluminada Infantino', 'Judie Jourdan', 'Tory Tookes',
    'Kendall Kroger', 'Charolette Carrol']

HOLIDAYS = [parse(d).date() for d in (
    "December 26, 2016",
    "January 02, 2017",
    "January 16, 2017",
    "February 20, 2017",
    "May 29, 2017",
    "July 04, 2017",
    "September 04, 2017",
    "October 09, 2017",
    "November 10, 2017",
    "November 23, 2017",
    "December 25, 2017")]

MORNING = 0
AFTERNOON = 1


def make_work_schedule(weeks=1, tz=dateutil.tz.gettz('PST')):
    """
    Make up a schedule of working hours for a coach over a number of weeks.

    :returns: a list of schedulable blocks of working time normalized to UTC.
    """
    n = datetime.now()
    ## 8 AM in the coach's local time zone
    s0 = datetime(year=n.year, month=n.month, day=n.day, hour=8,minute=0,second=0,microsecond=0)

    ## We'll give the coaches a couple blocks of admin time each week
    ## represented as a tuple of morning/afternoon and weekday [0-4]
    ## because datetime.weekday() returns 0 for Monday
    admin_blocks = tuple((block, wd) for block,wd in product((MORNING,AFTERNOON), range(5)))
    admin_blocks = random.sample(admin_blocks, 2)

    ## create a template for a week
    week_template = []
    for s in [s0 + relativedelta(weekday=wd) for wd in (MO, TU, WE, TH, FR)]:
        ## morning block
        if (MORNING,s.weekday()) not in admin_blocks:
            week_template.append((s, s+relativedelta(hours=4)))
        ## afternoon block
        if (AFTERNOON,s.weekday()) not in admin_blocks:
            week_template.append((s+relativedelta(hours=5), s+relativedelta(hours=9)))

    ## create schedule by applying template with holidays removed
    ## note that we normalize to UTC by adding time zone offset
    schedule = []
    for i in range(0,weeks):
        week_i = relativedelta(weeks=i)
        for s,e in week_template:
            s += week_i
            e += week_i
            if s.date() not in HOLIDAYS:
                schedule.append((s-tz.utcoffset(s), e-tz.utcoffset(e)))

    return schedule


def slots_available(coach_id, date, tz=dateutil.tz.gettz('PST'), cursor=None):
    st = datetime(year=date.year,month=date.month,day=date.day)
    st -= tz.utcoffset(st)
    et = st + timedelta(hours=24)
    query = """\
        SELECT e.* 
        FROM event e JOIN participant p ON e.id=p.event_id 
        WHERE p.person_id=%s
        AND e.end_time>=%s and e.start_time<=%s;"""
    cursor.execute(query, (coach_id, st, et))

    schedulable = []
    appts = []
    for row in curs:
        if row.type == 'schedulable':
            schedulable.append((row.start_time, row.end_time))
        else:
            appts.append((row.start_time, row.end_time))

    slots = []
    for s,e in schedulable:
        n_slots = (e-s) // timedelta(hours=1)
        for i in range(n_slots):
            slot_s = s+timedelta(hours=i)
            slot_e = s+timedelta(hours=(i+1))

            for appt_s, appt_e in appts:
                if slot_s <= appt_e and slot_e >= appt_s:
                    ## slot overlaps with another appointment
                    break
            else:
                slots.append((slot_s, slot_e))
    return slots

def create_event(start_time, end_time, event_type='appointment', name=None, participants=[], notes=None, cursor=None):
    cursor.execute("INSERT INTO event (start_time, end_time, type, name, notes) VALUES (%s, %s, %s, %s, %s) RETURNING id;",\
                   (start_time, end_time, event_type, name, notes))
    event_id = curs.fetchone()[0]
    for person_id in participants:
        cursor.execute("INSERT INTO participant (event_id, person_id) VALUES (%s, %s);", (event_id, person_id))
    return event_id


coach_ids = []
client_ids = []
client_coaches = {} 

try:
    conn = psycopg2.connect(config['db_connect'], cursor_factory=NamedTupleCursor)

    with conn:
        with conn.cursor() as curs:
            ## populate person table
            for coach in coaches:
                fn, ln = coach.rsplit(maxsplit=1)
                curs.execute("INSERT INTO person (first_name, last_name, coach) VALUES (%s, %s, %s) RETURNING id;",(fn,ln,True))
                coach_ids.append(curs.fetchone()[0])

            for client in clients:
                fn, ln = client.rsplit(maxsplit=1)
                curs.execute("INSERT INTO person (first_name, last_name, client) VALUES (%s, %s, %s) RETURNING id;",(fn,ln,True))
                client_ids.append(curs.fetchone()[0])

            ## associate coaches with clients
            for i in client_ids:
                j = random.choice(coach_ids)
                client_coaches[i] = j
                curs.execute("INSERT INTO relationship (coach_id, client_id, since) VALUES (%s, %s, %s);",(j,i, datetime.now()))

    with conn:
        with conn.cursor() as curs:
            ## a coach is schedulable during working hours
            coach_tzs = {}
            for coach_id in coach_ids:
                coach_tzs[coach_id] = dateutil.tz.gettz(random.choice(('PST','EST')))
                schedule = make_work_schedule(weeks=26, tz=coach_tzs[coach_id])
                for s,e in schedule:
                    curs.execute("INSERT INTO event (start_time, end_time, type) VALUES (%s, %s, %s) RETURNING id;", (s,e,'schedulable'))
                    event_id = curs.fetchone()[0]
                    curs.execute("INSERT INTO participant (event_id, person_id) VALUES (%s, %s);", (event_id, coach_id))

    with conn:
        with conn.cursor() as curs:
            ## make some appointments over the next few weeks
            for client_id in client_ids:
                coach_id = client_coaches[client_id]
                coach_tz = coach_tzs[coach_id]
                d = date.today() + timedelta(days=random.randint(1,30))
                for i in range(6):
                    max_d = d + timedelta(days=7)
                    slots = slots_available(coach_id, d, tz=coach_tz, cursor=curs)
                    while not slots:
                        d += timedelta(days=1)
                        if d > max_d:
                            break
                        slots = slots_available(coach_id, d, tz=coach_tz, cursor=curs)
                    if slots:
                        slot = random.choice(slots)
                        create_event(slot[0], slot[1], event_type='coaching', participants=[coach_id, client_id], cursor=curs)
                    d += timedelta(days=random.randint(25,35))
finally:
    conn.close()

