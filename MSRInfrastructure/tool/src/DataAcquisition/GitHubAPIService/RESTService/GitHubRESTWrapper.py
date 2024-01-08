import threading
import requests
from datetime import datetime
from src.DataAcquisition.GitHubAPIService.TokenManager import TokenManager
from typing import Union
from github import Github, Repository, Auth, RateLimitExceededException, NamedUser, Label, PaginatedList, Issue, \
    PullRequest, PullRequestComment, PullRequestReview, IssueEvent, IssueComment, File, Workflow, WorkflowRun, \
    Commit
from src.DataAcquisition.GitHubAPIService.GitHubAPIType import GITHUB_API_TYPE
from src.Utility.Logger import MSRLogger


class GitHubRESTWrapper:
    """
    A wrapper for PyGitHub to collect data from the GitHub REST API. REST services such as CommitQuery|IssueQuery|
    PullRequestQuery utilize this wrapper to access the GitHub REST API.
    """

    def __init__(self, token_manager: TokenManager, repo_owner: str, repo_name: str):
        self.lock = threading.Lock()
        self.logger = MSRLogger.get_logger(self.__class__.__name__)
        self.token_manager = token_manager
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo = repo_owner + "/" + repo_name
        self.github: Union[Github, None] = None
        self.client: Union[Repository, None] = None
        self.token = ""
        self.running: bool = False
        self._MIN_TOKEN_COUNT = 50

    def start_client(self):
        """
        Starts the client and handles administrative tasks.
        """
        # Reset token
        self.token = ""
        # Create new client and acquire token
        github, client = self._create_client()
        self.github: Github = github
        self.client: Repository = client
        self.running = True

    def _create_client(self) -> (Github, Repository):
        """
        Create a new client to query the GitHub REST API
        :return: client: Github, Repository
        """
        try:
            self.token = self.token_manager.get_token(GITHUB_API_TYPE.REST_API)
            authentication = Auth.Token(self.token)
            github = Github(auth=authentication, per_page=100, seconds_between_requests=0.1)
            client = github.get_repo(self.repo)
            return github, client
        except RateLimitExceededException:
            self._token_limit_exceeded()

    def _token_limit_exceeded(self):
        """
        Executed if token limit is exceeded. Replaces the old client with a new one.
        """
        self.logger.info(f"{self.repo} Rate limit reached -> changing token")
        # Destroy old client
        self.destroy_client(rate_limit_exceeded=True)
        # Create a new client
        self.start_client()

    def destroy_client(self, rate_limit_exceeded: bool = False):
        """
        Destroys the old PyGithub client.
        :param: rate_limit_exceeded if the client gets destroyed because the rate limit is exceeded
        """
        # Update the running value
        if not self.running:
            self.logger.exception(f"{self.repo} Destroying client failed -> client is not running")
        self.running = False
        # Return token
        if rate_limit_exceeded:
            reset_datetime = datetime.utcfromtimestamp(self.github.rate_limiting_resettime)
            self.token_manager.return_token(self.token, GITHUB_API_TYPE.REST_API, reset_datetime)
            self.logger.info(f"{self.repo} Client with token: {self.token} successfully destroyed with reuse_time {reset_datetime}")
        else:
            self.token_manager.return_token(self.token, GITHUB_API_TYPE.REST_API)
            self.logger.info(f"{self.repo} Client with token: {self.token} successfully destroyed with immediate reuse")
        # Close client
        self.github.close()
        self.github = None
        self.client = None

    def send_custom_request(self, endpoint: str) -> dict:
        """
        This method sends a custom rest request while checking for token rate limit. Use with caution.
        :param endpoint: url_endpoint e.g., /facebook/react/dependency-graph/sbom
        :return: The REST request result as dictionary
        """
        # Check if the client is running
        if not self.running:
            self.logger.exception(f"{self.repo} Request failed -> client is not running")
        # Destroys the old client and creates a new one if token count is below self._MIN_TOKEN_COUNT
        if self.get_remaining_token() <= self._MIN_TOKEN_COUNT:
            self._token_limit_exceeded()
        # Execute custom
        custom_request = requests.get(
            url="https://api.github.com/repos/" + self.repo_owner + "/" + self.repo_name + endpoint,
            headers={
                "X-GitHub-Api-Version": "2022-11-28",
                "Authorization": "Bearer " + self.token,
                "Accept": "application/vnd.github+json"
            }
        )
        return custom_request.json()

    def get_remaining_token(self):
        """
        Remaining token point for the current token.
        :return: int
        """
        return self.github.rate_limiting[0]

    def _get_next_result(self, iterator):
        """
        Handle token exceptions during for loops.
        :param iterator: Iterator of PaginatedList
        """
        try:
            next_result = next(iterator)
            # Destroys the old client and creates a new one if token count is below self._MIN_TOKEN_COUNT
            if self.get_remaining_token() <= self._MIN_TOKEN_COUNT:
                self._token_limit_exceeded()
            return next_result
        except RateLimitExceededException:
            self._token_limit_exceeded()
            return self._get_next_result(iterator)
        except StopIteration:
            raise StopIteration()

    def get_user_by_id(self, user_id: int) -> NamedUser:
        try:
            return self.github.get_user_by_id(user_id)
        except RateLimitExceededException:
            self._token_limit_exceeded()
            return self.get_user_by_id(user_id)

    def get_pull_request(self, request_number: int) -> PullRequest:
        try:
            return self.client.get_pull(request_number)
        except RateLimitExceededException:
            self._token_limit_exceeded()
            return self.get_pull_request(request_number)

    # Below are various generator methods to retrieve data with PyGithub from the GitHub REST API iteratively
    def get_branches(self) -> PaginatedList:
        branches = self.client.get_branches().__iter__()
        while True:
            try:
                yield self._get_next_result(branches)
            except StopIteration:
                return

    def get_commits(self):
        commits = self.client.get_commits().__iter__()
        while True:
            try:
                yield self._get_next_result(commits)
            except StopIteration:
                return

    def get_commit_comments(self, commit: Commit):
        commit_comments = commit.get_comments().__iter__()
        while True:
            try:
                yield self._get_next_result(commit_comments)
            except StopIteration:
                return

    def get_pull_requests(self) -> PullRequest:
        pull_requests = self.client.get_pulls(state="all").__iter__()
        while True:
            try:
                yield self._get_next_result(pull_requests)
            except StopIteration:
                return

    def get_repository_pull_request_file_actions(self, pull_request: PullRequest):
        file_actions = pull_request.get_files().__iter__()
        while True:
            try:
                yield self._get_next_result(file_actions)
            except StopIteration:
                break

    def get_pull_request_comments(self, pull_request: PullRequest) -> IssueComment:
        pull_request_comments = pull_request.get_issue_comments().__iter__()
        while True:
            try:
                yield self._get_next_result(pull_request_comments)
            except StopIteration:
                break

    def get_pull_request_timeline(self, pull_request: PullRequest) -> IssueEvent:
        pull_request_events = pull_request.get_issue_events().__iter__()
        while True:
            try:
                yield self._get_next_result(pull_request_events)
            except StopIteration:
                break

    def get_pull_request_files(self, pull_request: PullRequest) -> File:
        pull_request_files = pull_request.get_files().__iter__()
        while True:
            try:
                yield self._get_next_result(pull_request_files)
            except StopIteration:
                break

    def get_pull_request_reviews(self, pull_request: PullRequest) -> PullRequestReview:
        pull_request_reviews = pull_request.get_reviews().__iter__()
        while True:
            try:
                yield self._get_next_result(pull_request_reviews)
            except StopIteration:
                break

    def get_pull_request_review_comments(self, pull_request: PullRequest) -> PullRequestComment:
        pull_request_review_comments = pull_request.get_comments().__iter__()
        while True:
            try:
                yield self._get_next_result(pull_request_review_comments)
            except StopIteration:
                break

    def get_pull_request_labels(self, pull_request: PullRequest) -> Label:
        pull_request_labels = pull_request.get_labels().__iter__()
        while True:
            try:
                yield self._get_next_result(pull_request_labels)
            except StopIteration:
                break

    def get_issue(self, issue_number: int):
        try:
            return self.client.get_issue(issue_number)
        except RateLimitExceededException:
            self._token_limit_exceeded()
            return self.get_issue(issue_number)

    def get_issue_labels(self, issue: Issue) -> Label:
        issue_labels = issue.get_labels().__iter__()
        while True:
            try:
                yield self._get_next_result(issue_labels)
            except StopIteration:
                break

    def get_issue_events(self, issue: Issue):
        issue_events = issue.get_events().__iter__()
        while True:
            try:
                yield self._get_next_result(issue_events)
            except StopIteration:
                break

    def get_issue_comments(self, issue: Issue) -> IssueComment:
        issue_comments = issue.get_comments().__iter__()
        while True:
            try:
                yield self._get_next_result(issue_comments)
            except StopIteration:
                break

    def get_workflows(self):
        workflows = self.client.get_workflows().__iter__()
        while True:
            try:
                yield self._get_next_result(workflows)
            except StopIteration:
                break

    def get_workflow_runs(self, workflow: Workflow) -> WorkflowRun:
        workflow_runs = workflow.get_runs().__iter__()
        while True:
            try:
                yield self._get_next_result(workflow_runs)
            except StopIteration:
                break

