import warnings

from src.DataAcquisition.GitHubAPIService.RESTService.GitHubRESTWrapper import GitHubRESTWrapper
from src.Utility.Utility import dict_search


class CommitsRoot:
    """
    Generates metadata for each commit (author/ committer/ comments)
    """

    def __init__(self, github_rest_api: GitHubRESTWrapper):
        self._github_rest_api = github_rest_api

    def get_data(self):
        for commit in self._github_rest_api.get_commits():
            commit_hash = commit.sha

            # Edge case
            if commit_hash is None:
                continue

            # Collect necessary author and committer data
            commit_result = {
                "hash": dict_search(commit._rawData, ["sha"], ""),
                "authoredAt": dict_search(commit._rawData, ["commit", "author", "date"], ""),
                "author": None if dict_search(commit._rawData, ["author"], None) is None else {
                    "id": dict_search(commit._rawData, ["author", "node_id"], ""),
                    "login": dict_search(commit._rawData, ["author", "login"], ""),
                    "name": dict_search(commit._rawData, ["author", "name"], ""),
                    "email": dict_search(commit._rawData, ["author", "email"], ""),
                },
                "committedAt": dict_search(commit._rawData, ["commit", "committer", "date"], ""),
                "committer": None if dict_search(commit._rawData, ["committer"], None) is None else {
                    "id": dict_search(commit._rawData, ["committer", "node_id"], ""),
                    "login": dict_search(commit._rawData, ["committer", "login"], ""),
                    "name": dict_search(commit._rawData, ["committer", "name"], ""),
                    "email": dict_search(commit._rawData, ["committer", "email"], "")
                }
            }
            # Load all commit comments if there is at least one
            commit_comments = []
            comment_count = dict_search(commit._rawData, ["commit", "comment_count"], -1)
            if comment_count > 0:
                for commit_comment in self._github_rest_api.get_commit_comments(commit):
                    commit_comments.append({
                        "id": dict_search(commit_comment._rawData, ["node_id"], ""),
                        "body": dict_search(commit_comment._rawData, ["body"], ""),
                        "path": dict_search(commit_comment._rawData, ["path"], ""),
                        "position": dict_search(commit_comment._rawData, ["position"], -1),
                        "line": dict_search(commit_comment._rawData, ["line"], -1),
                        "createdAt": dict_search(commit_comment._rawData, ["created_at"], ""),
                        "user": None if dict_search(commit_comment._rawData, ["user"], None) is None else {
                            "id": dict_search(commit_comment._rawData, ["user", "node_id"], ""),
                            "login": dict_search(commit_comment._rawData, ["user", "login"], "")
                        }
                    })
            # Update commit results to include the commit comments
            commit_result.update({
                "commitComments": commit_comments
            })

            yield commit_result
