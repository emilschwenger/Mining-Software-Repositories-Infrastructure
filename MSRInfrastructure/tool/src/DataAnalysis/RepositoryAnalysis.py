from neo4j import GraphDatabase, Driver
from typing import Optional
import src.RepositoryCollector as RepositoryCollector
from src.Utility.Logger import MSRLogger
from src.Utility.Utility import read_config

class RepositoryAnalysis:
    """
    RepositoryAnalysis provides a list of cypher queries to calculate software repository metrics.
    NOTE: The queries in this class do not consume results. For consuming the results it is necessary to write a method
    that extracts the query results before a session ends --> Inside of the with session() as s: scope
    """

    def __init__(self, repo: RepositoryCollector):
        self.logger = MSRLogger.get_logger(self.__class__.__name__)
        self.config = read_config()
        self.project_id = repo.get_project_id()
        self.IP = "neo4j1" if repo.is_deployment() else "localhost"
        self.URI = f"bolt://{self.IP}:7687"
        self.db: Optional[Driver] = None
        self.repo_owner = repo.get_repo_owner()
        self.repo_name = repo.get_repo_name()
        self.repo = repo

    def list_projects(self):
        """
        Returns a list of all projects that are currently in the database
        """
        with self.db.session() as t:
            projects = t.run(f"""
                    MATCH (p:Project)
                    RETURN p
                    """)
            project_list = []
            for project in projects:
                project_id = project[0].get("id")
                project_name = project[0].get("name")
                project_list.append((project_id, project_name))
            return project_list

    def connect(self):
        self.db = GraphDatabase.driver(uri=self.URI, auth=(self.config.get("db_username"), self.config.get("db_password")))
        self.logger.info(f"{self.repo_owner}/{self.repo_name} Connection to Neo4J established")

    def disconnect(self):
        self.db.close()

    def run_query(self, query: str):
        """TODO: If one wants to consume query results, it is necessary to consume them within the session context"""
        with self.db.session() as t:
            return t.run(query)

    def get_commits_on_monthly_basis(self, repo_id: str):
        """
        The number of Commits since project start on a monthly basis
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (p:Project {{id: '{repo_id}'}})-[:HAS_COMMIT_MONTH]->(pcm:ProjectCommitMonth)<-[:COMMIT_IN_MONTH]-(c:Commit)<-[:CONTAINS_COMMIT]-(b:Branch {{name: 'origin/HEAD'}})
        RETURN pcm.year as year, pcm.month as month, COUNT(c)
        """)

    def get_commits_count_by_author_descending(self, repo_id: str):
        """
        For every user calculate the number of commits a user authored and sort results in descending order
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (p:Project {{id: '{repo_id}'}})-[:HAS_COMMIT_MONTH]->(pcm:ProjectCommitMonth)<-[:COMMIT_IN_MONTH]-(c:Commit),
        (c)<-[:AUTHOR_OF]-(u:User),
        (c)<-[:CONTAINS_COMMIT]-(b:Branch {{name: 'origin/HEAD'}})
        RETURN u.login as author_login, COUNT(c) as commit_count
        ORDER BY commit_count DESC
        """)

    def get_avg_issue_close_time_per_month(self, repo_id: str):
        """
        The avg close time for Issues on a monthly basis
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (p:Project {{id: '{repo_id}'}})-[:HAS_ISSUE_MONTH]->(im:ProjectIssueMonth)<-[:ISSUE_IN_MONTH]-(i:Issue),
        (i)<-[closes_issue:CLOSES_ISSUE]-(:User),
        (i)<-[creates_issue:CREATES_ISSUE]-(:User)
        WITH im.year as year, im.month as month, duration.between(creates_issue.createdAt, closes_issue.createdAt) as open_duration
        RETURN year, month, AVG(open_duration), COUNT(open_duration)
        """)

    def get_avg_pull_request_close_time_per_month(self, repo_id):
        """
        The avg close time for PullRequests on a monthly basis
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (p:Project {{id: '{repo_id}'}})-[:HAS_PULL_REQUEST_MONTH]->(prm:ProjectPullRequestMonth)<-[:PULL_REQUEST_IN_MONTH]-(pr:PullRequest),
        (pr)-[:HAS_EVENT]->(:PullRequestEvent {{__typename: 'ClosedEvent'}})<-[cpre:CREATES_PULL_REQUEST_EVENT]-(:User),
        (pr)<-[cpr:CREATES_PULL_REQUEST]-(prc:User)
        WITH prm.year as year, prm.month as month, duration.between(cpr.createdAt, cpre.createdAt) as open_duration
        RETURN year, month, AVG(open_duration)
        """)

    def get_new_issue_author_count_per_month(self, repo_id: str):
        """
        The number of new Issue authors on a monthly basis
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (:Project {{id: '{repo_id}'}})-[im:HAS_ISSUE_MONTH]->(:ProjectIssueMonth)<-[:ISSUE_IN_MONTH]-(i:Issue)<-[:CREATES_ISSUE]-(u:User)
        WITH im.date_month as date_month, COLLECT(DISTINCT u.login) as usernames
        CALL {{
            WITH date_month, usernames
            MATCH  (:Project {{id: '{repo_id}'}})-[s_im:HAS_ISSUE_MONTH]->(:ProjectIssueMonth)<-[:ISSUE_IN_MONTH]-(s_i:Issue)<-[:CREATES_ISSUE]-(s_u:User)
            WHERE ((s_im.date_month.year * 12) + s_im.date_month.month) < ((date_month.year * 12) + date_month.month)
            RETURN COLLECT(DISTINCT s_u.login) as previous_usernames
        }}
        RETURN date_month, SIZE(apoc.coll.subtract(usernames, previous_usernames)) as new_authors_count
        """)

    def get_new_pull_request_author_count_per_month(self, repo_id: str):
        """
        The number of new PullRequest authors on a monthly basis
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (:Project {{id: '{repo_id}'}})-[prm:HAS_PULL_REQUEST_MONTH]->(:ProjectPullRequestMonth)<-[:PULL_REQUEST_IN_MONTH]-(pr:PullRequest)<-[:CREATES_PULL_REQUEST]-(u:User)
        WITH prm.date_month as date_month, COLLECT(DISTINCT u.login) as usernames
        CALL {{
            WITH date_month, usernames
            MATCH (:Project {{id: '{repo_id}'}})-[s_prm:HAS_PULL_REQUEST_MONTH]->(:ProjectPullRequestMonth)<-[:PULL_REQUEST_IN_MONTH]-(:PullRequest)<-[:CREATES_PULL_REQUEST]-(s_u:User)
            WHERE ((s_prm.date_month.year * 12) + s_prm.date_month.month) < ((date_month.year * 12) + date_month.month)
            RETURN COLLECT(DISTINCT s_u.login) as previous_usernames
        }}
        RETURN date_month, SIZE(apoc.coll.subtract(usernames, previous_usernames)) as new_authors_count
        """)

    def get_label_issue_and_pull_request_count(self, repo_id: str):
        """
        For every repository label retrieve the number of PullRequests and Issues with that label
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (:Project {{id: '{repo_id}'}})-[:PROJECT_HAS_LABEL]->(l:Label)
        CALL {{
            WITH l
            MATCH (l)<-[ihl:ISSUE_HAS_LABEL]-(:Issue)
            RETURN COUNT(ihl) as issue_label_count
        }}
        CALL {{
            WITH l
            MATCH (l)<-[prhl:PULL_REQUEST_HAS_LABEL]-(:PullRequest)
            RETURN COUNT(prhl) as pull_request_label_count
        }}
        RETURN l.name, issue_label_count, pull_request_label_count
        """)

    def get_avg_issue_response_time_per_month(self, repo_id: str):
        """
        The avg response time for Issues on monthly basis
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (:Project {{id: '{repo_id}'}})-[:HAS_ISSUE_MONTH]->(pim:ProjectIssueMonth)<-[:ISSUE_IN_MONTH]-(i:Issue)<-[ci:CREATES_ISSUE]-(:User)
        CALL {{
            WITH i, ci
            MATCH (i)<-[coi:COMMENTS_ON_ISSUE]-(:User)
            RETURN MIN(duration.between(ci.createdAt, coi.createdAt)) as response_time
        }}
        RETURN pim.year as year, pim.month as month, AVG(response_time) as avg_response_time
        """)

    def get_avg_pull_request_merge_time_per_month(self, repo_id: str):
        """
        The avg merge time for PullRequests on a monthly basis
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (p:Project {{id: '{repo_id}'}})-[:HAS_PULL_REQUEST_MONTH]->(prm:ProjectPullRequestMonth)<-[:PULL_REQUEST_IN_MONTH]-(pr:PullRequest),
        (pr)-[:HAS_EVENT]->(:PullRequestEvent {{__typename: 'MergedEvent'}})<-[cpre:CREATES_PULL_REQUEST_EVENT]-(:User),
        (pr)<-[cpr:CREATES_PULL_REQUEST]-(:User)
        WITH prm.year as year, prm.month as month, duration.between(cpr.createdAt, cpre.createdAt) as merge_duration
        RETURN year, month, AVG(merge_duration) as avg_merge_duration
        """)

    def get_closed_issues_per_month(self, repo_id: str):
        """
        Count the current amount of closed and open Issues on a monthly basis
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (:Project {{id: '{repo_id}'}})-[him:HAS_ISSUE_MONTH]->(:ProjectIssueMonth)
        WITH him.date_month as date_month
        CALL {{
             WITH date_month
             MATCH (:Project {{id: '{repo_id}'}})-[s__him:HAS_ISSUE_MONTH]->(:ProjectIssueMonth)<-[:ISSUE_IN_MONTH]-(s__i:Issue)
             WHERE s__him.date_month <= date_month
             WITH DISTINCT(s__i)
             RETURN COUNT(s__i) as all_issues
        }}
        CALL {{
            WITH date_month
            MATCH (:Project {{id: '{repo_id}'}})-[s_him:HAS_ISSUE_MONTH]->(:ProjectIssueMonth)<-[:ISSUE_IN_MONTH]-(s_i:Issue {{state: 'CLOSED'}}) 
            OPTIONAL MATCH (s_i)<-[s_ci:CLOSES_ISSUE]-(:User)
            WITH s_i, CASE WHEN (s_ci is not null) and (((s_ci.createdAt.year * 12) + s_ci.createdAt.month) <= ((date_month.year * 12) + date_month.month)) THEN True WHEN (s_ci is null) and s_him.date_month <= date_month THEN True ELSE False END as in_time
            WHERE in_time
            WITH DISTINCT(s_i)
            RETURN COUNT(s_i) as closed_issues
        }}
        RETURN date_month, all_issues - closed_issues as opened_issues, closed_issues
        """)
        # ORDER BY date_month DESC

    def get_closed_pull_requests_per_month(self, repo_id: str):
        """
        Count the current amount of closed and open PullRequests on a monthly basis
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (:Project {{id: '{repo_id}'}})-[hprm:HAS_PULL_REQUEST_MONTH]->(:ProjectPullRequestMonth)
        WITH hprm.date_month as date_month
        CALL {{
            WITH date_month
            MATCH (:Project {{id: '{repo_id}'}})-[s__hprm:HAS_PULL_REQUEST_MONTH]->(:ProjectPullRequestMonth)<-[:PULL_REQUEST_IN_MONTH]-(s__pr:PullRequest)
            WHERE ((s__hprm.date_month.year * 12) + s__hprm.date_month.month) <= ((date_month.year * 12) + date_month.month)
            RETURN COUNT(s__pr) as all_pull_requests
        }}
        CALL {{
            WITH date_month 
            MATCH (:Project {{id: '{repo_id}'}})-[hprm:HAS_PULL_REQUEST_MONTH]->(:ProjectPullRequestMonth)<-[:PULL_REQUEST_IN_MONTH]-(s_pr:PullRequest)
            OPTIONAL MATCH (s_pr)-[:HAS_EVENT]->(s_pre:PullRequestEvent {{__typename: 'ClosedEvent'}})<-[s_cpre:CREATES_PULL_REQUEST_EVENT]-(:User)
            WITH CASE 
                WHEN s_pre is not null and s_pr.state <> 'OPEN' and (((s_cpre.createdAt.year * 12) + s_cpre.createdAt.month) <= ((date_month.year * 12) + date_month.month)) THEN True
                WHEN s_pre is null and s_pr.state <> 'OPEN' and hprm.date_month <= date_month THEN True
                ELSE False End as is_closed, s_pr
            WITH DISTINCT(s_pr), is_closed
            WHERE is_closed
            RETURN COUNT(is_closed) as closed_pull_requests
        }}
        RETURN date_month, all_pull_requests - closed_pull_requests as open_pull_requests, closed_pull_requests
        """)
        # ORDER BY date_month DESC

    def get_issue_author_comment_count(self, repo_id: str):
        """
        The total amount of Issue comments for each commenting user
        :return:
        """
        return self.run_query(f"""
        MATCH (:Project {{id: '{repo_id}'}})-[:HAS_ISSUE_MONTH]->(:ProjectIssueMonth)<-[:ISSUE_IN_MONTH]-(i:Issue)<-[:COMMENTS_ON_ISSUE]-(u:User)
        RETURN u.login, COUNT(i) as comment_count
        """)

    def get_discussion_author_comment_count(self, repo_id: str):
        """
        Count the number of Comment for each DiscussionComment Author
        :param repo_id:
        :return:
        """
        return self.run_query(f"""
        MATCH (p:Project {{id: '{repo_id}'}})-[:PROJECT_HAS_DISCUSSION]->(d:Discussion)-[:HAS_COMMENT]->(dc:DiscussionComment)<-[:CREATES_DISCUSSION_COMMENT]-(u:User)
        RETURN u.login, COUNT(dc) as comment_count
        """)
