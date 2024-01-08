from abc import ABC, abstractmethod
from src.Utility.Utility import dict_search


class GraphQLSecondaryRootNode(ABC):
    """
    Generates a Query tree to fetch information from the GraphQL API.
    1. Handles cursor advancement up to the first layer automatically by parsing query results.
    2. Generates a list of partially collected nodes that could not be completely collected with GraphQL.
    """

    def __init__(self):
        self._first_execution = True  # Indicates if this is the first time the query this class generates executes
        self._has_next_page: bool = True  # Indicates if this classes node type has a next page e.g., if the
        # IssueRootNode inherits this class and _has_next_page is true it means that there are more issues to collect
        self._cursor: str = ""  # The cursor is necessary to store as the GraphQL API requires it in the next request
        # to continue collecting more data where the last query stopped

    @abstractmethod
    def get_query(self) -> str:
        """
        Method to return the next query
        :return: str
        """
        pass

    def parse_result(self, last_query_result: dict) -> []:
        """
        Parses results and return a list of node numbers that are only partially collected
        """
        # Update hasNextPage, cursor, and is_first_execution
        has_next_page = dict_search(last_query_result, ["pageInfo", "hasNextPage"], None)
        cursor = dict_search(last_query_result, ["pageInfo", "endCursor"], None)
        self.set_has_next_page(has_next_page)
        self.set_cursor(cursor)
        self.set_first_execution(False)
        # Generate a list of nodes that are only partially collected
        partially_collected_values = []
        for pull_request in last_query_result.get("nodes", []):
            if self._contains_has_next_page(pull_request):
                if "number" in pull_request:
                    partially_collected_values.append(pull_request["number"])
        return partially_collected_values

    def _contains_has_next_page(self, value) -> bool:
        """
        Recursively searches for a dictionary containing the hasNextPage key with a value of True
        :param: value: Value can be of type list or dictionary.
        """
        if isinstance(value, list):
            for list_entry in value:
                if self._contains_has_next_page(list_entry):
                    return True
        elif isinstance(value, dict):
            for dict_key, dict_value in value.items():
                if dict_key == "hasNextPage" and dict_value:
                    return True
                if self._contains_has_next_page(dict_value):
                    return True
        return False

    def has_next_page(self) -> bool:
        return self._has_next_page

    def set_has_next_page(self, value: bool):
        self._has_next_page = value

    def set_cursor(self, cursor: str):
        self._cursor = cursor

    def get_cursor(self) -> str:
        return self._cursor

    def is_first_execution(self):
        return self._first_execution

    def set_first_execution(self, first_execution: bool):
        self._first_execution = first_execution


class PullRequestRootNodeGraphQL(GraphQLSecondaryRootNode):
    """
    Construct the pull request query
    """

    def get_query(self) -> str:
        query_arguments = "first: 15"
        if not self.is_first_execution():
            query_arguments += ", after:" + '\"' + self.get_cursor() + '\"'
        return """
        pullRequests({query_arguments}) !
          pageInfo !
            hasNextPage
            endCursor
          ?
          nodes !
            id
            number
            mergedAt
            title
            body
            isDraft
            locked
            createdAt
            activeLockReason
            state
            baseRepository !
              id
              url
            ?
            headRepository !
              id
              url
            ?
            headRefOid
            headRefName
            baseRefOid
            baseRefName
            author !
              ... on User !
                id
                login
                email
                name
              ?
            ?
            reviewRequests(first: 100) !
              nodes !
                requestedReviewer !
                  ... on User !
                    id
                    name
                    login
                    email
                  ?
                ?
              ?
            ?
            milestone !
              id
              number
              title
              description
              dueOn
              createdAt
              closedAt
              progressPercentage
              creator !
                ... on User !
                  id
                  login
                  email
                  name
                ?
              ?
            ?
            assignees(first: 10) !
              nodes !
                id
                login
                email
                name
              ?
              pageInfo !
                hasNextPage
                endCursor
              ?
            ?
            comments(first: 50) !
              nodes !
                id
                body
                createdAt
                author !
                  ... on User !
                    id
                    login
                    email
                    name
                  ?
                ?
              ?
              pageInfo !
                hasNextPage
                endCursor
              ?
            ?
            timelineItems(first: 100, itemTypes: [MERGED_EVENT, CLOSED_EVENT]) !
              nodes !
                __typename
                ... on MergedEvent !
                    id
                    createdAt
                    actor !
                    ... on User !
                      id
                      login
                      email
                      name
                    ?
                  ?
                  commit !
                    oid
                  ?
                ?
                ... on ClosedEvent !
                  id
                  createdAt
                  actor !
                    ... on User !
                      id
                      login
                      email
                      name
                    ?
                  ?
                ?
              ?
              pageInfo !
                hasNextPage
                endCursor
              ?
            ?
            reviews(first: 100) !
              nodes !
                id
                state
                body
                submittedAt
                createdAt
                author !
                  ... on User !
                    id
                    login
                    email
                    name
                  ?
                ?
                commit !
                  oid
                ?
                comments(first: 100) !
                  nodes !
                    id
                    body
                    createdAt
                    diffHunk
                    createdAt
                    path
                    startLine
                    originalStartLine
                    line
                    originalLine
                    author !
                      ... on User !
                        id
                        login
                        email
                        name
                      ?
                    ?
                    replyTo !
                      id
                    ?
                    commit !
                      oid
                    ?
                    originalCommit !
                      oid
                    ?
                  ?
                  pageInfo !
                    hasNextPage
                    endCursor
                  ?
                ?
              ?
              pageInfo !
                hasNextPage
                endCursor
              ?
            ?
            labels(first: 10) !
              nodes !
                id
                name
              ?
              pageInfo !
                hasNextPage
                endCursor
              ?
            ?
            files(first: 50) !
              nodes !
                additions
                deletions
                path
                changeType
              ?
              pageInfo !
                hasNextPage
                endCursor
              ?
            ?
          ?
        ?
        """.format(query_arguments=query_arguments)


