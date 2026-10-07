# Quickstart

Requirements:

- Python 3.10+
- Git

## 1. Build deterministic fixtures

```bash
python3 harness/build_fixtures.py --out generated_tasks
```

This creates eight immutable baseline repositories.

## 2. Run the control self-test

```bash
python3 harness/selftest.py
```

Expected result:

```json
{"expected":{"FC003":"STALE","FC008":"GREEN"},"observed":{"FC003":"STALE","FC008":"GREEN"},"status":"GREEN"}
```

## 3. Evaluate a candidate patch

```bash
python3 harness/evaluate_candidate.py \
  --task-dir generated_tasks/FC001 \
  --variant F_full_fabric \
  --candidate-patch /path/to/candidate.patch \
  --receipt-out attempt.json
```

Promotion is fail-closed:

- tests must be GREEN;
- verifier must be GREEN;
- stale guard must be GREEN.

A stale or failed attempt can execute successfully and still be refused promotion.

## 4. Reproduce CI

The public GitHub Actions workflow runs the same self-test on `ubuntu-latest`.

This resource is intentionally independent of private repositories, private prompts, credentials, and unpublished scientific material.
