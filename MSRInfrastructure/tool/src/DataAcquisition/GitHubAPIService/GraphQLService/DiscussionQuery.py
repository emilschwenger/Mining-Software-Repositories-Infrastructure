from src.Utility.Utility import dict_search

class DiscussionRoot:
    """
    Generates queries to collect all discussion comments for a specific Discussion.
    NOTE: Only collects up to 100 DiscussionComment replies
    """
    def __init__(self, number: int):
        # Default initialization
        self._number: int = number
        self._is_first_execution: bool = True
        self._cursor: str = ""
        self._has_next_page: bool = True

    def is_finished(self) -> bool:
        """
        Returns True if the next query delivers new results.
        :return: bool
        """
        return not self._has_next_page

    def get_query_content(self) -> (str, bool):
        """
        Generates the discussion query based on a template/ updated cursor/ and discussion number
        :return:
        """
        query_arguments = "first: 100"
        if not self._is_first_execution:
            query_arguments += ", after:" + '\"' + self._cursor + '\"'
        return """
        discussion(number: {number}) !
            id
            labels(first: 50) !
              nodes !
                id
                name
              ?
            ?
            category !
              name
            ?
            comments({query_arguments}) !
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
        """.format(number=self._number, query_arguments=query_arguments), self.is_finished()

    def parse_result(self, query_result: dict):
        """
        Parses previous query results to get necessary parameters for query construction.
        :param query_result: previous query results
        """
        self._is_first_execution = False
        self._cursor = dict_search(query_result, ["repository", "discussion", "comments", "pageInfo", "endCursor"], None)
        self._has_next_page = dict_search(query_result, ["repository", "discussion", "comments", "pageInfo", "hasNextPage"], False)

