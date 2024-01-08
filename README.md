# Mining Software Repositories Infrastructure
## Run the infrastructure
### Clone the repository
```
git clone https://github.com/emilschwenger/MSRInfrastructure.git
cd MiningSoftwareRepositories-Infrastructure
```
### Edit configuration file and repository url list
**Add all repositories to collect to the MSRInfrastructure/repository_list.txt file (every line one repository URL)**

**Modify MSRInfrastructure/config.json**
1. Configure the maximum number of repositories to simultaneously collect = x
2. Add GitHub tokens with read:user and read:email permissions (estimated number of tokens are 2 * x)
3. Configure if the infrastructure collects commit file content and pull request file content 
### Run docker compose
Run ```docker-compose up -d``` to start the infrastructure.
## Access the collection results
Open the Neo4J Browser on http://localhost:7474/browser/ to explore the repository database and run queries.