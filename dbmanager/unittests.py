from types import *
from sqlite3 import Row
import common
import usermanager
import logmanager

def run_tests():
	print(common._get_sqlite_timestamp())

	assert usermanager.create_users_if_dne()
	assert usermanager.insert_user("test_u")
	assert usermanager.user_exists("test_u")
	assert not usermanager.user_exists("blablabla")
	assert not usermanager.wc_info_filled("test_u")
	assert usermanager.update_wc_info("test_u", "daily", "11111", "3590sxeioel34ios34109")
	assert usermanager.wc_info_filled("test_u")
	assert not usermanager.fb_info_filled("test_u")
	assert usermanager.update_fb_info("test_u", "sl35902nej3390fh493wj394hlhk039")
	assert usermanager.fb_info_filled("test_u")
	assert not usermanager.get_users() is NoneType
	user = usermanager.get_user("test_u")
	assert isinstance(user, Row)
	assert not user["id"] is NoneType
	assert not user["username"] is NoneType
	assert not user["registered_on"] is NoneType
	assert not user["goal_period"] is NoneType 
	assert not user["wc_id"] is NoneType
	assert not user["wc_token"] is NoneType
	assert not user["fb_token"] is NoneType

	assert logmanager.create_logs_if_dne()
	assert logmanager.insert_log(user["id"], 0.5, 500000)
	assert not logmanager.get_logs() is NoneType
	assert not logmanager.get_logs("test_u") is NoneType
	assert not logmanager.get_logs(user_id=user["id"]) is NoneType
	assert not logmanager.get_logs("test_u", user["id"])