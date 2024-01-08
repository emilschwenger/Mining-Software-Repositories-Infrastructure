import time
from typing import List
from src.DataAcquisition.GitHubAPIService.TokenManager import TokenManager
from src.RepositoryCollector import RepositoryCollector
from src.DataAcquisition.GitHubAPIService.GitHubClientFactory import GitHubClientFactory
from queue import Queue
from src.Utility.Logger import MSRLogger
from src.Utility.Utility import read_config, read_repo_list, extract_repo_url_owner_and_name


class CollectionThreadPool:
    """
    The CollectionThreadPool is responsible for starting and stopping RepositoryCollector threads. It allows
    for a maximum number of number_threads to run at the same time. This variable is configurable in the
    MSRInfrastructure/config.json file.
    """

    def __init__(self):
        # Initialize logger
        self.logger = MSRLogger.get_logger(self.__class__.__name__)
        # Load configuration file and content
        config = read_config()
        # Load config value if this execution deploys in docker or is local
        self.deploy = config.get("deploy", None)
        if self.deploy is None:
            self.logger.exception("Configuration file corruption, please define .deploy.")
        # Load config value for the maximum number of concurrent threads
        self.number_threads = config.get("threads", None)
        if self.number_threads is None:
            self.logger.exception("Configuration file corruption, please define .threads.")
        # Load repository list and put repository owner and name into queue
        self.repository_list = read_repo_list()
        if len(self.repository_list) <= 0:
            self.logger.exception("Define at least one or more repositories to collect.")
        self.repository_queue = Queue()
        for repo_url in self.repository_list:
            if repo_url is not None and len(repo_url) > 18:
                self.repository_queue.put(extract_repo_url_owner_and_name(repo_url))
        # Load config value if the database should store commit file content
        self.commit_content = config.get("commit_content", None)
        if self.commit_content is None:
            self.logger.exception("Configuration file corruption, please define .commit_content.")
        # Load config value if the database should store pull request file content
        self.pull_request_file_content = config.get("pull_request_file_content", None)
        if self.pull_request_file_content is None:
            self.logger.exception("Configuration file corruption, please define .pull_request_file_content.")
        # Create a new instance if TokenManager
        self.token_manager = TokenManager()
        # Initialize thread pool
        self.thread_pool: List[RepositoryCollector] = []

    def start(self):
        """
        Starts the thread pool loop that checks every 15 seconds if a RepositoryCollector finished and if this is the
        case starts a new instance with the next repository in line. This method never starts more the number_threads
        threads at the same time.
        """
        while self.repository_queue.qsize() > 0 or len(self.thread_pool) > 0:
            if len(self.thread_pool) < self.number_threads and self.repository_queue.qsize() > 0:
                # If the number of thread in the pool is smaller than the maximum number of threads and the repository
                # list at least contains one new repository initialize a new thread
                next_repository = self.repository_queue.get()
                self.logger.info(f"Initializing new thread for repository {next_repository}")
                self._start_instance(next_repository[0], next_repository[1])
            else:
                # If the maximum number of threads is currently or the repository list is empty
                # wait 15 seconds and try again
                time.sleep(15)
                # Remove all stopped threads from the thread pool
                updated_thread_pool = []
                for thread in self.thread_pool:
                    if not thread.is_alive():
                        thread.join()
                    else:
                        updated_thread_pool.append(thread)
                self.thread_pool = updated_thread_pool

    def _start_instance(self, repo_owner: str, repo_name: str):
        """
        Starts a new instance of RepositoryCollector to collect the next repository in a dedicated thread.
        """
        # Start the thread
        collector = RepositoryCollector(
            repository_owner=repo_owner,
            repository_name=repo_name,
            github_client_factory=GitHubClientFactory(repo_owner, repo_name, self.token_manager),
            deploy=self.deploy,
            commit_data=self.commit_content,
            pull_request_data=self.pull_request_file_content
        )
        collector.start()
        # Append thread to the thread pool
        self.thread_pool.append(collector)
