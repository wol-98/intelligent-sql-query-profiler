# M20 Optimization Intelligence Dashboard
## Evidence & Decision Data Contract

### 1. Purpose

This document defines how M20 represents evidence produced by M13-M19.

M20 is an API and visualization layer. It does not create new experimental
evidence or independently reproduce M19 decision logic.

---

### 2. Evidence Sources

M20 may expose evidence originating from:

- M12 workload/fingerprint analysis
- M13 workload-aware prioritization
- M14 recommendation validation and effectiveness analysis
- M15 composite-index candidate generation
- M16 composite-index column-order experiments
- M17 index cost and maintenance analysis
- M18 linked cost-benefit experiments
- M19 production decision and safety framework

The source of each evidence field must remain identifiable.

---

### 3. Evidence Status

Evidence status uses the existing project vocabulary:

- COMPLETE
- PARTIAL
- INSUFFICIENT

The status describes availability and completeness of the evidence.

It does not describe whether the evidence is favorable or unfavorable.

---

### 4. Missing Evidence

Missing evidence must remain explicitly missing.

Example:

```json
{
  "median_improvement_percent": null
}
