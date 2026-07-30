# Factory Test

Factory Test owns controlled Commons acceptance fixtures and end-to-end
verification. It does not own runtime state, past experience, or normative
controls.

`Commons`, `Commons Factory`, and an unqualified `Factory` name the whole
six-repository system. Factory Runtime is the production ticket runner; Factory
Test independently exercises and verifies that flow.

The first versioned corpus is
[`fixtures/commons.factory.evaluation.v1`](fixtures/commons.factory.evaluation.v1/README.md).

The pre-registered five-criterion acceptance contract and machine-readable
thresholds are in
[`acceptance/commons.factory.v1`](acceptance/commons.factory.v1/contract.md).
Factory Test owns the scenarios, corpus, and harness. Gates owns conformance
and acceptance verdict controls; Episodic owns only the append-only historical
event bytes.

The historical trigger-only rerun bundle is preserved under
[`fixtures/historical/trigger-only-rerun`](fixtures/historical/trigger-only-rerun/README.md).
It stops after Review, pins an obsolete worker/model, and is neither an active
Factory Runtime configuration nor the SC-2 eight-stage harness. Factory Test
intentionally has no root `.factory/` or `opencode.json` auto-discovery surface.
