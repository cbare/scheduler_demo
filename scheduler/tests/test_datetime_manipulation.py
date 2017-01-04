from events import Event, divide_into_blocks, appointments
from datetime import datetime, timedelta


def test_divide_into_blocks():
    event = Event(start_time=datetime(2020,4,1,11,0), end_time=datetime(2020,4,1,15,0), type='schedulable')
    blocks = list(divide_into_blocks(event))
    print('\nblocks:')
    for block in blocks:
        print(' ', block)
    assert len(blocks) == 4
    assert blocks == [Event(datetime(2020,4,1,11,0),datetime(2020,4,1,12,0), name='Available', type='open slot'),
                      Event(datetime(2020,4,1,12,0),datetime(2020,4,1,13,0), name='Available', type='open slot'),
                      Event(datetime(2020,4,1,13,0),datetime(2020,4,1,14,0), name='Available', type='open slot'),
                      Event(datetime(2020,4,1,14,0),datetime(2020,4,1,15,0), name='Available', type='open slot')]


def test_blocks():
    events = (Event(start_time=datetime(2020,4,1,11,0), end_time=datetime(2020,4,1,15,0), type='schedulable'),
              Event(start_time=datetime(2020,4,2,10,0), end_time=datetime(2020,4,2,12,0), type='schedulable'),
              Event(start_time=datetime(2020,4,2,13,0), end_time=datetime(2020,4,2,17,0), type='schedulable'),
              Event(start_time=datetime(2020,4,2,11,0), end_time=datetime(2020,4,2,12,0), type='coaching'),
              Event(start_time=datetime(2020,4,2,13,0), end_time=datetime(2020,4,2,14,0), type='coaching'),
              Event(start_time=datetime(2020,4,2,14,0), end_time=datetime(2020,4,2,15,0), type='coaching'))

    blocks = appointments(events)

    print('\nblocks:')
    for block in blocks:
        print(' ', block)
