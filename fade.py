from app import db
from app.models import User, Activity, Day, DaysActivities
from datetime import datetime

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

	day_1_ago = Day.query.filter_by(date=(day - timedelta(1))).first()
	day_1_ago_score = 0
	for act in day_1_ago.days_activities:
		day_1_ago_score += int(act.completed * (act.activity.weight / 2))

	day_2_ago = Day.query.filter_by(date=(day - timedelta(2))).first()
	day_2_ago_score = 0
	for act in day_2_ago.days_activities:
		day_2_ago_score += int(act.completed * (act.activity.weight / 3))

	day_3_ago = Day.query.filter_by(date=(day - timedelta(3))).first()
	day_3_ago_score = 0
	for act in day_3_ago.days_activities:
		day_3_ago_score += int(act.completed * (act.activity.weight / 4))

	day_4_ago = Day.query.filter_by(date=(day - timedelta(4))).first()
	day_4_ago_score = 0
	for act in day_4_ago.days_activities:
		day_4_ago_score += int(act.completed * (act.activity.weight / 5))

	score = today_score + day_1_ago_score + day_2_ago_score + day_3_ago_score + day_4_ago_score
	return score / get_possible_score(day)