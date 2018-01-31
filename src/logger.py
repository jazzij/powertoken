import logging

# System logger
systemLogFormat = '%(asctime)-15s: %(message)s'
systemLogPath = format("logs/%s_system.log" % ("a2zfranz",))
systemLogger = logging.getLogger("powertoken.system")
systemLogger.setLevel(logging.INFO)
systemLoggerFileHandler = logging.FileHandler(self.systemLogPath)
systemLoggerFileHandler.setLevel(logging.INFO)
systemLoggerFileHandler.setFormatter(logging.Formatter(systemLogFormat))
systemLogger.addHandler(systemLoggerFileHandler)
		
# Output logger
outputLogFormat = '%(asctime)s, %(message)s,'
outputLogPath = format("logs/%s_output.log" % ("a2zfranz",))
outputLogger = logging.getLogger("powertoken.output")
outputLogger.setLevel(logging.INFO)
outputLoggerFileHandler = logging.FileHandler(self.systemLogPath)
outputLoggerFileHandler.setLevel(logging.INFO)
outputLoggerFileHandler.setFormatter(logging.Formatter(systemLogFormat))
outputLogger.addHandler(systemLoggerFileHandler)