---
name: threatModel
description: "Use when: producing STRIDE threat models with trust boundaries, asset identification, and feature threat classification."
type: reference
version: "1.0"
license: MIT
---

# Threat Model

> Skill metadata: version "1.0"; tags [security, threat-modeling, stride]; recommended tools [].

Use this skill in workspaces with the secure pack selected.

Produce lightweight STRIDE threat models for features and modules. A threat model identifies what can go wrong before writing code, not after.

## When to use

- Modeling a new user-facing feature, API endpoint, authentication flow, or integration with external services
- Any feature handling sensitive data, authentication, authorization, or with financial or compliance implications

## When NOT to use

- When reviewing already-deployed, stable, unchanged infrastructure
- When reviewing code style or documentation only

## When to threat model

- A new user-facing feature or API endpoint
- Any feature handling authentication, authorization, or sensitive data
- Integrations with external services or data stores
- Features with financial, legal, or compliance implications

## STRIDE categories

| Threat | Description | Example |
| --- | --- | --- |
| Spoofing | Pretending to be someone else | Forged auth tokens, impersonation |
| Tampering | Modifying data without authorization | Input manipulation, log tampering |
| Repudiation | Denying an action occurred | Missing audit logs |
| Information Disclosure | Exposing data to unauthorized parties | Verbose errors, IDOR |
| Denial of Service | Exhausting resources | Missing rate limits, unbounded input |
| Elevation of Privilege | Gaining unintended permissions | IDOR leading to admin access, SSRF |

## Threat model output format

Produce this table for every threat model:

| Threat type | Description | Likelihood (H/M/L) | Mitigation |
| --- | --- | --- | --- |

Followed by:
- **Trust boundaries identified**: list the points where data crosses a trust boundary (e.g., user input → backend, backend → database, service → external API)
- **Assets at risk**: what data or capabilities an attacker would target

## Scope discipline

Keep the model focused on the component described. Do not enumerate every theoretical risk in the broader system. One table per component is correct; cross-component threats belong in a separate model for the integration point.

## Likelihood guidance

- **High**: straightforward to exploit with widely available tools or knowledge
- **Medium**: requires meaningful effort or specific knowledge
- **Low**: requires unusual conditions, insider access, or sophisticated capability

## Verify

- [ ] Trust boundaries and assets identified
- [ ] All six STRIDE categories applied (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
- [ ] Each threat documented with ID, category, description, and suggested mitigation
