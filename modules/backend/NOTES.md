# backend: what this module should bring

**Summary:** Services and APIs: API contracts, database migrations, security checklist, observability.

Not delivered to projects: design notes for writing the module.

- API contract documented and checked (OpenAPI or a protocol doc updated in the same commit).
- Migrations: forward-only, reviewed, tested on a copy.
- Security checklist: auth, input validation, secrets, local-only defaults.
- Health rows: dependency audit, slow endpoints against budgets.