class IssueRootNodeGraphQL(GraphQLSecondaryRootNode):
    """
    Construct the issue query
    """

    def get_query(self) -> str:
        query_arguments = "first: 30"
        if not self.is_first_execution():
            query_arguments += ", after:" + '\"' + self.get_cursor() + '\"'
        return """
        issues({query_arguments}) !
          nodes !
            id
            number
            title
            body
            state
            createdAt
            milestone !
              id
              number
              title
              description
              dueOn
              createdAt
              closedAt
              progressPercentage
              state
              creator !
                ... on User !
                  id
                  login
                  email
                  name
                ?
              ?
            ?
            timelineItems(first: 100, itemTypes: [CLOSED_EVENT, CONVERTED_TO_DISCUSSION_EVENT]) !
              nodes !
                __typename
                ... on ClosedEvent !
                  id
                  createdAt
                  actor !
                    ... on User !
                      id
                      login
                      email
                      name
                    ?
                  ?
                ?
                ... on ConvertedToDiscussionEvent !
                  id
                ?
              ?
              pageInfo !
                endCursor
                hasNextPage
              ?
            ?
            author !
              ... on User !
                id
                login
                email
                name
              ?
            ?
            assignees(first: 20) !
              nodes !
                id
                login
                email
                name
              ?
              pageInfo !
                endCursor
                hasNextPage
              ?
            ?
            labels(first: 50) !
              nodes !
                id
                name
              ?
              pageInfo !
                endCursor
                hasNextPage
              ?
            ?
            comments(first: 100) !
              nodes !
                id
                createdAt
                body
                author !
                  ... on User !
                    id
                    login
                    email
                    name
                  ?
                ?
              ?
              pageInfo !
                endCursor
                hasNextPage
              ?
            ?
          ?
          pageInfo !
            endCursor
            hasNextPage
          ?
        ?
        """.format(query_arguments=query_arguments)


class DiscussionRootNodeGraphQL(GraphQLSecondaryRootNode):
    """
    Construct the discussion query
    """

    def get_query(self) -> str:
        query_arguments = "first: 30"
        if not self.is_first_execution():
            query_arguments += ", after:" + '\"' + self.get_cursor() + '\"'
        return """
        discussions({query_arguments}) !
          nodes !
            id
            number
            title
            closed
            closedAt
            createdAt
            upvoteCount
            body
            category !
              name
            ?
            author !
              ... on User !
                id
                login
                email
                name
              ?
            ?
            labels(first: 50) !
              nodes !
                id
                name
              ?
              pageInfo !
                endCursor
                hasNextPage
              ?
            ?
            comments(first: 30) !
              nodes !
                id
                body
                isAnswer
                createdAt
                author !
                  ... on User !
                    id
                    login
                    email
                    name
                  ?
                ?
                replies(first: 100) !
                    nodes !
                      id
                      body
                      createdAt
                      author !
                        ... on User !
                          id
                          name
                          login
                          email
                        ?
                      ?
                    ?
                    pageInfo !
                      hasNextPage
                      endCursor
                    ?
                ?
              ?
              pageInfo !
                endCursor
                hasNextPage
              ?
            ?
          ?
          pageInfo !
            endCursor
            hasNextPage
          ?
        ?
        """.format(query_arguments=query_arguments)


class ReleaseRootNodeGraphQL(GraphQLSecondaryRootNode):
    """
    Construct the release query
    """

    def get_query(self) -> str:
        query_arguments = "first: 100"
        if not self.is_first_execution():
            query_arguments += ", after:" + '\"' + self.get_cursor() + '\"'
        return """
        releases({query_arguments}) !
          nodes !
            id
            name
            publishedAt
            createdAt
            author !
              id
              login
              email
              name
            ?
            tagCommit !
              oid
            ?
          ?
          pageInfo !
            endCursor
            hasNextPage
          ?
        ?
        """.format(query_arguments=query_arguments)


