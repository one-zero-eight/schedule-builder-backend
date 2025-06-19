# Schedule Builder Backend
## About

Schedule Builder is created as a tool for Innopolis University Department of Education (DoE) to assist the department in efficient creation of high-quality curriculums for bachelors, masters, and PhD students without any conflicts.
### Technologies
- [Python 3.12](https://www.python.org/downloads/) & [uv](https://docs.astral.sh/uv/)
- [FastAPI](https://fastapi.tiangolo.com/)
- Formatting and linting: [black](https://docs.astral.sh/ruff/), [pre-commit](https://pre-commit.com/), [isort](https://github.com/PyCQA/isort)
- Deployment: [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/), [GitHub Actions](https://github.com/features/actions)
## Development

### Set up for development

1. Install [Python 3.12+](https://www.python.org/downloads/), [uv](https://docs.astral.sh/uv/), [Docker](https://docs.docker.com/engine/install/)
2. Install project dependencies with [uv](https://docs.astral.sh/uv/cli/#install).
   ```bash
   uv sync
   ```
3. Start development server:
   ```bash
   uvicorn src.presentation.app:app --port=8000 --host=0.0.0.0 --reload
   ```
   > Follow provided instructions if needed
4. Open in the browser: http://localhost:8000
   > The api will be reloaded when you edit the code

> [!IMPORTANT]
> For endpoints requiring authorization click "Authorize" button in Swagger UI

> [!TIP]
> Edit `settings.yaml` according to your needs, you can view schema in
> [config_schema.py](src/config_schema.py) and in [settings.schema.yaml](settings.schema.yaml)
### Deployment

We use Docker with Docker Compose plugin to run the service on servers.

1. Copy the file with settings: `cp settings.example.yaml settings.yaml`
2. Change settings in the `settings.yaml` file according to your needs
   (check [settings.schema.yaml](settings.schema.yaml) for more info)
3. Install Docker with Docker Compose
4. Build a Docker image: `docker compose build --pull`
5. Run the container: `docker compose up --detach`
6. Check the logs: `docker compose logs -f`

# How to update dependencies

## Project dependencies

1. Run `uv show --outdated --all` to check for outdated dependencies
2. Run `uv add <package>@latest` to add a new dependency if needed
