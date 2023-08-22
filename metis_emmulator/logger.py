import logging


def make_logger(name: str, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('{%(asctime)s} - [%(name)s] - (%(levelname)s) : %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
