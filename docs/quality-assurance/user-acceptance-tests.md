# User acceptance tests
## Sprint 4 Acceptance Tests
### Acceptance Test 1 (Collision Checking)
Formulation: **Given** a Google Spreadsheets table with scheduling conflicts, **when** a user launches the plugin within the scope of the table and clicks the
button ”Check conflicts,” **then** upon back-end loading the user receives a list of conflicts in the table.

Issue link: [here](https://github.com/SWP2025/schedule-builder-backend/issues/34).

### Acceptance Test 2 (Collision Filtering)
Formulation: **Given** a list of conflicts in the table upon running the plugin
on a Google Spreadsheets table, **when** a user selects a filter for the conflict type (room,
teacher, capacity, Outlook), **then** only conflicts of the selected type are displayed.

Issue link: [here](https://github.com/SWP2025/schedule-builder-frontend/issues/26).

### Acceptance Test 3 (Animations Functionality)
Formulation: **Given** a Google Spreadsheets table with scheduling
conflicts, **when** a user launches the plugin within the scope of table and clicks the
button ”Check conflicts,” **then** during back-end loading the user sees a high-quality
animation.

Issue link: no issue link, successfully closed during Sprint 4.
## Sprint 5 Acceptance Tests

### Acceptance Test 4 (Collision Highlighting)
Formulation: **Given** a Google Spreadsheets table with scheduling conflicts, **when**
a user launches the plugin within the scope of table and clicks the button "Check conflicts,"
**then** for each conflict in the output it is possible to highlight it
(so that the user's cursor gets moved to the conflicting cell).

Issue link: no issue link, successfully closed during Sprint 5.

### Acceptance Test 5 (Collision Ignoring)
Formulation: **Given** a Google Spreadsheets table with scheduling conflicts, **when**
a user launches the plugin within the scope of table and clicks the button "Check conflicts,"
**then** for each conflict in the output it is possible to ignore it
(so that the conflict is not displayed).

Issue link: no issue link, successfully closed during Sprint 5.
