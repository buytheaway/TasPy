import logging

FMT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATEFMT = "%H:%M:%S"

def setup_logging(level=logging.INFO):
    logging.basicConfig(level=level, format=FMT, datefmt=DATEFMT)