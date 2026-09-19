# M20 — Optimization Intelligence Dashboard

## Status

M20 is the application and visualization layer built on top of
the validated M13–M19 optimization engine.

## Objective

Transform the existing workload analysis, recommendation,
experimental validation, cost-benefit analysis, production
decision, safety guardrail, and evidence provenance outputs
into an interactive dashboard.

## Architecture

```text
React + Vite + Tailwind
          |
          | HTTP / JSON
          v
       FastAPI
          |
          v
   Application Services
          |
          v
 Existing M13–M19 Engine
          |
          v
 PostgreSQL / Supabase
