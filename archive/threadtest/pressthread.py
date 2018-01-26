import threading, time

class PressThead (threading.Thread):
	def __init__(self, threadId, name):
		threading.Thread.__init__(self)
		self.threadId = threadId
		self.name = name
		self.daemon = True

	def run(self):
		while True:
			print("Would be polling WEconnect...")
			time.sleep(60)