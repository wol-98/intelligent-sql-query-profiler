# M20 Optimization Intelligence Dashboard
## Error & Empty-State Contract

### 1. Purpose

This document defines how M20 communicates API errors, unavailable data,
empty collections, incomplete evidence, and unestablished provenance.

The dashboard must distinguish between absence of records and absence of
evidence.

---

### 2. HTTP Success

Successful read operations return HTTP 200.

A successful response may contain:

- populated data
- an empty collection
- records with incomplete evidence

HTTP 200 does not imply that all evidence is available.

---

### 3. Empty Collections

If a valid collection query returns no records, the collection endpoint
returns an empty collection using the response shape defined by that endpoint.

For the currently implemented list endpoints, the empty response is:

```json
[]
