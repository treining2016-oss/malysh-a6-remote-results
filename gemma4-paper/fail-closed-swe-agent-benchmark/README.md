# Fail-Closed SWE Agent Benchmark

Public-safe reproducibility resource for the **Google – The Gemma 4 Developer Agent Paper Track**.

## Goal

Measure whether a coding-agent control architecture improves reliability independently of raw model capability.

The benchmark focuses on failure modes that ordinary pass-rate metrics can miss:

- stale repository state;
- conflicting writers;
- duplicate work across session rollover;
- partial tool side effects;
- verifier rejection of plausible-but-invalid patches;
- unsafe promotion of unverified results.

## Core principle

> An agent result is not canonical because it finished. It becomes canonical only when the evidence still matches the world and every predeclared gate passed.

## Architecture under study

1. **Observer** — read-only state reconstruction.
2. **Executor** — bounded work against a pinned starting state.
3. **Verifier** — independent tests, invariants, stale checks and evidence validation.
4. **Promotion gate** — atomic, single-writer, fail-closed promotion.

## Ablations

- **A** Baseline
- **B** + retrieval
- **C** + observer
- **D** + stale-state / single-writer protection
- **E** + independent verifier
- **F** full fabric + continuity-aware handoff

## Task classes

Eight deterministic task classes cover single-file repair, multi-file consistency, stale state, conflicting writers, partial side effects, hidden invariants, session rollover, and dependency-aware navigation.

## Reproducibility

Every attempt emits a structured receipt including:

- task and variant identifiers;
- seed;
- repository commits before/after;
- candidate patch SHA-256;
- test verdict;
- stale-guard verdict;
- verifier verdict;
- promotion verdict;
- invalid-write / duplicate-work / rollback counts;
- tool-call count;
- wall time.

Canonical fixtures are immutable. Attempts execute on fresh clones so one attempt cannot contaminate another.

## Current status

The harness control self-test is GREEN:

- a normal deterministic task promotes **GREEN**;
- a stale-state task executes but is refused with **STALE**.

No empirical model-comparison claims are published until the preregistered A–F runs exist.

## Scope

This repository contains only public-safe benchmark material. It excludes private prompts, credentials, server topology, unpublished scientific work, and private repositories.
