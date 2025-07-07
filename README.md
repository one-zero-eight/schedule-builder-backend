[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![project_license][license-shield]][license-url]
[![commits][commit-shield]][commit-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/SWP2025/schedule-builder-backend">
    <img src="docs/images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Schedule Builder</h3>

  <p align="center">
    Schedule Builder is created as a tool for Innopolis University Department of Education (DoE) to assist the department in efficient creation of high-quality curriculums for bachelors, masters, and PhD students without any conflicts.
    <br />
    <a href="https://docs.google.com/spreadsheets/d/1amQqvE0rfU92pfMsMnUKA-lTGjlcJ-Sv5UcPpGnxW4w/edit?gid=558406858#gid=558406858">Demo Website</a>
    &middot;
    <a href="https://github.com/SWP2025/schedule-builder-backend/issues/new?template=bug-report-template.md">Report Bug</a>
    &middot;
    <a href="https://github.com/SWP2025/schedule-builder-backend/issues/new?template=technical-task-template.md">Request Feature</a>
    &middot;
    <a href="ADD DEMO VIDEO LINK HERE">Demo Video</a>
  </p>
</div>

## About Us
#### Project Goal(s)
WIP
#### Project Description
WIP
## Context Diagram
(stakeholders, external systems)
<!-- ROADMAP -->
## Roadmap

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3
    - [ ] Nested Feature

See the [open issues](https://github.com/github_username/repo_name/issues) for a full list of proposed features (and known issues).
## Testing User Guide
To test our product, you may follow the deploy link to Google Spreadsheets table with deployed plugin in it. In the plugin, you will be firstly required to visit the special page
of InNoHassle and obtain your requests token. Paste the token in the special field
and click the schedule checking button. After collisions fetching, you may navigate through
them and take actions in the table. 
## How to Install?
### Development setup
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
   uv run uvicorn src.presentation.app:app --port=8000 --host=0.0.0.0 --reload
   ```
   > Follow the provided instructions (if needed).
6. Open the following link the browser: http://localhost:8000.
   > The API will be reloaded when you edit the code.

> [!IMPORTANT]
> For endpoints requiring authorization, click "Authorize" button in Swagger UI!

> [!TIP]
> Edit `settings.yaml` according to your needs, you can view schema in [settings.schema.yaml](settings.schema.yaml).

### Deployment
We use Docker with Docker Compose plugin to run the service on servers.

1. Copy the file with settings: `cp settings.example.yaml settings.yaml`.
2. Change settings in the `settings.yaml` file according to your needs
   (check [settings.schema.yaml](settings.schema.yaml) for more info).
3. Install Docker with Docker Compose.
4. Build and run docker container: `docker compose up --build`.

### Dependencies updates
1. Run `uv sync -U` to update all dependencies.
2. Run `uv pip list --outdated` to check for outdated dependencies.

## Documentation
`.` \
`├── Development` **[here](https://github.com/SWP2025/schedule-builder-backend/tree/main/CONTRIBUTING.md)**. \
`├── Quality characteristics and attribute scenarios` **[here](https://github.com/SWP2025/schedule-builder-backend/tree/main/docs/quality-attributes/quality-attribute-scenarios.md).** \
`├── Quality assurance` \
`│   ├── Automated tests` **[here](https://github.com/SWP2025/schedule-builder-backend/tree/main/docs/quality-assurance/automated-tests.md).** \
`│   └── User acceptance tests` **[here](https://github.com/SWP2025/schedule-builder-backend/tree/main/docs/quality-assurance/user-acceptance-tests.md).** \
`├── Build and deployment automation` \
`│   ├── Continuous Integration` **[here](https://github.com/SWP2025/schedule-builder-backend/tree/main/docs/automation/continuous-integration.md).** \
`│   └── Continuous Deployment` **[here](https://github.com/SWP2025/schedule-builder-backend/tree/main/docs/automation/continuous-delivery.md).** \
`└── Architecture` \
`***    ├── Static view` **[here](https://github.com/SWP2025/schedule-builder-backend/tree/main/docs/architecture/static-view/static-view.md).** \
`***    ├── Dynamic view` **[here](https://github.com/SWP2025/schedule-builder-backend/tree/main/docs/architecture/dynamic-view/dynamic-view.md).** \
`***    └── Deployment view` **[here](https://github.com/SWP2025/schedule-builder-backend/tree/main/docs/architecture/deployment-view/deployment-view.md).**







<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/SWP2025/schedule-builder-backend.svg?style=for-the-badge
[contributors-url]: https://github.com/SWP2025/schedule-builder-backend/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/SWP2025/schedule-builder-backend.svg?style=for-the-badge
[forks-url]: https://github.com/SWP2025/schedule-builder-backend/network/members
[stars-shield]: https://img.shields.io/github/stars/SWP2025/schedule-builder-backend.svg?style=for-the-badge
[stars-url]: https://github.com/SWP2025/schedule-builder-backend/stargazers
[issues-shield]: https://img.shields.io/github/issues/SWP2025/schedule-builder-backend.svg?style=for-the-badge
[issues-url]: https://github.com/SWP2025/schedule-builder-backend/issues
[license-shield]: https://img.shields.io/github/license/SWP2025/schedule-builder-backend.svg?style=for-the-badge
[license-url]: https://github.com/SWP2025/schedule-builder-backend/blob/master/LICENSE
[product-screenshot]: images/screenshot.png
[commit-shield]: https://img.shields.io/github/commit-activity/t/SWP2025/schedule-builder-backend.svg?style=for-the-badge
[commit-url]: https://github.com/SWP2025