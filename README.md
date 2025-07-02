# Schedule Builder Backend
## Development
Document the development policies that you used during sprint 5.
### Kanban Board
The project's Kanban board is organized in the following way:

| Board column | Entry criteria                                                                                                                                                                                                              |
|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Backlog      | A task is accepted to Backlog if:<br/>- it has been mentioned during the Customer Review,<br/>- the significance of the task has been discovered during the sprint.                                                         |
| Todo         | A task is accepted to Todo, if it is assigned to the current sprint and has to be completed by the deadline of the current sprint.                                                                                          |
| In Progress  | A task is accepted to In Progress, if the task is assigned to the current sprint and the task completion has already been started.                                                                                          |
| In Review    | A task is accepted to In Review, if the task was completed. This way, fellow team members can review the solution and provide useful feedback.                                                                              |
| Done         | A task is accepted to Done, if it satisfies the project's Definition of Done: the issue is finished (in terms of programming), deployed to the production, and is accordingly tested, thus verified in efficient execution. |
### Git Workflow
Specify which base workflow you adapted to your context (e.g., GitHub flow, Gitflow, etc). 

Explain / Define rules for: 
- Creating issues from the defined templates (link the 
earlier defined templates).
- Labelling issues. 
- Assigning issues to team members. 
- Creating, naming, merging branches; 
- Commit messages format; 
- Creating a pull request for an issue (link the earlier 
defined template). 
- Code reviews. 
- Merging pull requests. 
- Resolving issues.

Illustrate your git workflow using a Gitgraph diagram. 

### Secrets Management
Document your rules for secrets management (e.g. passwords or API keys). Mention where you store your secrets without revealing sensitive information.

### Automated Testing
Document: 
- Which tools you used for testing. 
- Which types of tests you implemented. 
- Where tests of each type are in the repository.

### Continuous Integration
For each CI workflow file: 
- Provide a link to that file. 
- Provide a list of static analysis tools and testing tools that you use in the CI part. For each tool in the list, briefly explain what you use it for. 
- Provide a link to where all CI workflow runs can be seen.

### Continuous Deployment
For each CD workflow file: 
- Provide a link to that file. 
- Provide a list of static analysis tools and testing tools that you use in the CD part. For each tool in the list, briefly explain what you use it for. 
- Provide a link to where all CD workflow runs can be seen.

## Quality
### Characteristic name
#### Sub-characteristic name
- Explain why that sub-characteristic is important. 
- Provide (a link to) one or more tests for that sub-characteristic in Quality Attribute Scenario format.

### Characteristic name
#### Sub-characteristic name
- Explain why that sub-characteristic is important. 
- Provide (a link to) one or more tests for that sub-characteristic in Quality Attribute Scenario format.

### Characteristic name
#### Sub-characteristic name
- Explain why that sub-characteristic is important. 
- Provide (a link to) one or more tests for that sub-characteristic in Quality Attribute Scenario format.

## Architecture

## Usage
Explain how to use your MVP v2. Provide information for access if needed, for example authentication credentials and so on. Make sure the customer and TA can launch/access and inspect your product after following the instructions in that section.

# OLD MATERIAL (TO BE REVAMPED)
## About

Schedule Builder is created as a tool for Innopolis University Department of Education (DoE) to assist the department in efficient creation of high-quality curriculums for bachelors, masters, and PhD students without any conflicts.

### Technologies
- [Python 3.12](https://www.python.org/downloads/) & [uv](https://docs.astral.sh/uv/)
- [FastAPI](https://fastapi.tiangolo.com/)
- Formatting and linting: [ruff](https://docs.astral.sh/ruff/), [black](https://black.readthedocs.io/en/stable/), [pre-commit](https://pre-commit.com/), [isort](https://github.com/PyCQA/isort)
- Deployment: [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/), [GitHub Actions](https://github.com/features/actions)

## Development

### Set up for development

1. Install [Python 3.12+](https://www.python.org/downloads/), [uv](https://docs.astral.sh/uv/), [Docker](https://docs.docker.com/engine/install/)
2. Install project dependencies with [uv](https://docs.astral.sh/uv/cli/#install).
   ```bash
   uv sync
   ```
3. Copy settings.example.yaml to settings.yaml and add token
   ```bash
   cp settings.example.yaml settings.yaml 
   ```
5. Start development server:
   ```bash
   uv run uvicorn src.presentation.app:app --port=8000 --host=0.0.0.0 --reload
   ```
   > Follow provided instructions if needed
6. Open in the browser: http://localhost:8000
   > The api will be reloaded when you edit the code

> [!IMPORTANT]
> For endpoints requiring authorization click "Authorize" button in Swagger UI

> [!TIP]
> Edit `settings.yaml` according to your needs, you can view schema in [settings.schema.yaml](settings.schema.yaml)

### Deployment

We use Docker with Docker Compose plugin to run the service on servers.

1. Copy the file with settings: `cp settings.example.yaml settings.yaml`
2. Change settings in the `settings.yaml` file according to your needs
   (check [settings.schema.yaml](settings.schema.yaml) for more info)
3. Install Docker with Docker Compose
4. Build && run docker container `docker compose up --build`

## How to update dependencies

1. Run `uv sync -U` to update all dependencies
2. Run `uv pip list --outdated` to check for outdated dependencies
