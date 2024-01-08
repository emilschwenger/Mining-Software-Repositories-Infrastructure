from CollectionThreadPool import CollectionThreadPool
from src.Utility.Logger import MSRLogger

# Initializing logger
logger = MSRLogger.get_logger("Initializer")


def start_collection():
    """
    Starts the collection process by initializing a thread pool where each thread collects one repository. To configure
    this thread pool instance change the MSRInfrastructure/config.json file. To specify repositories to collect
    configure MSRInfrastructure/repository_list.txt
    """
    # Start the collection thread pool and start collection
    logger.info("Starting thread pool")
    thread_pool = CollectionThreadPool()
    thread_pool.start()


if __name__ == '__main__':
    start_collection()
