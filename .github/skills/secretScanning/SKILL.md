---
name: secretScanning
description: "Use when: scanning for credential leakage before version control or enforcing pre-commit secret hygiene."
type: reference
version: "1.0"
license: MIT
---

# Secret Scanning

> Skill metadata: version "1.0"; tags [security, secrets, scanning]; recommended tools [].

Use this skill in workspaces with the secure pack selected.

Detect credential leakage before it reaches version control. Secrets committed to a repository are effectively public, even in private repos.

## When to use

- Before staging or committing files that may contain credentials, tokens, or connection strings

## When NOT to use

- When the file has already been committed and the secret revoked — use `git-filter-repo` instead
- When scanning for code logic issues — prefer `secureReview`

## High-confidence secret patterns

Flag these as **probable secrets** requiring confirmation before staging:

| Pattern | Examples |
| --- | --- |
| API keys | `sk-...`, `pk_live_...`, `AKIA...` (AWS), `ghp_...` (GitHub) |
| Connection strings | `postgresql://user:pass@...`, `mongodb+srv://...`, `redis://:pass@...` |
| Private keys | `-----BEGIN RSA PRIVATE KEY-----`, `-----BEGIN EC PRIVATE KEY-----` |
| JWT secrets | Long random strings assigned to `secret`, `jwt_secret`, `JWT_SECRET` |
| Bearer tokens | `Authorization: Bearer <long-token>` hardcoded in source |
| Password literals | `password = "..."`, `passwd = "..."` with a non-placeholder value |

## Common false positives — do not flag

- Placeholder values: `"your-api-key-here"`, `"changeme"`, `"<INSERT_KEY>"`, `"TODO"`
- Test fixture values: files under `tests/`, `fixtures/`, `__tests__/` with obviously fake values
- Example values in documentation or README
- Environment variable references: `os.getenv("SECRET")`, `process.env.SECRET`, `${SECRET}`
- References to secret managers: `vault://...`, `arn:aws:secretsmanager:...`

## When a probable secret is found

1. Name the file and line number
2. State the pattern matched
3. Stop — do not stage or commit the file
4. Suggest the fix: move to environment variable or secret manager reference

## Entropy-based detection guidance

High-entropy strings (30+ random characters) assigned to names containing `key`, `token`, `secret`, `password`, `passwd`, `credential`, `auth` are probable secrets even without a recognizable prefix pattern. Flag them.

Low-entropy strings assigned to those names are likely placeholder text. Do not flag.

## Verify

- [ ] Applied both high-confidence and medium-confidence secret patterns
- [ ] Probable secrets surfaced for user confirmation before staging
- [ ] No known-pattern false negatives (AWS keys, GitHub tokens, private key headers, connection strings)
