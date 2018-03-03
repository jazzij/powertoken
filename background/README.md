# PowerToken Background Scripts
### (Last Update, 3/2/2018)


## Dependencies

* Python 2.7 (but should be compatible with Python 3)
* Fitbit Web API (https://dev.fitbit.com/reference/web-api/quickstart/)
* WEconnect Web API (documentation not available to the public)
* dbmanager module (common to the entire PowerToken project)


## Brief Overview

The scripts `hourly_maintenance.py` and `poll_and_update.py` are meant to be run as Cron jobs. You can edit your Cron Tab to run them periodically using `crontab -e` and adding these two lines:

`0 * * * * python <absolute-path>/powertoken/background/hourly_maintenance.py > <absolute-path>/powertoken/ptdata/maintenance.log`

`0,15,30,45 * * * * python <absolute-path>/powertoken/background/poll_and_update.py > <absolute-path>/powertoken/ptdata/polling.log`

We have the maintenance script set to run at the beginning of every hour and the polling script to run at the 0, 15, 30, and 45 minute marks (effectively every 15 minutes).


## Database Maintenance

Every hour, the `hourly_maintenance.py` script performs 5 activities:

In the `users` table of the database:
* Makes sure all user fields are complete, and removes incomplete profiles.
* Makes sure all WEconnect and Fitbit access tokens are unexpired.

In the `activities` table:
* If any users have been removed from the database, deletes their activity records.
* Removes any expired activities.
* If users have added or updated activities, adds those to the database.


## Poll WEconnect and update Fitbit

The `poll_and_update.py` script performs the main function of the PowerToken system. The workflow is as follows:

1. If any activities (from the database) start or end within the next 15 minutes, add the user who owns them to a list. 
2. For each user in the list:
    1. Poll WEconnect for progress. Progress is returned as a decimal percentage.
    2. Update Fitbit with the new step count `progress * 1000000`.
    3. Add an entry to the `logs` table of the database.
