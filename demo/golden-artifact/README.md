# Golden Artifact Demo

This demo provides a minimal golden-artifact fixture for testing the golden
regression gate (build/check-golden.py).

## Files

- `input.json` — A small, deterministic JSON input representing a team manifest
- `expected.txt` — The committed golden output that the gate verifies against

## Usage

The gate generates output from the input using a simple deterministic function
and compares it to the expected file. When the expected file is missing or the
output diverges from it, the gate fails with a helpful diff.

## Design Notes

This pattern is inspired by AntV Infographic's SSR golden examples: small,
committed inputs and outputs that prove the renderer behaves correctly without
relying on network calls or external dependencies. Team6 adopts the principle
of committed golden files and regression checks, but uses pure Python stdlib
rather than any AntV renderer or dependency.
