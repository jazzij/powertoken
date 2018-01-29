# manager.py

from crontab import CronTab

pt_cron = CronTab(user="franz322")
job = pt_cron.new(command="python routes.py")
job.day.every(1)
pt_cron.write()