class LabelRootNodeGraphQL(GraphQLSecondaryRootNode):
    """
    Construct the label query
    """

    def get_query(self) -> str:
        query_arguments = "first: 100"
        if not self.is_first_execution():
            query_arguments += ", after:" + '\"' + self.get_cursor() + '\"'
        return """
        labels({query_arguments}) !
          nodes !
            id
            name
          ?
          pageInfo !
            endCursor
            hasNextPage
          ?
        ?
        """.format(query_arguments=query_arguments)


class MilestoneRootNodeGraphQL(GraphQLSecondaryRootNode):
    """
    Construct the milestone query
    NOTE: This is not in use as milestones are automatically collected with issues and pull requests
    """

    def get_query(self) -> str:
        query_arguments = "first: 30"
        if not self.is_first_execution():
            query_arguments += ", after:" + '\"' + self.get_cursor() + '\"'
        return """
        milestones({query_arguments}) !
          nodes !
            id
            number
            title
            description
            dueOn
            createdAt
            closedAt
            progressPercentage
            state
            issues(first: 100) !
              nodes !
                id
              ?
              pageInfo !
                endCursor
                hasNextPage
              ?
            ?
            pullRequests(first: 100) !
              nodes !
                id
              ?
              pageInfo !
                endCursor
                hasNextPage
              ?
            ?
            creator !
              ... on User !
                id
                login
                email
                name
              ?
            ?
          ?
          pageInfo !
            endCursor
            hasNextPage
          ?
        ?
        """.format(query_arguments=query_arguments)


class WatcherRootNodeGraphQL(GraphQLSecondaryRootNode):
    """
    Construct the watchers query
    """

    def get_query(self) -> str:
        query_arguments = "first: 50"
        if not self.is_first_execution():
            query_arguments += ", after:" + '\"' + self.get_cursor() + '\"'
        return """
        watchers({query_arguments}) !
          nodes !
            id
            login
            email
            name
          ?
          pageInfo !
            endCursor
            hasNextPage
          ?
        ?
        """.format(query_arguments=query_arguments)


class StargazerRootNodeGraphQL(GraphQLSecondaryRootNode):
    """
    Construct the stargazers query
    """

    def get_query(self) -> str:
        query_arguments = "first: 50"
        if not self.is_first_execution():
            query_arguments += ", after:" + '\"' + self.get_cursor() + '\"'
        return """
        stargazers({query_arguments}) !
          nodes !
            id
            login
            email
            name
          ?
          pageInfo !
            endCursor
            hasNextPage
          ?
        ?
        """.format(query_arguments=query_arguments)


class GraphQLRootNode:
    """
    GraphQLRootNode is capable of dynamically generating GraphQL queries to collect Labels|Releases|
    Discussions|Issues|PullRequests|Watchers|Stargazers. After generating a query it takes in the query result to
    parse cursors for retrieving the next results. Parsing cursors is only possible on the first layer (the nodes named
    in advance).
    """
    def __init__(self, activate: [str], exception: [str]):
        """
        :param activate: A list of node names to generate queries for.
        :param exception: A list of node names that cannot keep the query running
        """
        self.children: dict = {}
        self.exception: [str] = exception
        if "labels" in activate:
            self.children.update({"labels": LabelRootNodeGraphQL()})
        if "releases" in activate:
            self.children.update({"releases": ReleaseRootNodeGraphQL()})
        if "discussions" in activate:
            self.children.update({"discussions": DiscussionRootNodeGraphQL()})
        if "issues" in activate:
            self.children.update({"issues": IssueRootNodeGraphQL()})
        if "pullRequests" in activate:
            self.children.update({"pullRequests": PullRequestRootNodeGraphQL()})
        if "watchers" in activate:
            self.children.update({"watchers": WatcherRootNodeGraphQL()})
        if "stargazers" in activate:
            self.children.update({"stargazers": StargazerRootNodeGraphQL()})

    def get_query_content(self) -> (str, bool):
        """
        After parsing a query result, this method is capable of returning the next query content. THis content contains
        new cursors that have been discovered when aprsing the latest query results
        :return: (query, query_is_finished)
        """
        # Add secondary root nodes to the query that still delivers new data
        query_array = [child.get_query() for child in self.children.values() if child.has_next_page()]
        query_array_keys = [child_key for child_key, child_value in self.children.items() if
                            child_value.has_next_page()]
        query_array_except = [child_key for child_key in query_array_keys if child_key not in self.exception]
        # Format query and return as string
        query = "\n".join(query_array)
        return query.replace("!", "{").replace("?", "}"), len(query_array_except) == 0

    def parse_result(self, last_query_result: dict) -> dict:
        """
        Parses previous query results to update cursors and has_next_page values.
        :return: A dictionary with lists of partially collected nodes.
        Partially collected node = Nodes below the first layer that have the has_next_page set to true
        """
        partially_collected_nodes = {}
        # Task 1 & 2
        for result_key in last_query_result["repository"]:
            if result_key in self.children:
                partially_collected_nodes[result_key] = self.children[result_key].parse_result(last_query_result["repository"][result_key].copy())
        return partially_collected_nodes
