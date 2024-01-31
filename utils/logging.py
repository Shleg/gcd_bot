# logging_config.py
import logging


def setup_logging():
    logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")

