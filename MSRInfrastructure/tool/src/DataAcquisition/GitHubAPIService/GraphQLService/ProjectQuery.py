class ProjectRoot:
    """
    Generates the GraphQL query to collect all project data.
    """

    def get_query_content(self) -> str:
        return """
        id
        url
        name
        description
        isArchived
        archivedAt
        isMirror
        mirrorUrl
        isLocked
        lockReason
        diskUsage
        visibility
        forkingAllowed
        hasWikiEnabled
        languages(first: 100) {
          nodes {
            name
          }
        }
        repositoryTopics(first: 100) {
          nodes {
            topic {
              name
            }
          }
        }
        licenseInfo {
          spdxId
        }
        owner {
          ... on User {
            name
            email
            login
            id
            createdAt
          }
          ... on Organization {
            orgName: name
            organizationEmail: email
            orgDesc: description
            orgLogin: login
            orgId: id
            createdAt
          }
        }
        """
