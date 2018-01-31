import logging, datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
	def add_fields(self, log_record, record, message_dict):
		super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
		if not log_record.get("timestamp"):
			now = datetime.utcnow().strftime("%Y-%02m-%02dT%02H:%02M:%02S.%f")
			log_record["timestamp"] = now
		if log_record.get("level"):
			log_record["level"] = log_record["level"].upper()
		else:
			log_record["level"] = record.levelname

# System logger
systemLogFormat = '%(asctime)-15s: %(message)s'
systemLogPath = format("logs/%s_system.log" % ("a2zfranz",))
systemLogger = logging.getLogger("powertoken.system")
systemLogger.setLevel(logging.INFO)
systemLoggerFileHandler = logging.FileHandler(systemLogPath)
systemLoggerFileHandler.setLevel(logging.INFO)
systemLoggerFileHandler.setFormatter(CustomJsonFormatter('(timestamp) (level) (name) (message)'))
systemLogger.addHandler(systemLoggerFileHandler)
		
# Output logger
outputLogFormat = '%(asctime)s, %(message)s,'
outputLogPath = format("logs/%s_output.log" % ("a2zfranz",))
outputLogger = logging.getLogger("powertoken.output")
outputLogger.setLevel(logging.INFO)
outputLoggerFileHandler = logging.FileHandler(outputLogPath)
outputLoggerFileHandler.setLevel(logging.INFO)
outputLoggerFileHandler.setFormatter(CustomJsonFormatter('(timestamp) (level) (name) (message)'))
outputLogger.addHandler(systemLoggerFileHandler)