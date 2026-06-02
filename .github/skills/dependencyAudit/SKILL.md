---
name: dependencyAudit
description: "Use when: auditing dependency vulnerabilities with OSV.dev queries for lockfile packages and CVE triage."
type: reference
version: "1.1"
license: MIT
---

# Dependency Audit

> Skill metadata: version "1.1"; tags [security, dependencies, audit, osv]; recommended tools [query_osv, query_deps].

Use this skill in workspaces with the secure pack selected.

Query known CVEs for project dependencies with the registered `security` MCP server when it is connected. If the server is unavailable, fall back to OSV.dev directly or a native package-manager audit command and normalize the results to the same package/version/CVE fields.

## When to use

- Before releasing or deploying
- When adding or updating a dependency
- When a security advisory is mentioned for a package in use
- As part of a periodic security review

## When NOT to use

- When reviewing source code for logic bugs — prefer `secureReview`
- When the workspace has no package lockfile to audit

## When to audit

- Before releasing or deploying
- When adding or updating a dependency
- When a security advisory is mentioned for a package you use
- As part of a periodic security review

## Using the security MCP tools

When the `security` MCP server is connected, prefer these tools:

**`query_osv(package, version, ecosystem)`**
- `package`: exact package name as it appears in the lockfile
- `version`: exact installed version string
- `ecosystem`: `PyPI`, `npm`, `crates.io`, `Go`, `Maven`, `Hex`, `NuGet`, `RubyGems`, `Packagist`, `Pub`, `Linux`, or `GitHub Actions`
- Returns: vulnerability summaries with OSV IDs and any published severity data

**`query_deps(package, version, system)`**
- `package`: exact package name as it appears in the lockfile
- `version`: exact installed version string
- `system`: `pypi`, `npm`, `cargo`, `go`, `maven`, `nuget`, `rubygems`, `packagist`, `hex`, or `pub`
- Returns: dependency health signals including known CVE count, license data, and scorecard information

If the `security` MCP server is unavailable, extract the package/version pairs from the lockfile and query OSV.dev directly or run the ecosystem's native audit command, then report the results with the same package, version, severity, and fix-version fields.

## Interpreting results

| CVSS score | Severity | Action |
| --- | --- | --- |
| 9.0–10.0 | Critical | Block release — must fix before shipping |
| 7.0–8.9 | High | Fix before release unless no viable upgrade path |
| 4.0–6.9 | Medium | Fix in next planned dependency update cycle |
| 0.1–3.9 | Low | Track; fix opportunistically |

## Recommended fix path

1. Check the `fixed-in` field from the OSV result — upgrade to that version or later
2. If no fixed version exists, look for an alternative package
3. If neither is available, document the risk and apply mitigations (isolation, input validation, rate limiting) appropriate to the vulnerability type
4. Verify the upgrade does not introduce a breaking API change before committing

## No-hit result

If `batch_query_lockfile` returns zero vulnerabilities, report: "No known vulnerabilities found in `<lockfile>` as of `<query date>`." Do not treat a clean result as a permanent guarantee.

## Verify

- [ ] Queried the registered `security` MCP tools or an explicit documented fallback for all direct dependencies
- [ ] Each CVE triaged with severity, affected version range, and patch status
- [ ] Findings reported with ecosystem, package, version, and CVE ID
