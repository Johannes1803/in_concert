"""Example main.py relying on class and class audit logger."""
import atexit
import logging.config
import sys

import yaml
from named_loggers_base import AuditedClass


class Car(AuditedClass):
    """Dummy class logging sth."""

    def drive(self):
        self.audit.debug("Oil needs to be changed soon")
        self.audit.info("Starting to drive.")


class Main:
    """Wrapper around main"""

    @staticmethod
    def run() -> int:
        """
        Run main application, return 0 exit status on success

        :return: exit status 0
        """
        car = Car()
        car.drive()
        return 0


if __name__ == "__main__":
    # Logging setup
    with open("logging_config.yaml", "r") as f:
        logging_config = yaml.safe_load(f)
    logging.config.dictConfig(logging_config)
    atexit.register(logging.shutdown)
    log = logging.getLogger("main")
    log.info("Starting")

    # wrap main in try except block to ensure all possible errors are logged
    try:
        application = Main()
        status = application.run()
    except Exception as e:
        logging.exception(e)
        status = 2
    sys.exit(status)
