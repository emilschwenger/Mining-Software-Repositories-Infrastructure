import threading
from typing import Optional

from src.Utility.Logger import MSRLogger
from src.Utility.Utility import dict_search

from src.DataAnalysis.RepositoryAnalysis import RepositoryAnalysis
from src.DataInsertion.RepositoryInsertion import RepositoryInsertion

from src.DataAcquisition.GitHubAPIService.GitHubClientFactory import GitHubClientFactory
from src.DataAcquisition.GitHubCollector import GraphQLCollector, RESTCollector
from src.DataAcquisition.GitHubCollector import DATA_TREE
from src.DataProcessing.ProjectProcessor import ProjectProcessorRoot
from src.PreprocessorStorage.PreprocessorStorageInterface import PreprocessorStorageInterface
from src.DataProcessing.IssueProcessor import IssueProcessorRoot
from src.DataProcessing.WorkflowProcessor import WorkflowProcessorRoot
from src.DataProcessing.BranchProcessor import BranchProcessorRoot
from src.DataProcessing.CommitProcessor import CommitContentProcessorRoot, CommitMetaProcessorRoot
from src.DataProcessing.ReleaseProcessor import ReleaseProcessorRoot
from src.DataProcessing.DependencyProcessor import DependencyProcessorRoot
from src.DataProcessing.StarsProcessor import StarsProcessorRoot
from src.DataProcessing.WatchesProcessor import WatchesProcessorRoot
from src.DataProcessing.LabelProcessor import LabelProcessorRoot
from src.DataProcessing.DiscussionProcessor import DiscussionProcessorRoot
from src.DataProcessing.PullRequestFileProcessor import PullRequestFileProcessorRoot
from src.DataProcessing.PullRequestProcessor import PullRequestProcessorRoot
from src.DataProcessing.CommitFileProcessor import CommitFileProcessorRoot
from src.DataAcquisition.CloningService.CloningService import CloningService


