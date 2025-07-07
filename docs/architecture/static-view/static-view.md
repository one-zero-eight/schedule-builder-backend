## Static view
![](https://github.com/SWP2025/schedule-builder-backend/tree/main/docs/architecture/static-view/componentDiagram.png)

The created codebase is coupled, as:
- the entirety of backend is managed with a router,
- a validator is applied upon the conduction of parsing and Outlook requests,
- a user has no possibilities to bypass the authorizer and has to be verified in order to use the product.

The maintainability of the product is simplistic with our design choices, since the system is modifiable, testable,
and analysable (as per [ISO 25010](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010) standard).
