---
name: securityReview
description: "Use when: conducting a security-focused review of source code, API surfaces, authentication flows, or trust boundaries — covering injection, secret exposure, access control, and cryptographic failures."
version: "1.0"
license: MIT
---

# Security Review

> Skill metadata: version "1.0"; tags [security, review, trust-boundary, injection, owasp, authentication]; recommended tools [grep_search, semantic_search, read_file, file_search].

Procedural skill for conducting a security-focused code review. Covers trust boundary identification, injection surface scanning, secret and credential exposure, authentication and authorization review, and secure-by-default assessment. When the `secure` pack is installed, use its `secureReview` skill for the full OWASP Top 10:2025 reference table and structured output format; this skill provides the underlying procedural guidance and works standalone.

## When to use

- When reviewing code for security vulnerabilities as part of a general code review
- When checking a new API surface, authentication flow, or trust boundary before it merges
- When the review scope includes user input handling, database queries, file operations, or external calls
- When `review` agent dispatches to a security-focused review step

## When NOT to use

- When the `secure` pack is installed and a dedicated security review prompt is preferred — `secureReview` provides the OWASP Top 10:2025 reference table and structured output format; use that instead
- When the primary goal is dependency vulnerability scanning — prefer `depSearch`
- When reviewing infrastructure or deployment manifests — prefer the `devopsReview` pack skill if available
- When purely stylistic or maintainability findings are needed — prefer `agenticReview` or a general `review`

---

## Module 1 — Map Trust Boundaries

1. **Identify all entry points** where untrusted input enters the system:
   - HTTP request parameters, headers, body fields
   - Uploaded file contents and file paths
   - Environment variables and configuration sources
   - Inter-process messages (IPC, message queues, WebSockets)
   - CLI arguments and stdin

2. **Trace each input to its sinks** using `grep_search` or `semantic_search` to follow the data flow:
   - Database queries (SQL / NoSQL / ORM)
   - OS command invocations (`subprocess`, `exec`, `system`, `popen`)
   - File system operations (read, write, path construction)
   - Template renderers and string interpolation in output
   - Deserialization (`json.loads`, `yaml.load`, `pickle.loads`, `eval`)

3. **Flag trust boundary crossings** where input is used at a sink without explicit validation, parameterization, or encoding.

---

## Module 2 — Injection Surface Scan

4. **Search for high-risk patterns** using `grep_search` (set `isRegexp: true`):

   | Pattern | Risk |
   | --- | --- |
   | String interpolation in DB queries (`f"SELECT.*{`, `+.*WHERE`) | SQL injection |
   | `subprocess.*shell=True` with a variable argument | Command injection |
   | `eval\(`, `exec\(`, `__import__\(` | Code injection |
   | `yaml\.load\(` without `Loader=yaml\.SafeLoader` | YAML deserialization |
   | `pickle\.loads\(` | Arbitrary code execution |
   | Path join with unvalidated user input | Path traversal |

5. **For each hit**, read the surrounding context (±20 lines) to confirm whether the input is sanitized before reaching the sink. Report only confirmed or high-confidence risks — not all pattern matches.

---

## Module 3 — Secret And Credential Exposure

6. **Scan for hardcoded secrets** using `grep_search` with `isRegexp: true`:
   - `(?i)(api[_-]?key|apikey|api_secret)\s*=\s*['"][^'"]{8,}`
   - `(?i)(token|auth[_-]?token|access[_-]?token)\s*=\s*['"][^'"]{10,}`
   - `(?i)(password|passwd|pwd)\s*=\s*['"][^'"]{4,}`
   - `-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----`

7. **Verify secrets are loaded from environment variables or a secrets manager** at call sites — not from config files committed to source control.

8. **Check that sensitive data is absent from log statements** — search for `logger\.(info|debug|warning).*password|log.*token|print.*secret` patterns near credential-handling code.

---

## Module 4 — Authentication And Authorization

9. **For each protected route or operation**, verify:
   - Authentication is enforced server-side before the protected resource is returned
   - Authorization verifies the requesting identity owns or has permission for the specific resource (not just being authenticated)
   - Session tokens are invalidated on logout and have a finite TTL

10. **Check for IDOR patterns** — resource IDs in URLs or payloads that are not cross-checked against the authenticated user's ownership or role.

11. **Review credential storage**:
    - Passwords hashed with a modern algorithm (`bcrypt`, `argon2`, `scrypt`) — not MD5 or SHA1
    - No plaintext password in source, logs, or error messages
    - Password reset tokens are time-limited and single-use

---

## Module 5 — Report Findings

12. **Format each finding**:

    | Severity | Location | Finding | Suggestion |
    | --- | --- | --- | --- |
    | Critical / High / Medium / Low | `file:line` | One sentence | Minimal change to resolve |

    - **Critical**: direct exploitation path with no mitigation required
    - **High**: likely exploitation path requiring low effort
    - **Medium**: potential risk requiring specific conditions
    - **Low**: defence-in-depth concern or best-practice gap

13. **Do not report speculation** — every finding must have a file, a line, and a concrete risk description confirmed from the code read.

14. If the `secure` pack is installed, add the OWASP Top 10:2025 category ID (A01–A10) to each finding using the `secureReview` reference table.

---

## Verify

- [ ] Entry points identified and traced to their sinks (Module 1)
- [ ] Injection surface scanned with at least the patterns in Module 2 step 4
- [ ] Secret and credential patterns searched per Module 3
- [ ] At least one protected route or resource reviewed for authentication and authorization (Module 4)
- [ ] Every reported finding has a file, line, severity, and concrete suggestion
- [ ] No speculative findings reported (pattern match confirmed by reading context)
