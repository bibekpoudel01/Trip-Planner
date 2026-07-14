import logging

import os
from datetime import datetime
LOG_FILE=f"{datetime.now().strftime('%m_%d-%Y_%H-%M-%S')}.log"#log file name with timestamp
logs_path=os.path.join(os.getcwd(),"logs",LOG_FILE)#logs directory path
os.makedirs(logs_path,exist_ok=True)#create logs directory if it doesn't exist
LOG_FILE_PATH=os.path.join(logs_path,LOG_FILE)#full path to the log file


logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO#log level set to INFO

)
def get_logger(name):
    logger=logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger