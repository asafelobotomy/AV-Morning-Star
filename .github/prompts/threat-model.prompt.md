---
mode: ask
description: "Produce a STRIDE threat model for the described component or feature."
---

Produce a STRIDE threat model for the component or feature described below.

Use the `threatModel` skill for STRIDE category definitions and output format.
If a referenced skill is unavailable, state which skill is unavailable and proceed using this prompt's local instructions only.

Output:
1. **Trust boundaries**: list the points where data crosses a trust boundary
2. **Assets at risk**: what data or capabilities an attacker would target
3. **Threat table**:

| Threat type | Description | Likelihood (H/M/L) | Mitigation |
| --- | --- | --- | --- |

Keep the model scoped to the described component only.
