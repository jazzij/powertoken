import logging
from pythonjsonlogger import jsonlogger

# System logger
systemLogFormat = '%(asctime)-15s: %(message)s'
systemLogPath = format("logs/%s_system.log" % ("a2zfranz",))
systemLogger = logging.getLogger("powertoken.system")
systemLogger.setLevel(logging.INFO)
systemLoggerFileHandler = logging.FileHandler(systemLogPath)
systemLoggerFileHandler.setLevel(logging.INFO)
systemLoggerFileHandler.setFormatter(jsonlogger.JsonFormatter())
systemLogger.addHandler(systemLoggerFileHandler)
		
# Output logger
outputLogFormat = '%(asctime)s, %(message)s,'
outputLogPath = format("logs/%s_output.log" % ("a2zfranz",))
outputLogger = logging.getLogger("powertoken.output")
outputLogger.setLevel(logging.INFO)
outputLoggerFileHandler = logging.FileHandler(outputLogPath)
outputLoggerFileHandler.setLevel(logging.INFO)
outputLoggerFileHandler.setFormatter(jsonlogger.JsonFormatter())
outputLogger.addHandler(systemLoggerFileHandler)