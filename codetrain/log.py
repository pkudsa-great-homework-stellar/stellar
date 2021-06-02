import logging
import time
import os


def print_log(log_stack: list, basepath: str, name: str, lock):
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n')

    handler = logging.FileHandler(
        os.path.join(basepath, f"log_{name}.txt"))
    handler.setLevel(level=logging.INFO)
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    logger.addHandler(handler)
    logger.addHandler(console)
    while True:
        lock.acquire()
        while log_stack:
            logger.info(log_stack.pop(0))
        lock.release()
        time.sleep(4)
