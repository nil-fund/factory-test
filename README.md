# Factory Test

Factory Test owns controlled Commons acceptance fixtures and end-to-end
verification. It does not own runtime state, past experience, or normative
controls.

The first versioned corpus is
[`fixtures/commons.factory.evaluation.v1`](fixtures/commons.factory.evaluation.v1/README.md).

The pre-registered five-criterion acceptance contract and machine-readable
thresholds are in
[`acceptance/commons.factory.v1`](acceptance/commons.factory.v1/contract.md).
Factory Test owns the scenarios, corpus, and harness. Gates owns conformance
and acceptance verdict controls; Episodic owns only the append-only historical
event bytes.

The checked-in `.factory/config.toml`, `.factory/gates.toml`, and five workflow
files are preserved legacy/pre-acceptance fixtures from a trigger-only rerun.
They stop after Review, do not implement the canonical Intake-through-Ship
sequence, and are not the SC-2 eight-stage harness or evidence of success.
