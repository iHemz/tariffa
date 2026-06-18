# Test fixtures

## `sample_invoice.pdf` (not committed)

The extraction agent's live golden-case test
(`test_extracts_key_fields_from_a_real_invoice` in `tests/test_extraction.py`) is **skipped** until
you provide a real document here.

Drop a realistic commercial invoice for a chemical / industrial raw-material shipment at:

```
tests/fixtures/sample_invoice.pdf
```

Then run the test with a key set:

```bash
ANTHROPIC_API_KEY=... uv run pytest tests/test_extraction.py -k real_invoice
```

Per `docs/05-build-phases.md`, sourcing a handful of invoices with enough formatting variety is its
own task and the real measure of whether extraction works — the wiring tests only prove the agent is
plumbed correctly. Gather several and expand this into a golden set as you go.

Keep real documents out of git (they may contain third-party commercial data) — this directory is
`.gitignore`d except for this README.
