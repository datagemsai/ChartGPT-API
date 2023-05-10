import logging
import os
import time


def setup_logger(logger_name="chartbot", log_file_prefix="run") -> logging.Logger:
    directory = "logs/"

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Create a logger object
    file_name = f"logs/{log_file_prefix}_{time.strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger(logger_name)  # Use logger_name parameter

    # Set the logging level for the logger
    logger.setLevel(logging.INFO)

    # Create a file handler and set the logging level for the handler
    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(logging.INFO)

    # Create a formatter and add it to the file handler
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)
    return logger

