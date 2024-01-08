import sys
import threading
import logging

logging.basicConfig(
    format="[%(asctime)s | %(name)s] %(message)s"
)


class MSRLogger:
    """
    Singleton pattern to globally instantiate multiple loggers
    """
    logger_instances = {}
    lock = threading.Lock()

    @staticmethod
    def get_logger(logger_name: str) -> logging.Logger:
        """
        Creates a new logger instance and stores it in logger_instances for repetitive access
        """
        with MSRLogger.lock:
            if logger_name not in MSRLogger.logger_instances.keys():
                logger = logging.getLogger(logger_name)
                logger.setLevel(logging.DEBUG)
                MSRLogger.logger_instances[logger_name] = logger
            return MSRLogger.logger_instances[logger_name]
