Changes tracked:

1) Edited readme to add python requests dependency
2) added __init__.py file to the powertoken/src/ directory
3) copied routes.py to routes_old_working.py to keep working code around

Application code (__init.py, static, templates) is in 
~/powertoken/src


4) changed name of routes.py to __init__.py 
	>didn't seem to cause any errors when running the app again
	> apache redirect is redirecting from the port (:5000) so internal changes to the directory or structure shouldn't affect it


5)


Errors: gloabl name 'outputLogger is not defined)
a) commented out outputlogger temporarily


(charge) umhadmin@cs-u-cyberdemon:~/Documents/PowerToken_Proj/powertoken/src$ sudo a2ensite PowerToken
Enabling site PowerToken.
To activate the new configuration, you need to run:
  service apache2 reload


path on cyberdemon
/home/umhadmin/Documents/PowerToken_Proj/powertoken/src


PATHS to UPDATE
/etc/apache2/sites-available/PowerToken.conf
~/powertoken/powertoken/powertoken.wsgi

f


