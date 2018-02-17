"""
module common
Functions common to both the weconnect and powertoken models.
Created by Abigail Franz on 2/16/2018
"""

import logging

error_logger = logging.getLogger("ptErrorLogger")
error_logger.setLevel(logging.ERROR)

def is_valid(response):
	"""
	Return a Boolean value indicating the success of an HTTP request.
	"""
	if response.status_code >= 300:
		error_logger.error(format(" Request could not be completed. Error: %d %s" 
				% (response.status_code, response.text())))
		return False
	else:
		return True