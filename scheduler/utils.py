from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta, SU, MO, TU, WE, TH, FR, SA
from dateutil.parser import parse
from flask.json import JSONEncoder
from events import Event


class ScheldulerJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Event):
            return {attr:getattr(obj,attr)
                    for attr in ['id','start_time','end_time', 'name', 'type', 'notes', 'participants']
                    if getattr(obj,attr)}
        elif isinstance(obj, datetime):
            return obj.isoformat()+'Z'
        return super(ScheldulerJSONEncoder, self).default(obj)


def week_window_to_show(kwargs={}):
    """
    Figure out whether to show this week or next week
    """
    s = e = None
    if 'from' in kwargs:
        s = parse(kwargs['from'])
        if 'to' in kwargs:
            e = parse(kwargs['to'])
        else:
            e = s + timedelta(weeks=1)
    else:
        today = date.today()
        if today.isoweekday() > 4:
            s = today + relativedelta(weekday=SU(+1))
        else:
            s = today + relativedelta(weekday=SU(-1))
    if not e:
        e = s + relativedelta(weeks=+1)
    return s, e




