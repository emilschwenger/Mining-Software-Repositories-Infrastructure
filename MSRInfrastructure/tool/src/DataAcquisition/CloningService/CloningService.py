import shutil

import magic
from git import Repo, Commit
from src.Utility.Logger import MSRLogger

import src.RepositoryCollector as RepositoryCollector


class CloningService:
    """
    This service is responsible for offering data retrieval by cloning a repository into the local file system.
    """

    def __init__(self, repo: RepositoryCollector, content: bool):
        # Initialize default values
        self.logger = MSRLogger.get_logger(self.__class__.__name__)
        self.content: bool = content
        self.repo: RepositoryCollector = repo
        self.repo_url = "https://github.com/" + self.repo.get_repo_owner() + "/" + self.repo.get_repo_name() + ".git"
        self.clone_path = "/repo_clone/" if self.repo.is_deployment() else "./dev_data/repo_clone/"
        self.clone_repo_path = self.clone_path + self.repo.get_repo_owner() + "-" + self.repo.get_repo_name()
        # Initialize the cloning process
        self.repository: Repo = self.repository_factory()

    def get_file_actions(self):
        """
        Generator to retrieve all file changes in a repository.
        """
        for child, parent in self.get_commit_parents():
            for diff in parent.diff(child, create_patch=True):
                if diff is None:
                    continue
                # Process diff
                difference = "" if diff.diff is None else diff.diff.decode(errors="replace")
                line_begin_character = [line[0] if len(line) > 0 else "" for line in difference.splitlines()]
                # Determine change type
                change_type = "M"
                if diff.new_file:
                    change_type = "A"
                elif diff.deleted_file:
                    change_type = "D"
                elif diff.renamed_file:
                    change_type = "R"
                mime_before = "unknown"
                path_before = ""
                try:
                    path_before = diff.a_path if diff.a_path is not None else ""
                except Exception as e:
                    pass
                file_sha_before = ""
                file_size_before = -1
                if diff.a_blob is not None:
                    try:
                        file_sha_before = diff.a_blob.hexsha if diff.a_blob.hexsha is not None else ""
                        file_size_before = diff.a_blob.size if diff.a_blob.size is not None else -1
                        mime_before = magic.from_buffer(diff.a_blob.data_stream.read(), mime=True)
                    except Exception as e:
                        continue
                mime_after = "unknown"
                path_after = ""
                try:
                    path_after = diff.b_path if diff.b_path is not None else ""
                except Exception as e:
                    pass
                file_sha_after = ""
                file_size_after = -1
                if diff.b_blob is not None:
                    try:
                        file_sha_after = diff.b_blob.hexsha if diff.b_blob.hexsha is not None else ""
                        file_size_after = diff.b_blob.size if diff.b_blob.size is not None else -1
                        mime_after = magic.from_buffer(diff.b_blob.data_stream.read(), mime=True)
                    except Exception as e:
                        continue
                yield {
                    "childCommitSha": child.hexsha,
                    "parentCommitSha": parent.hexsha,
                    "changeType": change_type,
                    "mimeTypeBefore": mime_before,
                    "pathBefore": path_before,
                    "fileShaBefore": file_sha_before,
                    "fileSizeBefore": file_size_before,
                    "mimeTypeAfter": mime_after,
                    "pathAfter": path_after,
                    "fileShaAfter": file_sha_after,
                    "fileSizeAfter": file_size_after,
                    "copiedFile": diff.copied_file,
                    "renamedFile": diff.renamed_file,
                    "newFile": diff.new_file,
                    "deletedFile": diff.deleted_file,
                    "diff": "" if not self.content or not CloningService.is_mime_type_relevant(mime_after) else difference,
                    "addedLines": line_begin_character.count("+"),
                    "deletedLines": line_begin_character.count("-"),
                }

    def get_branch_commits(self):
        """
        Generator to retrieve all commits for all remote branches in the repository.
        :return: (remote_branch_name: str, head_commit_sha: str, branch_commits: [])
        """
        for remote_branch in self.get_remote_branches():
            head_commit_sha = ""
            first_iteration = True
            branch_commits = []
            for commit in self.repository.iter_commits(remote_branch):
                if first_iteration:
                    head_commit_sha = commit.hexsha
                    first_iteration = False
                branch_commits.append(commit.hexsha)
            yield remote_branch, head_commit_sha, branch_commits

    def get_commit_parents(self) -> [(Commit, Commit)]:
        """
        Retrieve parent and child commits.
        :return: [child_hash: Commit, parent_hash: Commit]
        """
        for commit in self.get_commits_objects():
            for parent_commit in commit.parents:
                yield commit, parent_commit

    def get_commits_objects(self):
        """
        Generator to return for each commit of a repository.
        :return: dict
        """
        commit_sha_set = set()
        for remote_branch in self.get_remote_branches():
            for commit in self.repository.iter_commits(remote_branch):
                if commit in commit_sha_set:
                    continue
                commit_sha_set.add(commit)
                yield commit

    def get_remote_branches(self):
        """
        Generator for all remote branches of a repository.
        :return: string
        """
        for branch in self.repository.references:
            if branch.is_remote():
                yield branch

    def repository_factory(self) -> Repo:
        self.logger.info(f"Cloning repository from {self.repo_url}")
        return Repo.clone_from(self.repo_url, self.clone_repo_path)

    def clean_up(self):
        """
        Deletes the cloned repository and all its content
        """
        shutil.rmtree(path=self.clone_repo_path)

    @staticmethod
    def is_mime_type_relevant(mime_type: str) -> bool:
        """
        Determines if the given mime-type is relevant to collect content based blacklisting.
        :return: bool
        """
        if mime_type is None:
            return False
        elif mime_type.startswith("image/"):
            return False
        elif mime_type.startswith("audio/"):
            return False
        elif mime_type.startswith("video/"):
            return False
        elif mime_type.startswith("model/"):
            return False
        elif mime_type.startswith("chemical/"):
            return False
        elif mime_type.startswith("application/vnd"):
            return False
        elif mime_type.startswith("application/octet-stream"):
            return False
        # TODO: Add more mime types that are irrelevant to collect
        return True
