Changes tracked:

1) Edited readme.md to add python requests dependency
2) changed routes.py to __init__.py file to the powertoken/src/ directory
	> copied routes.py to routes_old_working.py to keep working code around just in case 
	>didn't seem to cause any errors when running the app again
	> apache redirect is redirecting from the port (:5000) so internal changes to the directory or structure shouldn't affect it


3) commented out outputlogger temporarily because it was throwing errors
4) Changed directory structure-- renamed src folder to powertoken folder. It's confusing, but consistent with all the wsgi tutorial recommendations
So application code is now in ~/powertoken/powertoken/


ADD/UPDATE these files to set your local machine configs (need sudo access)
/etc/apache2/sites-available/PowerToken.conf
~/powertoken/powertoken/powertoken.wsgi


Future look into:
Multi-role web app (admin/user): https://andypi.co.uk/2015/11/27/multiple-user-roles-python-flask/




