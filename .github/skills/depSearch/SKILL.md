---
name: depSearch
description: "Use when: discovering package manifests, querying registry metadata, assessing dependency health signals, finding replacement candidates, or confirming import usage before removing a package."
version: "1.0"
license: MIT
---

# Dep Search

> Skill metadata: version "1.0"; tags [deps, packages, registry, manifest, health, vulnerability]; recommended tools [query_osv, query_deps, web_search, file_search, grep_search, read_file].

Procedural skill for the discovery and research phases of dependency work. Guides manifest scanning, registry metadata lookup, vulnerability assessment, and import-usage confirmation. Called by the `deps` agent before any suggestion or mutating operation — this skill covers Steps 1–4 (discover, inspect, audit, suggest); the `deps` agent handles Step 5 (act).

## When to use

- Before auditing, updating, or removing a package — to confirm declared and installed state
- When researching a package's health, vulnerability record, or maintenance status
- When looking for a maintained alternative to an abandoned or vulnerable package
- When confirming that a package is actually imported in source files before proposing removal

## When NOT to use

- When the goal is to install, update, or remove packages directly — that is the `deps` agent's Act phase; this skill covers only discovery and research
- When the question is about code architecture rather than package health — prefer `review`
- When a specific known CVE needs remediation steps — query `query_osv` directly

---

## Module 1 — Discover Manifests

1. **Search for dependency manifest files** using `file_search` with glob patterns:

   | Ecosystem | Files to find |
   | --- | --- |
   | Python | `requirements*.txt`, `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `uv.lock`, `poetry.lock` |
   | Node.js | `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
   | Rust | `Cargo.toml`, `Cargo.lock` |
   | Go | `go.mod`, `go.sum` |
   | Ruby | `Gemfile`, `Gemfile.lock` |
   | .NET | `*.csproj`, `packages.config`, `global.json` |
   | Java/JVM | `pom.xml`, `build.gradle`, `build.gradle.kts` |

2. **Read each manifest** with `read_file` and extract:
   - Package name and declared version (or range)
   - Whether it is a runtime or dev/test dependency
   - Whether a lock file is present (lock file = reproducible installs)

3. If no manifests are found, report that clearly and stop — do not guess the ecosystem.

---

## Module 2 — Query Registry Metadata

4. **Use `query_deps`** (via the `security` MCP server) as the first choice for registry metadata. It returns latest version, vulnerability count, OpenSSF Scorecard, license, and dependency count in a single call.

   Fallback when `query_deps` is unavailable:

   | Ecosystem | Fallback command |
   | --- | --- |
   | Python | `pip index versions <pkg>` or fetch `https://pypi.org/pypi/<pkg>/json` |
   | Node.js | `npm view <pkg> version time.modified` |
   | Rust | `cargo search <pkg>` |
   | Go | `go list -m <mod>@latest` |
   | General | `web_search` for `<pkg> <ecosystem> latest version` |

5. **For each package under review**, record:
   - Latest stable version and approximate release date
   - Gap between declared/installed version and latest
   - License identifier (flag if not OSI-approved or if copyleft for a commercial project)
   - Whether the project is maintained — last release within 12 months is the baseline threshold

---

## Module 3 — Vulnerability Assessment

6. **Use `query_osv`** (via the `security` MCP server) to query the OSV database for each package:
   - Pass: package name, installed version, ecosystem
   - Record: any returned CVE or GHSA identifiers, CVSS severity score, and the earliest fix version

   Fallback when `query_osv` is unavailable:

   | Ecosystem | Fallback |
   | --- | --- |
   | Python | `pip-audit` |
   | Node.js | `npm audit` |
   | General | `osv-scanner` or `web_search` for `<pkg> CVE site:osv.dev` |

7. **Flag immediately** any vulnerability with CVSS ≥ 7.0 (High or Critical) that has an available fix in a newer version. These are P0 and must appear first in the report.

8. **Verify fix availability** — confirm the fix version is stable and not itself flagged. Report if the only fix is a pre-release.

---

## Module 4 — Find Replacement Candidates

9. **When a package is abandoned or has no available fix**, search for maintained alternatives:
   - Use `web_search`: `maintained alternative to <pkg> <ecosystem> <current year>`
   - Check the package's own README or GitHub issues for officially recommended successors
   - Use `query_deps` on each candidate to compare OpenSSF Scorecard and vulnerability count

10. **Evaluate each candidate** against:
    - License compatibility with the project
    - API surface compatibility (same interface vs. migration effort required)
    - Maintenance activity — at least one release in the past 6 months
    - Adoption signal — download or install count as a proxy for community validation

11. **Cite every recommendation** with its source (registry metadata URL, web search result, or README reference). Do not recommend without a citation.

---

## Module 5 — Confirm Import Usage

12. **Before proposing removal of any package**, confirm it is actively imported:
    - Use `grep_search` with the package name as a plain-text pattern (`isRegexp: false`) across all source files
    - Also search for aliased import patterns (`import <pkg> as`, `from <pkg>`)
    - Check test files separately — a package used only in tests can sometimes be moved to dev deps rather than removed entirely

13. **Report usage evidence**: list the files and line numbers where the package is imported. If zero matches are found, note this explicitly as a supporting argument for removal.

14. **Check for transitive usage** — if the package is not directly imported, it may be a required dependency of another package in the manifest. Cross-check before proposing removal.

---

## Verify

- [ ] All manifest files in the workspace found and read (Module 1)
- [ ] Registry metadata retrieved for each package under review (Module 2)
- [ ] OSV vulnerability check performed for each package (Module 3)
- [ ] Any replacement candidates researched with at least one cited source per recommendation (Module 4)
- [ ] Import usage confirmed or absence confirmed for any package proposed for removal (Module 5)
- [ ] Every recommendation cites its source
