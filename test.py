from background.db import session
from app.models import User, Event, Activity
from app.viewmodels import EventLogViewModel

events = session.query(Event).all()
eventz = Event.query.all()
acts = Activity.query.all()

selected = Event.query.filter_by()

em = EventLogViewModel(events[2])
print(em)