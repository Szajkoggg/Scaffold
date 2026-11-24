# Module: backend

**Summary:** Services and APIs: the API contract kept true, migrations that are safe to run, and an independent
security review of every change that touches the attack surface.

## Checks

The commands come from the stack module; this module says what is checked, whatever the stack. The bootstrap writes
the chosen commands into `AGENTS.md`, "Commands".

| Check | When | How |
|---|---|---|
| Contract file | quick, on a change to an endpoint, message or schema | the contract changed in the same diff; it is valid (for OpenAPI: `npx @redocly/cli lint <file>`) |
| Contract against the code | full | the contract generated from the code compared with the committed one, or contract tests against the running service |
| Migrations | full, when one is added | applied to an empty database and to a copy of real-shaped data at the previous release's schema; the tests run on the result |
| Secrets | full | a secret scanner (e.g. gitleaks) over the changes; its command in `docs/WORKING.md` once chosen |

## Diagnosing

- **A failing request**: reproduce it with one command (`curl -i` with the headers and body) kept in `tmp/`; find
  its log lines by the request id, which every request gets and every log line and error response carries.
- **A migration failed halfway**: whether the database rolls back schema changes in a transaction decides what to do
  next (PostgreSQL does; MySQL commits each DDL statement). Read the migration table before running anything again.
- **Works locally, not deployed**: compare configuration and environment variables, dependency versions, and network
  exposure (local-only by default, below), in that order.
- **A slow endpoint**: the query plan (`EXPLAIN ANALYZE` in PostgreSQL) and the number of queries per request: one
  query per item of a list (N+1) is the usual cause.

## Health

The tools for this module's ledger row and the core's Security row, used by the `auditor`:

| Check | Tool |
|---|---|
| API contract | the contract against the endpoints served: undocumented, unused, deprecated past their date |
| Security | the checklist below over the endpoints; a secret scan over the whole history; the stack module's dependency audit |

## Measuring

- **Latency** per endpoint as percentiles (p50, p95, p99) under a stated load, never an average; the same load script
  each time, kept in the repository (k6, oha, wrk or the stack's tool), its numbers against the budgets in
  `docs/WORKING.md`.
- **The database**: queries per request and the slowest statements (`pg_stat_statements` in PostgreSQL, the slow
  query log elsewhere).

## Review

- **The contract**: a change to an endpoint, message or schema updates its contract (OpenAPI file or protocol
  document) in the same commit. Breaking changes are the user's decision.
- **Migrations**: forward-only, small, tested on a copy of real-shaped data; a migration and the code needing it go
  in an order that keeps the service running.
- **Security-relevant changes** (authentication, authorisation, input handling, secrets, permissions, network
  exposure, dependencies with network access) get a `security-reviewer` pass before the commit.

## Security checklist

- Every input from outside is validated at the boundary; nothing from outside reaches a query, a shell or a path
  unescaped.
- Authorisation is checked for each resource, not only at login.
- Secrets come from the environment or a secret store, never from the repository or a log line.
- Local-only by default: a service listens on loopback unless exposure is decided.
- Errors returned to clients do not leak internals; the log keeps the detail (principle 5).

## Agents

| Agent | Role | Runs at |
|---|---|---|
| `security-reviewer` | [roles/security-reviewer.md](../roles/security-reviewer.md) | main model, high |

## Sources

Where the truth is for this stack, nearest first (`docs/process/research.md`). Read by everyone looking something
up, and by the `researcher`.

- **The framework's and database's documentation** for the installed versions (see the stack module).
- **Security**: the [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) for the topic at hand
  (authentication, input validation, injection, secrets).
- **HTTP**: [MDN's HTTP reference](https://developer.mozilla.org/docs/Web/HTTP) for status codes, headers and
  caching.
