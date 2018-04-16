from app import db
from app.models import User, Activity, Day, DaysActivities
from datetime import datetime

gimli = User.query.filter_by(username="Gimli").first()

acts = [
    Activity(activity_id=100, start_time=datetime(2018, 4, 10, 17, 0, 0), end_time=datetime(2018, 4, 10, 18, 0, 0),
             expiration=datetime(9999, 12, 31, 23, 59, 59), weight=5, user=gimli), #Tues
    Activity(activity_id=101, start_time=datetime(2018, 4, 9, 17, 0, 0), end_time=datetime(2018, 4, 9, 18, 0, 0),
             expiration=datetime(9999, 12, 31, 23, 59, 59), weight=5, user=gimli), #Mon
    Activity(activity_id=102, start_time=datetime(2018, 4, 14, 7, 0, 0), end_time=datetime(2018, 4, 14, 8, 0, 0),
             expiration=datetime(9999, 12, 31, 23, 59, 59), weight=4, user=gimli), #Sat
    Activity(activity_id=103, start_time=datetime(2018, 4, 8, 10, 0, 0), end_time=datetime(2018, 4, 8, 11, 0, 0),
             expiration=datetime(9999, 12, 31, 23, 59, 59), weight=5, user=gimli), #Sun
    Activity(activity_id=104, start_time=datetime(2018, 4, 8, 7, 0, 0), end_time=datetime(2018, 4, 8, 7, 10, 0),
             expiration=datetime(9999, 12, 31, 23, 59, 59), weight=4, user=gimli), #daily
    Activity(activity_id=105, start_time=datetime(2018, 4, 8, 15, 0, 0), end_time=datetime(2018, 4, 8, 17, 0, 0),
             expiration=datetime(9999, 12, 31, 23, 59, 59), weight=4, user=gimli), #Sun
    Activity(activity_id=106, start_time=datetime(2018, 4, 8, 6, 0, 0), end_time=datetime(2018, 4, 8, 6, 30, 0),
             expiration=datetime(9999, 12, 31, 23, 59, 59), weight=5, user=gimli), #daily
    Activity(activity_id=107, start_time=datetime(2018, 4, 8, 19, 0, 0), end_time=datetime(2018, 4, 8, 19, 30, 0),
             expiration=datetime(9999, 12, 31, 23, 59, 59), weight=3, user=gimli), #daily
    Activity(activity_id=108, start_time=datetime(2018, 4, 7, 21, 0, 0), end_time=datetime(2018, 4, 8, 6, 0, 0),
             expiration=datetime(9999, 12, 31, 23, 59, 59), weight=3, user=gimli), #daily
    Activity(activity_id=109, start_time=datetime(2018, 4, 13, 17, 0, 0), end_time=datetime(2018, 4, 13, 17, 15, 0),
             expiration=datetime(9999, 12, 31, 23, 59, 59), weight=2, user=gimli), #Fri
    Activity(activity_id=110, start_time=datetime(2018, 4, 9, 15, 0, 0), end_time=datetime(2018, 4, 9, 15, 15, 0),
             expiration=datetime(9999, 12, 31, 23, 59, 59), weight=1, user=gimli) #daily
]
for act in acts:
    db.session.add(act)
db.session.commit()

days = [
    Day(date=datetime(2018, 4, 4), user=gimli),
    Day(date=datetime(2018, 4, 5), user=gimli),
    Day(date=datetime(2018, 4, 6), user=gimli),
    Day(date=datetime(2018, 4, 7), user=gimli),
    Day(date=datetime(2018, 4, 8), user=gimli),
    Day(date=datetime(2018, 4, 9), user=gimli),
    Day(date=datetime(2018, 4, 10), user=gimli),
    Day(date=datetime(2018, 4, 11), user=gimli),
    Day(date=datetime(2018, 4, 12), user=gimli),
    Day(date=datetime(2018, 4, 13), user=gimli),
    Day(date=datetime(2018, 4, 14), user=gimli)
]
for day in days:
    db.session.add(day)
db.session.commit()

# 4, 6, 7, 8, 10 are daily
daysacts = [
    DaysActivities(completed=True, day=days[4], activity=acts[3]), # Sun
    DaysActivities(completed=True, day=days[4], activity=acts[4]),
    DaysActivities(completed=True, day=days[4], activity=acts[5]),
    DaysActivities(completed=True, day=days[4], activity=acts[6]),
    DaysActivities(completed=True, day=days[4], activity=acts[7]),
    DaysActivities(completed=True, day=days[4], activity=acts[8]),
    DaysActivities(completed=True, day=days[4], activity=acts[10]),
    DaysActivities(completed=True, day=days[5], activity=acts[1]), # Mon
    DaysActivities(completed=True, day=days[5], activity=acts[4]),
    DaysActivities(completed=True, day=days[5], activity=acts[6]),
    DaysActivities(completed=True, day=days[5], activity=acts[7]),
    DaysActivities(completed=True, day=days[5], activity=acts[8])
    DaysActivities(completed=True, day=days[5], activity=acts[10]),
    DaysActivities(completed=True, day=days[6], activity=acts[0]), # Tues
    DaysActivities(completed=False, day=days[6], activity=acts[4]),
    DaysActivities(completed=False, day=days[6], activity=acts[6]),
    DaysActivities(completed=False, day=days[6], activity=acts[7]),
    DaysActivities(completed=False, day=days[6], activity=acts[8]),
    DaysActivities(completed=False, day=days[6], activity=acts[10]),
    DaysActivities(completed=False, day=days[7], activity=acts[4]), # Wed
    DaysActivities(completed=False, day=days[7], activity=acts[6]),
    DaysActivities(completed=False, day=days[7], activity=acts[7]),
    DaysActivities(completed=False, day=days[7], activity=acts[8]),
    DaysActivities(completed=False, day=days[7], activity=acts[10]),
    DaysActivities(completed=False, day=days[8], activity=acts[4]), # Thurs
    DaysActivities(completed=False, day=days[8], activity=acts[6]),
    DaysActivities(completed=False, day=days[8], activity=acts[7]),
    DaysActivities(completed=False, day=days[8], activity=acts[8]),
    DaysActivities(completed=False, day=days[8], activity=acts[10]),
    DaysActivities(completed=False, day=days[9], activity=acts[4]), # Fri
    DaysActivities(completed=False, day=days[9], activity=acts[6]),
    DaysActivities(completed=False, day=days[9], activity=acts[7]),
    DaysActivities(completed=False, day=days[9], activity=acts[8]),
    DaysActivities(completed=True, day=days[9], activity=acts[9]),
    DaysActivities(completed=True, day=days[10], activity=acts[2]), # Sat
    DaysActivities(completed=True, day=days[10], activity=acts[4]), 
    DaysActivities(completed=True, day=days[10], activity=acts[6]),
    DaysActivities(completed=True, day=days[10], activity=acts[7]),
    DaysActivities(completed=True, day=days[10], activity=acts[8]),
    DaysActivities(completed=True, day=days[10], activity=acts[10])
]
for dayact in daysacts:
    db.session.add(dayact)
db.session.commit()
