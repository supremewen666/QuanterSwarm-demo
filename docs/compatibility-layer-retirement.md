# Compatibility Layer Retirement Plan

This document records how the historical `app.*` compatibility layer was retired after `quanter_swarm.*` became the canonical package root.

## Goal

Keep the repository stable during the transition, then fully remove `src/app/` once internal usage and packaging entrypoints had migrated.

## Canonical Package Rules

The only canonical import roots are now:

- `quanter_swarm.application`
- `quanter_swarm.adapters`
- `quanter_swarm.agents`
- `quanter_swarm.services`
- `quanter_swarm.core`

The following namespaces are compatibility-only:

- `app`
- `app.cli`
- `app.services`
- `app.adapters`
- `app.dashboard`

## Current Status

The compatibility layer has been removed.

- `src/app/` no longer exists
- canonical package roots remain under `quanter_swarm.*`
- downstream callers must migrate to the corresponding canonical paths

## Retirement Stages

### Stage 1: Freeze legacy namespace

Status: implemented

- Canonical docs, scripts, and tests point to `quanter_swarm.*`
- `app.*` remains importable only for compatibility
- deprecation warnings are emitted by legacy package roots

### Stage 2: Remove internal usage

Status: implemented

Exit criteria:

- no repository-owned code imports `app.*`
- no tests rely on `app.*`
- no generated examples mention `app.*`
- packaging entrypoints point to `quanter_swarm.*`

At that point, the compatibility layer is only serving unknown external callers.

### Stage 3: Announce removal window

Status: completed

Audit result as of 2026-03-28:

- no repository-owned source modules import `app.*`
- no tests rely on `app.*`
- no generated examples use `python -m app.*`
- packaging entrypoints now resolve to `quanter_swarm.*`

Removal window:

- legacy `app.*` wrappers are deprecated now
- `src/app/` should not be removed before 2026-06-01
- until then, wrappers stay stable but receive no new business logic

Current actions:

- note the removal window in README or release notes
- keep wrappers stable but unchanged
- block new `app.*` references in review and linting guidance

### Stage 4: Delete compatibility layer

Status: implemented

Deleted:

- `src/app/`

Completed after:

- all internal references are gone
- migration guidance exists
- downstream users have had one transition window

## Practical Cleanup Checklist

- Keep all new entrypoints under `src/quanter_swarm/adapters/`
- Keep task-oriented flows under `src/quanter_swarm/application/`
- Prefer canonical imports in examples, docs, and tests
- Keep package examples and release notes on canonical `quanter_swarm.*` paths only
