"""
module __init__\n
Script that polls WEconnect and updates Fitbit in the background.\n
To run, type "python __init__.py" at the command line.\n
Created by Abigail Franz on 2/20/2018\n
Last modified by Abigail Franz on 2/21/2018
"""

import powertoken

pt = powertoken.PowerToken()
pt.run()