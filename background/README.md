# PowerToken Background Scripts
### (Last Update, 5/5/2018)


## Dependencies

* Python 2.7 (but should be compatible with Python 3)
* Python Requests 2.18.4 (http://docs.python-requests.org/en/master/)
* Python SQLAlchemy 1.2.5 (http://docs.sqlalchemy.org/en/latest)
* Fitbit Web API (https://dev.fitbit.com/reference/web-api/quickstart/)
* WEconnect Web API (documentation not available to the public)


## Brief Overview

The scripts [maintenance.py](maintenance.py) and [polling.py](polling.py) are meant to be run as Cron jobs. You can edit your Cron Tab to run them periodically using `crontab -e` and adding these two lines:

`0 * * * * bash <absolute-path>/powertoken/run_maintenance.sh`

`0,15,30,45 * * * * bash <absolute-path>/powertoken/run_polling.sh`

We have the maintenance script set to run at the beginning of every hour and the polling script to run at the 0, 15, 30, and 45 minute marks (effectively every 15 minutes).

You might notice that we are not running [maintenance.py](maintenance.py) and [polling.py](polling.py) directly from Cron. This is because both utilize a virtualenv, which Cron has no knowledge of. Instead, the bash scripts run_maintenance.sh and run_polling.sh activate the virtualenv, run the respective Python script, and then deactivate the virtualenv. Example bash scripts, [run_maintenance_ex.sh](../run_maintenance_ex.sh) and [run_polling_ex.sh](../run_polling.sh), have been included in the root directory of the repository.


## Database Maintenance

Every hour, the [maintenance.py](maintenance.py) script performs the following activities:

* Deletes all incomplete profiles from the `user` table.
* If any users have been removed from the database, deletes their `activity` and `day` (and corresponding `event`) records.
* If users have added or updated activities, updates the database.
* Populates each user's `day` and corresponding `event` records for today.


## Poll WEconnect and update Fitbit

The [polling.py](polling.py) script performs the main function of the PowerToken system. The workflow is as follows:

1. If any activities (from the database) start or end within the next 15 minutes, add the user who owns them to a list. 
2. For each user in the list:
    1. Poll WEconnect for progress. Progress is returned as a decimal percentage.
    2. Update Fitbit with the new step count `progress * 1000000`.
    3. Add an entry to the `logs` table of the database.

The two modules used by the application are `weconnect` and `fitbit`, which are located in the [weconnect.py](weconnect.py) and [fitbit.py](fitbit.py) files, respectively. As might be expected, the `weconnect` class handles API calls to WEconnect and the `fitbit` module handles API calls to Fitbit.


## Notes

Both scripts make use of the modules `background.helpers` and `background.models`. In turn, all the modules rely on `background.db`, which handles the database session. 

If something isn't working, it's probably a path issue. Check that your directory structure matches the structure the scripts are expecting.
