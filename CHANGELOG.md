# Changelog

All notable changes to this project will be documented in this file.

## v0.2.5

### 🐛 Bug Fixes
- Add None as default for room_capacity field of BaseLessonDTO
- Assign name to fastapi container
- Fix room-booking url
- Github actions v3
- Github actions v4

### 📚 Documentation
- Add CHANGELOG.md
- Update CHANGELOG.md
- Refactor README.md, add CONTRIBUTING.md, distribute documentation
- Start implementing dynamic README style
- Update README.md, update docs/architecture/architecture.md

### ⚙️ Miscellaneous Tasks
- Add pytest to uv
- Add changelog generation with git-cliff
- Move changelog-generation to separate file
- Add commit-push step for changelog-generation
- Make changelog-generation create pull request instead of pushing to main
- Add missing packages to uv

## v0.2.0

### 🚀 Features
- Add optional outlook_info field to LessonWithCollisions model

### 🐛 Bug Fixes
- Adding mail to tests
- Styling
- Test fixing
- Styling
- Relocate pull-request-template.md
- Fix AT for Quality section of README.md
- README.md links

### 💼 Other
- Merge pull request #53 from SWP2025/update-readme

### 📚 Documentation
- Update README.md to include Development, Usage, Architecture, and Quality templates
- Add Kanban board subsection to Development section of README.md
- Add Secrets management subsection to Development section of README.md
- Start working on Git Workflow subsection of Development section of README.md
- Continue working on Git workflow subsection of Development section of README.md
- Finish workflow table in Development section of README.md
- Finish Git Workflow subsection of Development section of README.md
- Finish Automated Testing subsection of Development section of README.md
- Finish Continuous Integration subsection of Development section of README.md
- Update Development section of README.md
- Update README.md layout, add docs/architecture, docs/quality-assurance
- Start working on Usage section of README.md
- Finish working on Usage section of README.md
- Complete Static view and Dynamic view diagrams in Architecture section of README.md
- Finish Static View subsection of Architecture section of README.md
- Update Architecture section of README.md
- Improve maintainability description in Architecture section of README.md
- Finish Architecture section of README.md
- Update QA scenarios for Quality section of README.md
- Finish QA scenarios for Quality section of README.md
- Update UAT for Quality section of README.md
- Fix inconsistencies in README.md
- Fix reference links for Quality section of README.md
- Update UAT in README.md
- Update Acceptance Tests after Customer Review

### ⚙️ Miscellaneous Tasks
- Add missing excel range to LessonWithCollisionTypeDTO in get_outlook_collisions
- Delete ds_store file, add it to .gitignore
- Fix github actions
- Fix github actions v2
- Tests update
- Fixing style

## v0.1.5

### 🚀 Features
- Make one request in the beginning of outlook check

### 🐛 Bug Fixes
- Updating repo name in docker hub
- Docker repo

### 💼 Other
- Excel_parsing into main

### 📚 Documentation

### ⚙️ Miscellaneous Tasks
- Fix response models so that Andrey Novikov will be happy
- Fix conflicts 2
- Fix errors
- Nginx conf
- Add parser's temp folder to gitignore
- Merge cells
- Fix nginx
- Add certificates in docker compose
- Fix nginx
- Nginx conf final
- Add cors
- Preparing settings.yaml for fast deploy
- Github actions
- Github actions fix
- Adding setting.yaml
- Transferring nginx certs settings to production
- Docker compose for production
- Fix docker compose dev
- Change response type & create connected components of room collisions
- Clean collision checker code
- Merge with main branch
- Sorting by weekday and then by time
- Initial architecture
- Refactor collisions check process
- Try to pass collisions checker to tests
- Test cases
- Merge from origin
- Fix tests setup
- Linting
- Fix tests input data fromat
- Integration tests
- Tests and github actions

## v0.1.0

### 🚀 Features
- Add method to get all timeslots

### 🐛 Bug Fixes
- Some techincal fixes with README.md
- Nginx conf
- Error in parsing

### 📚 Documentation
- Add dependency update instructions, fix some commands, add new step to local set up, add ruff to linters list

### ⚙️ Miscellaneous Tasks
- Teacher assistant manager x naming
- Teacher assistant manager
- Teacher assistants fix
- Dtos refactoring
- Endpoint to check collisions
- Delete settings.yaml
- Start backend from python file
- Fix all endpoints
- Get collisions by teacher
- Check room capacity for subject
- Add topleft and rightbottom cell to the collision object
- Resolve conflicts

## v0.0.0

### 🚀 Features
- Add logic for getting rooms and bookings
- Add logic for getting rooms and bookings

### 🐛 Bug Fixes
- Docker compose error
- Errors in auth providers
- Errors in parser
- Getting user id by token
- Collisions error
- Authorization
- Token provider
- Room not found exception

### ⚙️ Miscellaneous Tasks
- Basic project structure
- Add config files to .gitignore
- Dd refactoring
- Core courses parser configured
- Check collisions by rooms
- Dependencies for parsers
- Fixed room location
- TA list

<!-- generated by git-cliff -->
