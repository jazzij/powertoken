from app import db
from app.models import User, Activity, Day, DaysActivities
from datetime import datetime, timedelta

def get_possible_score(day):
    """day is of type Day"""
    daily_acts = day.days_activities.all()
    score = 0
    for act in daily_acts:
        score += act.activity.weight
    return score

def get_days_progress(day):
	"""day is of type Day"""
	today_score = 0
	for act in day.days_activities:
		today_score += (act.completed * act.activity.weight)
	print("today_score: {}".format(today_score))

	day_1_ago = Day.query.filter_by(date=(day.date - timedelta(1))).first()
	day_1_ago_score = 0
	for act in day_1_ago.days_activities:
		day_1_ago_score += int(act.completed * (act.activity.weight / 2))
	print("day_1_ago_score: {}".format(day_1_ago_score))

	day_2_ago = Day.query.filter_by(date=(day.date - timedelta(2))).first()
	day_2_ago_score = 0
	for act in day_2_ago.days_activities:
		day_2_ago_score += int(act.completed * (act.activity.weight / 3))
	print("day_2_ago_score: {}".format(day_2_ago_score))

	day_3_ago = Day.query.filter_by(date=(day.date - timedelta(3))).first()
	day_3_ago_score = 0
	for act in day_3_ago.days_activities:
		day_3_ago_score += int(act.completed * (act.activity.weight / 4))
	print("day_3_ago_score: {}".format(day_3_ago_score))

	day_4_ago = Day.query.filter_by(date=(day.date - timedelta(4))).first()
	day_4_ago_score = 0
	for act in day_4_ago.days_activities:
		day_4_ago_score += int(act.completed * (act.activity.weight / 5))
	print("day_4_ago_score: {}".format(day_4_ago_score))

	score = today_score + day_1_ago_score + day_2_ago_score + day_3_ago_score + day_4_ago_score
	print("score: {}".format(score))
	return float(score) / float(get_possible_score(day))

for i in range(8, 15):
	day = Day.query.filter_by(date=datetime(2018, 4, i)).first()
	print(get_days_progress(day))

