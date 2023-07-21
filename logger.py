import logging

def get_logger(app_name='sdmx_istat', path = './aggiornamento_db.log'):

    # Gets or creates a logger
    logger = logging.getLogger(app_name)  

    # set log level
    logger.setLevel(logging.DEBUG)

    # define file handler and set formatter
    file_handler = logging.FileHandler(path)
    formatter    = logging.Formatter('[%(asctime)s]:[%(name)s]:[%(funcName)s]:[%(levelname)s]: %(message)s')
    file_handler.setFormatter(formatter)

    # add file handler to logger
    logger.addHandler(file_handler)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger
