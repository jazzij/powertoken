from types import *
from sqlite3 import Row
import common
import usermanager
import logmanager

def run_tests():
	try:
		assert common.DB_PATH == "data/ptdb"
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert len(common._get_sqlite_timestamp()) == 23
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert usermanager.create_users_if_dne()
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert usermanager.insert_user("test_u")
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert usermanager.user_exists("test_u")
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert not usermanager.user_exists("blablabla")
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert not usermanager.wc_info_filled("test_u")
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert usermanager.update_wc_info("test_u", "daily", "11111", "3590sxeioel34ios34109")
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert usermanager.wc_info_filled("test_u")
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert not usermanager.fb_info_filled("test_u")
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert usermanager.update_fb_info("test_u", "sl35902nej3390fh493wj394hlhk039")
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert usermanager.fb_info_filled("test_u")
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert not usermanager.get_users() is NoneType
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	user = usermanager.get_user("test_u")
	
	try:
		assert isinstance(user, Row)
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert not user["id"] is NoneType
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert not user["username"] is NoneType
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert not user["registered_on"] is NoneType
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert not user["goal_period"] is NoneType
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert not user["wc_id"] is NoneType
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert not user["wc_token"] is NoneType
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert not user["fb_token"] is NoneType
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert logmanager.create_logs_if_dne()
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert logmanager.insert_log(user["id"], 0.5, 500000)
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)

	try:
		assert not logmanager.get_logs() is NoneType
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert not logmanager.get_logs("test_u") is NoneType
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert not logmanager.get_logs(user_id=user["id"]) is NoneType
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)
	
	try:
		assert not logmanager.get_logs("test_u", user["id"])
	except AssertionError as e:
		print(e)
	except Exception as e:
		print(e)