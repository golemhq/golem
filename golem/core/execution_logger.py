"""Create the logger object"""
import logging
import os


DEBUG_LOG_FILENAME = 'execution_debug.log'
INFO_LOG_FILENAME = 'execution_info.log'


def _get_log_level(log_level_string):
    log_level = ''
    if log_level_string == 'DEBUG':
        log_level = logging.DEBUG
    elif log_level_string == 'INFO':
        log_level = logging.INFO
    elif log_level_string == 'WARNING':
        log_level = logging.WARNING
    elif log_level_string == 'ERROR':
        log_level = logging.ERROR
    elif log_level_string == 'CRITICAL':
        log_level = logging.CRITICAL
    else:
        raise Exception('Log level {} is invalid'.format(log_level_string))
    return log_level


def get_logger(log_directory=None, console_log_level=None, log_all_events=False):
    logger = None
    if log_all_events:
        logger = logging.getLogger()
    else:
        logger = logging.getLogger('golem')
    logger.setLevel(logging.DEBUG)
    # add stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(_get_log_level(console_log_level))
    stream_format_string = '%(asctime)s %(levelname)s %(message)s'
    stream_formatter = logging.Formatter(stream_format_string, "%H:%M:%S")
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)
    # add file handler
    if log_directory:
        # debug file log
        log_file = os.path.join(log_directory, DEBUG_LOG_FILENAME)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format_string = '%(asctime)s %(name)s %(levelname)s %(message)s'
        file_formatter = logging.Formatter(file_format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        # info file log
        log_file = os.path.join(log_directory, INFO_LOG_FILENAME)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_format_string = '%(asctime)s.%(msecs)03d %(levelname)s %(message)s'
        file_formatter = logging.Formatter(file_format_string, "%H:%M:%S")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    return logger