class RepositoryCollector(threading.Thread):
    """
    RepositoryCollector is responsible for collecting all information concerning a specific repository
    """
    def __init__(self, repository_owner, repository_name, github_client_factory, commit_data=False,
                 pull_request_data=False, deploy=False):
        super().__init__()
        self.logger = MSRLogger.get_logger(self.__class__.__name__)  # Logger
        self._repository_owner: str = repository_owner  # Repository owner
        self._repository_name: str = repository_name  # Repository name
        self._repo = self._repository_owner + "/" + self._repository_name  # Repository full name
        self._deploy: bool = deploy  # If this execution runs in docker or the IDE
        self._commit_data: bool = commit_data  # If commit file content is collected
        self._pull_request_data: bool = pull_request_data  # If pull request file content is collected
        self._preprocessor_storage: PreprocessorStorageInterface = PreprocessorStorageInterface(
            repository_owner,
            repository_name,
            deploy
        )  # Initialize file CSV and in memory storage
        self._github_client_factory: GitHubClientFactory = github_client_factory  # Client factory to get API wrapper
        self._graph_ql_collector: Optional[GraphQLCollector] = None  # GraphQL collector to get GitHub GraphQL API data
        self._rest_collector: Optional[RESTCollector] = None  # REST collector to get GitHub REST API data
        self._cloning_service: Optional[CloningService, None] = None  # Initialize cloning service
        self._project_id = ""  # Node ID of the current project -> Defined in the ProjectProcessor

    def run(self):
        self.logger.info(f"Initializing repository {self._repo}")
        # Delete old repository CSV files
        self.logger.info(f"Clear repository CSV files {self._repo}")
        self.get_preprocessor_storage().delete_all_files()
        # Collect data and store it into CSV files
        self.logger.info(f"Start collecting {self._repo}")
        self.collect()
        # Destroy GitHub clients
        self.logger.info(f"Destroying GitHub clients {self._repo}")
        self._github_client_factory.destroy_client()
        # Write the data into the database
        self.start_insertion()
        # Delete cloned repository
        self.logger.info(f"Clear cloned repository {self._repo}")
        self._cloning_service.clean_up()
        # Delete repository CSV files
        self.logger.info(f"Clear repository CSV files {self._repo}")
        self.get_preprocessor_storage().delete_all_files()

    def start_insertion(self):
        """
        Instantiates a new RepositoryInsertion object and starts repository insertion into the database
        """
        insertion = RepositoryInsertion(self)
        return insertion.start()

    def collect(self):
        """
        Starts the complete repository collection by cloning into the local file system, REST API, and GraphQL API
        """
        # Clone the repository
        self._cloning_service = CloningService(self, content=self._commit_data)
        # GraphQL Initialization
        self._graph_ql_collector = GraphQLCollector(graphql_client=self.get_client_factory().get_graphql_api())
        # Collect and process project data
        self.process_project()
        # Collect and process commit data -> By cloning
        self.process_commits()
        # Collect and process file action and file data -> By cloning
        self.process_file_actions()
        # Collect and process branches -> By cloning
        self.process_branches()
        # Collect and process issues with graphql partially --> GraphQL
        partially_collected_issues = self.partially_process_issues()
        # self.logger.info(f"Partially collected issues for {self._repository_owner}/{self._repository_name}: {partially_collected_issues}")

        # Collect and process pull requests with graphql partially --> GraphQL
        partially_collected_pull_requests = self.partially_process_pull_requests()
        # self.logger.debug(f"Partially collected pull requests for {self._repository_owner}/{self._repository_name}: {partially_collected_pull_requests}")

        # Collect Discussion Data -> GraphQL
        self.process_discussions()
        # Collect and process stargazers and watchers -> GraphQL
        self.process_stargazers_watchers()
        # Collect and process releases -> GraphQL
        self.process_releases()
        # Collect and process labels -> GraphQL
        self.process_labels()
        # REST API Initialization
        self._rest_collector = RESTCollector(rest_client=self.get_client_factory().get_rest_api())
        # Collect and process remaining issues -> REST API
        self.process_remaining_issues(partially_collected_issues)
        # Collect and process remaining pull requests -> REST API
        self.process_remaining_pull_requests(partially_collected_pull_requests)
        # Collect and process dependency data
        self.process_dependencies()
        # Collect and process commit metadata (author/ committer)
        self.process_commit_meta()
        # Depending on whether PR file content is needed, data is collected previously with the GraphQL or REST API
        if self.isCollectPullRequestFileContent():
            # Collect and process pull request file changes
            self.process_pull_request_files()
        # Collect and process workflows
        self.process_workflows()

    def process_labels(self):
        self.logger.info(f"{self._repo} Start collecting - Labels")
        # Labels (Complete) -> GraphQL
        for query_result, partially_collected_nodes in self._graph_ql_collector.get([DATA_TREE.LABEL], []):
            labels_data = query_result.get("repository", {}).get("labels", None)
            if labels_data is not None:
                label_processor = LabelProcessorRoot(self, labels_data)
                label_processor.process()

    def process_watchers(self, query_result):
        watcher_data = query_result.get("repository", {}).get("watchers", None)
        if watcher_data is not None:
            watcher_processor = WatchesProcessorRoot(self, watcher_data)
            watcher_processor.process()

    def process_stargazers(self, query_result):
        stargazer_data = query_result.get("repository", {}).get("stargazers", None)
        if stargazer_data is not None:
            stargazer_processor = StarsProcessorRoot(self, stargazer_data)
            stargazer_processor.process()

    def process_discussions(self):
        self.logger.info(f"{self._repo} Start collecting - Discussions")
        for query_result, partially_collected_nodes in self._graph_ql_collector.get([DATA_TREE.DISCUSSION], []):
            # Get discussions data from graphql response
            primary_discussions_data = query_result["repository"]["discussions"]
            # Processing discussions (Write to CSV and in memory)
            primary_discussion_processor = DiscussionProcessorRoot(self, primary_discussions_data)
            primary_discussion_processor.process()
            # Execute follow up queries to retrieve partially collected discussion
            if "discussions" in partially_collected_nodes.keys():
                partially_collected_discussion = partially_collected_nodes["discussions"]
                # Loop over all partially collected discussion numbers
                for discussion_number in partially_collected_discussion:
                    # Retrieve all discussion data
                    for secondary_discussion_data in self._graph_ql_collector.get_discussion(discussion_number):
                        discussion_content = dict_search(secondary_discussion_data, ["repository", "discussion"], None)
                        secondary_discussion_processor = DiscussionProcessorRoot(self, {
                            "nodes": [] if discussion_content is None else [discussion_content]
                        })
                        secondary_discussion_processor.process()

    def process_releases(self):
        self.logger.info(f"{self._repo} Start collecting - Releases")
        for query_result, partially_collected_nodes in self._graph_ql_collector.get([DATA_TREE.RELEASE], []):
            release_data = query_result.get("repository", {}).get("releases", [])
            release_processor = ReleaseProcessorRoot(self, release_data)
            release_processor.process()

    def process_commit_meta(self):
        self.logger.info(f"{self._repo} Start collecting - Commit metadata (author/committer/comments)")
        # Collect commit metadata (author, committer, commit comments) -> REST API
        for commit in self._rest_collector.get_commits():
            commit_processor = CommitMetaProcessorRoot(self, commit)
            commit_processor.process()

    def process_pull_request_files(self):
        self.logger.info(f"{self._repo} Start collecting - Pull request file")
        # Collect PullRequest file meta and patch data (EXTREMELY HIGH COSTS) -> REST API
        for pull_request_file_action in self._rest_collector.get_repository_pull_request_file_actions():
            pull_request_file_processor = PullRequestFileProcessorRoot(self, pull_request_file_action)
            pull_request_file_processor.process()

    def process_workflows(self):
        self.logger.info(f"{self._repo} Start collecting - Workflows")
        # Collect Workflow Data (Complete) -> REST API
        for workflow in self._rest_collector.get_workflows():
            workflow_processor = WorkflowProcessorRoot(self, workflow)
            workflow_processor.process()

    def process_commits(self):
        self.logger.info(f"{self._repo} Start collecting - Commit history")
        # Task: Collect Commit -> By cloning
        for commit in self._cloning_service.get_commits_objects():
            commit_processor = CommitContentProcessorRoot(self, {
                "commit": commit
            })
            commit_processor.process()

    def process_file_actions(self):
        self.logger.info(f"{self._repo} Start collecting - Commit file/ file actions")
        # Task: Collect FileAction, File -> By cloning
        for file_action in self._cloning_service.get_file_actions():
            file_and_file_action_processor = CommitFileProcessorRoot(self, file_action)
            file_and_file_action_processor.process()

    def process_branches(self):
        self.logger.info(f"{self._repo} Start collecting - Branches")
        # Task: Collect Branches -> By cloning
        for remote_branch_name, head_commit_sha, branch_commits in self._cloning_service.get_branch_commits():
            branch_processor = BranchProcessorRoot(self, {
                "branchName": remote_branch_name,
                "headCommitSha": head_commit_sha,
                "branchCommits": branch_commits
            })
            branch_processor.process()

    def process_dependencies(self):
        self.logger.info(f"{self._repo} Start collecting - Dependencies")
        # Collect Dependency Data -> REST API
        dependency_data = self._rest_collector.get_sbom()
        dependency_processor = DependencyProcessorRoot(self, dependency_data)
        dependency_processor.process()

    def process_stargazers_watchers(self):
        self.logger.info(f"{self._repo} Start collecting - Stargazers/Watchers")
        # Collect and process stargazers and watchers -> GraphQL
        for query_result, partially_collected_nodes in self._graph_ql_collector.get(
                [DATA_TREE.STARGAZER, DATA_TREE.WATCHER], []
        ):
            self.process_stargazers(query_result)
            self.process_watchers(query_result)

    def process_project(self):
        self.logger.info(f"{self._repo} Start collecting - Project")
        # Collect Project data --> GraphQL
        project_data = self._graph_ql_collector.get_project()
        project_processor = ProjectProcessorRoot(self, project_data)
        project_processor.process()

    def partially_process_issues(self):
        self.logger.info(f"{self._repo} Start collecting - Issues partial")
        # Collect Issue Data -> GraphQL
        partially_collected_issues = []
        for query_result, partially_collected_nodes in self._graph_ql_collector.get([DATA_TREE.ISSUE], []):
            # Get issue data from graphql response
            issue_data = query_result["repository"]["issues"]
            # Processing issues (Write to CSV and in memory)
            issue_processor = IssueProcessorRoot(self, issue_data)
            issue_processor.process()
            # Add partially collected node numbers to list
            if "issues" in partially_collected_nodes.keys():
                partially_collected_issues.extend(partially_collected_nodes["issues"])
        return partially_collected_issues.copy()

    def process_remaining_issues(self, partially_collected_issues: []):
        self.logger.info(f"{self._repo} Start collecting - Issues remaining")
        # Collect Issue Data -> REST API
        for query_result in self._rest_collector.get_issues(partially_collected_issues):
            issue_processor = IssueProcessorRoot(self, query_result)
            issue_processor.process()

    def partially_process_pull_requests(self):
        self.logger.info(f"{self._repo} Start collecting - Pull requests partial")
        # Collect Pull Request Data -> GraphQL
        partially_collected_pull_requests = []
        for query_result, partially_collected_nodes in self._graph_ql_collector.get([DATA_TREE.PULL_REQUEST], []):
            # Get pull request data from graphql response
            pull_request_data = query_result["repository"]["pullRequests"]
            # Processing pull requests (Write to CSV and in memory)
            pull_request_processor = PullRequestProcessorRoot(self, pull_request_data)
            pull_request_processor.process()
            # Add partially collected node numbers to list
            if "pullRequests" in partially_collected_nodes.keys():
                partially_collected_pull_requests.extend(partially_collected_nodes["pullRequests"])
        return partially_collected_pull_requests.copy()

    def process_remaining_pull_requests(self, partially_collected_pull_requests: []):
        self.logger.info(f"{self._repo} Start collecting - Pull requests remaining")
        # Collect PullRequest Data -> REST API
        for query_result in self._rest_collector.get_pull_requests(partially_collected_pull_requests):
            pull_request_processor = PullRequestProcessorRoot(self, query_result)
            pull_request_processor.process()

    def get_preprocessor_storage(self):
        return self._preprocessor_storage

    def get_client_factory(self):
        return self._github_client_factory

    def get_repo_name(self):
        return self._repository_name

    def get_repo_owner(self):
        return self._repository_owner

    def is_deployment(self):
        return self._deploy

    def get_project_id(self):
        return self._project_id

    def set_project_id(self, project_id: str):
        self._project_id = project_id

    def isCollectCommitContent(self):
        return self._commit_data

    def isCollectPullRequestFileContent(self):
        return self._pull_request_data
