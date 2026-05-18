# Examples

Sample queries demonstrating the different routing patterns. Each shows
what expertises the router should pick.

## Queries

| File | Query | Should route to |
|---|---|---|
| `query_fiscal.txt` | Primary result + house projections | `fiscal_analysis` + `economic_forecasts` |
| `query_drift.txt` | Itaú revising Selic over time | `monetary_analysis` + `narrative_drift_detection` + `institutional_source_briefing` |
| `query_electoral.txt` | 2026 polling (Datafolha, Quaest) | `electoral_analysis` |
| `query_bridge.txt` | Fiscal context for monetary decision | `fiscal_analysis` + `monetary_analysis` |

## Running

```bash
# Single query from file
m3xabr query "$(cat examples/query_fiscal.txt)" --lancedb ./lancedb_data --debug
```

## Sample corpus

`sample_corpus/` contains 8 stub documents you can use to smoke-test
the pipeline without a real corpus. They're not representative of
production data — they exist to let you run the end-to-end pipeline
and verify wiring.

To use them, you need to ingest them into a LanceDB table. A minimal
ingestion script is shown in `sample_corpus/INGEST.md`.

## Expected outputs

`expected_outputs/` is reserved for golden regression outputs once
you've validated good responses. Empty in v0 — populate as you
iterate on expertise content.
