# Module: backend

**Summary:** Services and APIs: the API contract kept true, migrations that are safe to run, and an independent
security review of every change that touches the attack surface.

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
