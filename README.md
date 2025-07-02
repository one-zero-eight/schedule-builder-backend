# Schedule Builder
## Development
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
In the project, we use a modified version of Gitflow for workflow management (e.g., the `main` branch is used for
general code storage, auxiliary branches are made for all Kanban board issues, 
hotfixes, and features implementation).

The workflow rules can be found below.

| Aspect                                     | Rules                                                                                                                                                                                                                                                                                                                                  |
|--------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Creating issues from the defined templates | Templates created within this week (bug report, technical task, user story templates are accessible [here](https://github.com/SWP2025/schedule-builder-backend/issues)) alongside with average issue creation procedures are used in the project.                                                                                      |
| Labelling issues                           | The opened issues are labelled with an according milestone for issue deadline, complexity evaluation in story points, and additional tasks for development purposes (ex.: `enhancement`).                                                                                                                                              |
| Assigning issues to team members           | Back-end tasks are assigned to the Back-end development team, and front-end tasks are assigned to the Front-end development team. Any tasks regarding the Product Backlog maintenance, documentation, and other administrative assignments are put on the Team Lead of the project.                                                    | 
| Creating, naming, merging branches         | A branch is created for each significant development issue and named after the issue (ex.: the issue is to update the `README.md` file, hence, the branch name is `update-readme`). The branch is made off `main` and is merged back to `main` after a pull request and code review with fellow team members.                          |
| Commit messages format                     | A conventional commit tags [system](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional) is employed alongside with average commit names for commits made through GitHub (e.g., verified). The commit messages should be laconic, concise, and explain the essence of the code changes. |
| Creating a pull request for an issue       | A template created within this week (accessible [here](https://github.com/SWP2025/schedule-builder-backend/issues)) alongside with average pull request creation is used in the project.                                                                                                                                               |
| Code reviews                               | Code reviews are conducted within any pull request. For code review, two or three team members are assigned to analyze the code and either give oral feedback without GitHub documentation (during meetings) or leave detailed written feedback in the comments of the pull request (during average development).                      |
| Merging pull requests                      | A pull request is merged (only to `main`) if an only if the code review for that pull request is passed, and CI/CD does not break under the composed changes.                                                                                                                                                                          |
| Resolving issues                           | An issue is marked done if and only if the branch assigned to the issue is merged by the pull request upon passing the code review. Issues are resolved within the timeline of the milestone they are assigned to. If the issue is not resolved within the time limit, then it is transferred to the next milestone.                   |

The GitGraph diagram of the workflow may be found below. 
![alt text](docs/development/mermaid_chart.png)

### Secrets Management
In our project, secrets are defined as any piece of information that is critical
for authorization in the project system. The key rule of secrets management is to
ensure the safety of information within the desired scope of storage. Secrets storages
for according fields may be found below.

| Secret             | Storage                                                                                                                                                                                                                     |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| API Token          | Local `settings.yaml` file                                                                                                                                                                                                  |
| DockerHub Username | GitHub Secrets                                                                                                                                                                                                              |
| DockerHub Token    | GitHub Secrets                                                                                                                                                                                                              |

### Automated Testing
**Q1:** Which tools were used for testing?

We used the following tools:
- `pytest` (because of the tool's widespreadness),
- `pytest_asyncio` (in order to set up testing fixtures).

**Q2:** Which types of tests have been implemented? 

We implemented **unit** and **integration** tests.

**Q3:** Where are the tests of each type stored in the repository?

Unit tests may be found [here](https://github.com/SWP2025/schedule-builder-backend/tree/main/tests/unit), whereas integration tests may be found [here](https://github.com/SWP2025/schedule-builder-backend/tree/main/tests/integration).

### Continuous Integration
Our Continuous Integration system comprises only **one** workflow file that can be accessed [here](https://github.com/SWP2025/schedule-builder-backend/blob/main/.github/workflows/test-and-build.yml).
Moreover, we used the following testing and static analysis tools in the system:
- `black` (widespread code linter),
- `isort` (inputs sorting),
- `pytest` (universal Python code testing library).

All CI workflow runs can be accessed [here](https://github.com/SWP2025/schedule-builder-backend/actions).

### Continuous Deployment
Our Continuous Deployment system comprises only **one** workflow file that can be accessed [here](https://github.com/SWP2025/schedule-builder-backend/blob/main/.github/workflows/test-and-build.yml).
Moreover, we used the following testing and static analysis tools in the system:
- `black` (widespread code linter),
- `isort` (inputs sorting),
- `pytest` (universal Python code testing library).

All CD workflow runs can be accessed [here](https://github.com/SWP2025/schedule-builder-backend/actions).


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
