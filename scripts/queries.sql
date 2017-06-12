-- Get a coach's schedule within a time window
SELECT e.*
FROM event e
JOIN participant p on e.id=p.event_id
WHERE p.person_id=1
AND e.start_time<'2017-2-1 00:00:00' and e.end_time>='2017-1-1 00:00:00';

SELECT e.*
FROM event e
JOIN participant p on e.id=p.event_id
WHERE p.person_id=52
AND e.start_time<'2017-2-1 00:00:00' and e.end_time>='2017-1-1 00:00:00';

SELECT coach_event.id, coach_event.start_time, coach_event.end_time, coach_event.type, client_event.person_id as client_id
FROM (
    SELECT e.*, p.person_id
    FROM event e
    JOIN participant p on e.id=p.event_id
    WHERE p.person_id=2
    AND e.start_time<'2017-2-1 00:00:00' and e.end_time>='2017-1-1 00:00:00') coach_event
LEFT JOIN (
    SELECT e.id, p.person_id
    FROM event e
    JOIN participant p on e.id=p.event_id
    AND e.start_time<'2017-2-1 00:00:00' and e.end_time>='2017-1-1 00:00:00'
) client_event on coach_event.id=client_event.id and client_event.person_id!=coach_event.person_id;

