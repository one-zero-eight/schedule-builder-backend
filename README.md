# Schedule Builder API | InNoHassle ecosystem

> https://api.innohassle.ru/schedule-builder/v0

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/one-zero-eight/schedule-builder-backend">
    <img width="128" height="128" alt="image" src="https://github.com/user-attachments/assets/2c09e1e0-6bb0-4541-9ceb-c47202a67401" />
  </a>

<h3 align="center">Schedule Builder</h3>
  <p align="center">
    Schedule Builder is created as a tool for Innopolis University Department of Education (DoE) to assist the department in efficient creation of high-quality curriculums for bachelors, masters, and PhD students without any conflicts.
    <br />
    <a href="https://docs.google.com/spreadsheets/d/1amQqvE0rfU92pfMsMnUKA-lTGjlcJ-Sv5UcPpGnxW4w/edit?gid=558406858#gid=558406858">Demo Website</a>
    &middot;
    <a href="https://disk.yandex.ru/i/31xWqPXMcE1HCw">Demo Video</a>
  </p>
</div>

## Table of contents

Did you know that GitHub supports table of
contents [by default](https://github.blog/changelog/2021-04-13-table-of-contents-support-in-markdown-files/) 🤔

## About Us

#### Project Goal

Our key goal is to simplify the process of schedule creation and correction for Innopolis University DoE.

#### Project Description

Schedule Builder is a Google Spreadsheets plugin. The plugin is opened in parallel with the schedule and launched to check
the table for conflicts. Upon successful fetching, the user receives a list of conflicts found by the plugin. To simplify
the navigation, conflicts may be **highlighted** (user's cursor is moved to the conflicting cell) and **ignored** (conflict is
hidden from the user's view). The user may repeat scanning until all conflicts are resolved.

## How to use?

To test our product, you may follow the deploy link to Google Spreadsheets table with deployed plugin in it. In the plugin, you will be firstly required to visit the special page
of InNoHassle and obtain your requests token. Paste the token in the special field
and click the schedule checking button. After collisions fetching, you may navigate through
them and take actions in the table.

## Development

### Set up for development

1. Install [Python 3.12+](https://www.python.org/downloads/), [uv](https://docs.astral.sh/uv/), [Docker](https://docs.docker.com/engine/install/).
2. Install project dependencies with [uv](https://docs.astral.sh/uv/cli/#install).
   ```bash
   uv sync
   ```
3. Copy settings.example.yaml to settings.yaml and add token:
   ```bash
   cp settings.example.yaml settings.yaml
   ```
5. Start development server:
   ```bash
   uv run -m src.api --reload
   ```
   > Follow the provided instructions (if needed).
6. Open the following link the browser: http://localhost:8012.
   > The API will be reloaded when you edit the code.

> [!IMPORTANT]
> For endpoints requiring authorization, click "Authorize" button in Swagger UI!

> [!TIP]
> Edit `settings.yaml` according to your needs, you can view schema in [settings.schema.yaml](settings.schema.yaml).

**Set up PyCharm integrations**

1. Run configurations ([docs](https://www.jetbrains.com/help/pycharm/run-debug-configuration.html#createExplicitly)).
   Right-click the `__main__.py` file in the project explorer, select `Run '__main__'` from the context menu.
2. Ruff ([plugin](https://plugins.jetbrains.com/plugin/20574-ruff)).
   It will lint and format your code. Make sure to enable `Use ruff format` option in plugin settings.
3. Pydantic ([plugin](https://plugins.jetbrains.com/plugin/12861-pydantic)). It will fix PyCharm issues with
   type-hinting.
4. Conventional commits ([plugin](https://plugins.jetbrains.com/plugin/13389-conventional-commit)). It will help you
   to write [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

### Deployment
We use Docker with Docker Compose plugin to run the service on servers.

1. Copy the file with settings: `cp settings.example.yaml settings.yaml`.
2. Change settings in the `settings.yaml` file according to your needs
   (check [settings.schema.yaml](settings.schema.yaml) for more info).
3. Install Docker with Docker Compose.
4. Build and run docker container: `docker compose up --build`.

## FAQ

### How to run tests?

Run `SETTINGS_PATH=settings.test.yaml uv run pytest` to run all tests.


### How to update dependencies?
1. Run `uv sync -U` to update all dependencies.
2. Run `uv pip list --outdated` to check for outdated dependencies.
3. Run `uv add -U <dependency_name>` to update a specific dependency in `pyproject.toml`.

## Contributing

We are open to contributions of any kind.
You can help us with code, bugs, design, documentation, media, new ideas, etc.
If you are interested in contributing, please read
our [contribution guide](https://github.com/one-zero-eight/.github/blob/main/CONTRIBUTING.md).
