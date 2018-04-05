import os
import logging
from config import config

file_formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
)

console_formatter = logging.Formatter(
	'%(asctime)s %(levelname)s: %(message)s '
)

def configure_app_logger(logger):
    if not os.path.exists(config["LOGS_PATH"]):
        os.mkdir(config["LOGS_PATH"])

    # Setup Main Logger
    logger.setLevel(logging.INFO)
    file_handler = logging.handlers.RotatingFileHandler('logs/output.log', 
        maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def configure_celery_logger(celery_logger):
	if not os.path.exists(config["LOGS_PATH"]):
		os.mkdir(config["LOGS_PATH"])

	# Setup Celery Logger
	celery_logger.setLevel(logging.INFO)
	file_handler = logging.handlers.RotatingFileHandler('logs/celery.log', 
		maxBytes=1024 * 1024 * 100, backupCount=20)
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(file_formatter)
	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)
	console_handler.setFormatter(console_formatter)
	celery_logger.addHandler(file_handler)
	celery_logger.addHandler(console_handler)