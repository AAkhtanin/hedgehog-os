# Legacy Mapping

Legacy code is donor/reference only. The new MVP is built from passport v0.25 and the math appendix, not by repairing the old architecture.

Do not preserve the old architecture blindly. Use legacy files only when they help implement the new contracts and invariants.

## Mapping

- `PROJECT_GENESIS.md` -> historical foundation.
- `engine.py` -> RootOrchestrator skeleton donor.
- `manager.py` -> WorldStateAssembler donor, but weather must be an optional needle.
- `client.py` -> LocalDRS donor.
- `fractal.py` -> DAG execution donor.
- `run.py` -> executor runner donor.
- `validators.py` / `finalize.py` -> Post V&V donor.
- `validator.py` -> GTValidator donor.
- `logging_audit.py` -> audit donor.
- `embeddings.py` / `similar_lsh.py` / `vector_store.py` -> local semantic reuse donor.
- `index.py` / `record.py` / `resolver.py` -> future ExternalDRS pointer layer only.
- `architect` / `executor` prompts -> legacy reference only; contracts must be upgraded to `AttractorPacket` and `ResultProposal`.

## Prohibitions

- Never use legacy `config.py`.
- Never commit secrets.
- Do not add real external APIs for the MVP.
- Do not add LLM integration before the deterministic architecture is proven.
