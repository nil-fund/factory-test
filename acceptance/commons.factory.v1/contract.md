# Commons Factory success-criteria evidence contract

Status: pre-registered acceptance design contract, version 1. Factory Runtime
has non-authoritative operational telemetry, while Gates has a fail-closed
record and lifecycle conformance check. No approved production writer appends
to the Episodic acceptance stream, and no Gates acceptance verifier has
validated an authoritative run. Record conformance proves neither external
provider authenticity nor acceptance. The current evidence state is therefore
0 of 5 criteria evidenced and 0 of 5 achieved.

This contract defines what must be true before Commons may claim that Factory
meets its five success criteria. It separates three questions that must not be
collapsed:

1. **Implemented** — the required production path exists and focused tests pass.
2. **Evidenced** — a current acceptance run produced complete, authoritative
   evidence for that path.
3. **Achieved** — the evidence satisfies the pre-registered threshold in this
   contract.

A unit test, a workflow document, a mutable aggregate, or an unmerged branch can
prove implementation work. None of them alone proves achievement.

The machine-readable acceptance parameters are in
[`acceptance-plan.json`](acceptance-plan.json).
Changing a threshold requires changing both files in the same reviewed change.

## Scope

This contract applies to the Commons eight-stage pipeline:

```text
Intake -> Triage -> Spec -> Implement -> Verify -> Review -> Merge -> Ship
```

It does not change the legacy trigger-only Factory Runtime mode. It does not authorize
an agent to merge. A human remains the only actor allowed to perform the merge;
Factory Runtime may observe and attest that merge, then perform deterministic
post-merge verification and the configured Ship workflow.

## Authority and derivation boundaries

| Concern | Authority | May be rebuilt? | Must not become authority |
|---|---|---:|---|
| Raw Factory Runtime experience events | Episodic | No | Factory Runtime SQLite, Gates projections, Glance cache |
| Event envelope and lifecycle conformance | Gates | No | Factory Runtime producer types, Episodic directory layout |
| Acceptance scenarios, thresholds, fixtures, and harness | Factory Test | No | Runtime unit tests, dashboard labels |
| Queue, leases, workspaces, retries, delivery outbox | Factory Runtime | Yes, except an unexported outbox entry | Episodic readers |
| Fingerprints, executable checks, guardrails, promotion state | Gates | No | Factory Runtime prompts or dashboard labels |
| Metrics projections and scorecards | Derived from Episodic events plus Gates state | Yes | Hand-edited aggregate files |
| Dashboard presentation | Glance | Yes | Glance database or browser state |

Episodic owns the append-only historical bytes. Gates owns the normative event
schema, lifecycle reducer, executable conformance checks, fingerprints, and
acceptance verdicts. Factory Runtime owns the meaning and correctness of the
event candidates it emits. Factory Test owns this contract, its
machine-readable plan, the controlled corpus, and the acceptance harness.
Neither Gates nor Factory Test may retain a second authoritative copy of raw
run history.

Substrate must explicitly collect the nested typed path
`factory/YYYY/MM/DD.jsonl` into its memory manifest and query index. The
collector must keep controlled fixtures out of memory and must label
`factory-runtime-operational/**` as non-authoritative. Commons must not claim
Factory Runtime experience is queryable until those path, content-identity, and query
tests pass.

The target logical stream is:

```text
commons://episodic/factory/YYYY/MM/DD.jsonl
```

The schema and conformance checker must land in Gates, and the append-only
physical path must be governed in Episodic, before Factory Runtime emits
production events. This document is the Factory Test acceptance contract. It is not a
substitute for a Gates control, an approved Episodic writer, or independent
provider verification.

## Event envelope

Every line is one complete JSON object. These fields are required for every
Factory Runtime evaluation event:

| Field | Type | Contract |
|---|---|---|
| `schema_version` | string | Exactly `commons.factory.evaluation.v1` for this contract. |
| `event_id` | UUIDv7 string | Allocated once, persisted in the Factory Runtime outbox, and reused on every retry. |
| `event_type` | string | One of the event types defined below. |
| `occurred_at` | canonical RFC 3339 UTC timestamp | Time the represented fact occurred, encoded with uppercase `T` and `Z` and at most six fractional-second digits. |
| `recorded_at` | canonical RFC 3339 UTC timestamp | Time Episodic durably appended the event, encoded with uppercase `T` and `Z` and at most six fractional-second digits. Never substitutes for `occurred_at`. |
| `stream_id` | string | Stable Factory Runtime installation and managed-repository stream identifier. |
| `sequence` | integer | Strictly increasing within `stream_id`, with no reuse after reset or restore. |
| `producer` | object | `component`, `version`, `instance_id`, and `process_id`. |
| `source` | object | `kind`, stable `id`, optional `revision`, and optional immutable `uri`. |
| `correlation` | object | Stable Commons and Factory Runtime identities described below. |
| `actor` | object | `kind`, stable `id`, and agent/model fields when applicable. |
| `payload` | object | Event-specific facts. |
| `integrity` | object | `payload_sha256`, `draft_sha256`, `previous_event_sha256`, and redaction policy version. |

### Integrity preimages

Independent producers and consumers use these exact byte-level definitions:

- `payload_sha256` is lowercase hex SHA-256 over the RFC 8785 JSON
  Canonicalization Scheme UTF-8 bytes for the object
  `{"event_type": <event type>, "payload": <payload>}`.
- `draft_sha256` is lowercase hex SHA-256 over RFC 8785 UTF-8 bytes for an
  object containing exactly `schema_version`, `event_id`, `event_type`,
  `occurred_at`, `stream_id`, `producer`, `source`, `correlation`, `actor`, and
  `payload`, plus `supersedes_event_id` and `correction_reason` iff present.
  Append-assigned `sequence`, `recorded_at`, all `integrity` fields, and JSONL
  formatting are excluded.
- `previous_event_sha256` is lowercase hex SHA-256 over the exact UTF-8 bytes
  of the prior physically accepted JSON object line in the same stream,
  excluding its `LF` or `CRLF` terminator. It is not a hash of reparsed or
  reserialized JSON.
- The first physical event in a stream uses JSON `null` as the
  `previous_event_sha256` sentinel.
- JSONL writers may terminate lines with `LF` or `CRLF`, but the terminator is
  never part of the preimage. Blank lines are forbidden.
- Corrections append to this physical hash chain before any effective
  correction projection. A correction never rewrites the earlier line or
  chains from a projected replacement.

### Correlation fields

`correlation` contains these fields. A field may be `null` only when the event
occurs before that identity exists.

| Field | Required from | Meaning |
|---|---|---|
| `commons_system_id` | all events | Stable Commons installation identifier. |
| `repository_id` | all events | Canonical remote identity, not a checkout path. |
| `ticket_id` | intake onward | Source ticket identity. |
| `intent_id` | intake onward | Stable normalized-intent identity shared by equivalent human and system intake. |
| `pipeline_execution_id` | pipeline start onward | Globally unique pipeline execution identity; never a resettable SQLite row id alone. |
| `pipeline_template_hash` | pipeline start onward | Hash of ordered stages, transition policy, workflow hashes, and gate bindings. |
| `stage_attempt_id` | stage events | Globally unique identity for one stage attempt. |
| `stage` | stage events | One of the eight canonical stage names. |
| `runtime_run_id` | worker events | Factory Runtime-local run id, qualified by `stream_id`; diagnostic only. |
| `parent_event_id` | dependent events | The immediately causal event, not merely an earlier compatible event. Worker selection points to the exact current predecessor. |

### Actor fields

`actor.kind` is one of `human`, `system`, or `agent`.

- A human actor includes canonical provider identity plus `provider_evidence`
  references and hashes. Those fields are recorded claims until a separate
  Gates-owned verifier resolves them against a trust root and credential
  unavailable to Factory Runtime.
- A system actor includes the component and rule or schedule that caused the
  action.
- An agent actor includes `worker_id`, `runtime`, `model_id`,
  `worker_config_hash`, and, when exposed by the provider, model revision.

Provider evidence is chronologically valid only when
`authenticated_at <= verified_at <= recorded_at`. A verified merge attestation
additionally requires
`merged_at <= verified_at <= occurred_at <= recorded_at`.

Unknown agent or model identity is an evidence failure for the agent-swap
criterion. It must not be replaced with the configured default.

### Event types and payloads

#### `factory.intake.accepted`

Required payload fields:

- `origin_kind`: `human` or `system`
- `origin_channel`: for example `github`, `scanner`, `telemetry`, or `schedule`
- `raw_input_ref` and `raw_input_sha256`
- `normalized_intent_sha256`
- `normalizer_version`
- `accepted`: boolean

Sensitive raw input remains at its governed source. Episodic stores an immutable
reference and hash, not credentials or unredacted secret-bearing content.

#### `factory.pipeline.started`

Required payload fields:

- `initial_stage`, which must be `intake` for success-criteria runs
- `stage_order`, exactly the eight canonical stages
- `workflow_commit`
- `gates_commit`
- `factory_commit`
- `substrate_commit`
- `pipeline_template`, the complete bounded
  `commons.pipeline-template.v1` object containing:
  - the canonical stage order and transition-policy version;
  - one workflow SHA-256 for each stage; and
  - one ordered gate binding per stage, including gate id/version and every
    check id, rule version, and rule SHA-256.

`pipeline_template_hash` is exactly lowercase SHA-256 over the RFC 8785 UTF-8
bytes of the complete `pipeline_template` object. The Gates conformance checker
recomputes this digest, requires `stage_order` to match, and requires every gate
event's ordered check contract to match its stage binding. Equality is still
only a producer-consistency claim until an acceptance verifier resolves the
workflow, rule, and reviewed-commit hashes independently.

#### `factory.worker.selected`

Required payload fields:

- `stage`
- `selection_reason`
- `exploration`: boolean
- `eligible_workers`
- `excluded_workers`
- `separation_degraded`: boolean

The selected worker identity is in `actor`. The full configuration is referenced
by `worker_config_hash`; secrets are never embedded.

#### `factory.stage.completed`

Required payload fields:

- `stage`
- `outcome`: `passed`, `failed`, `cancelled`, or `escalated`
- `attempt_number`
- `artifact_uri` and `artifact_sha256`, both nullable only when no artifact was produced
- `latency_ms`
- `usage`: input, output, cached, and reasoning tokens, each integer or `null`
- `cost`: amount, ISO currency, source, status, and evidence

Cost status is one of `actual`, `estimated`, or `unknown`. Unknown is represented
by `amount: null`; it is never represented as zero. Zero is valid only when the
provider or local deterministic runner measured an actual zero cost.

An `actual` stage cost requires an immutable evidence URI, SHA-256,
`source_identity`, and `meter_version`, with kind `provider_invoice` or
`trusted_local_meter`. Estimated and unknown costs carry `evidence: null`.
These fields remain producer claims: acceptance requires a Gates-owned verifier
to resolve and hash-check the provider or local-meter artifact using trust
unavailable to Factory Runtime. That verifier is not implemented, so actual-cost
acceptance evidence and SC-5 are currently blocked.

#### `factory.gate.evaluated`

Required payload fields:

- `stage`, `gate_id`, and `gate_version`
- `gates_commit`
- `verdict`: `pass`, `fail`, or `escalate`
- `checks`: ordered objects containing check id, rule version, rule SHA-256,
  result, evidence references, and one SHA-256 per reference
- `input_artifact_sha256`

A gate record is a Factory Runtime-authored producer claim. Conformance proves only its
shape, causal input binding, ordered template/check binding, aggregate verdict,
and evidence-reference/hash cardinality. It does not prove that any executable
check ran. Acceptance must use a Gates-owned verifier, unavailable to Factory
Runtime,
to resolve and hash-check or rerun every declared rule and evidence artifact
against the reviewed Gates commit. That verifier is not implemented; therefore
no success criterion currently has admissible gate evidence. The existence of
Markdown rule text alone never produces a pass.

#### `factory.pipeline.awaiting_human`

Required payload fields:

- `boundary`: `merge`
- `pull_request_uri`
- `review_verdict_event_id`
- `merge_performed`: always `false`

No Merge or Ship stage event may exist for the same execution before a valid
human merge attestation.

#### `factory.merge.attested`

Required payload fields:

- `pull_request_uri`
- `provider_event_id`
- `pre_merge_head_sha`
- `merge_commit_sha`
- `target_branch`
- `merged_at`
- `provider_evidence`, binding provider, canonical repository and pull request,
  immutable provider event and delivery ids, provider subject/account type,
  base/head refs, pre-merge head, merge commit, evidence URI/hash,
  verification-bundle URI/hash, verifier component/version/principal,
  verification method/time, trust-policy commit, and trust-root identity

The actor must be `human`, its canonical identity must match the evidence
subject, and all duplicated merge fields must match the evidence bundle.
Schema and offline stream validation cannot establish authenticity because
Factory Runtime could self-author those fields. A separate Gates-owned verifier must
fetch and verify the provider evidence using a trust root, key, or provider
credential unavailable to Factory Runtime and its workers; reject known Factory
Runtime and worker principals; and emit a verdict bound to the exact evidence
hashes.
This proves provider attribution to a governed human-controlled account, not a
physical click if that account or token could be automated. The event observes
a merge; it never instructs Factory Runtime or an agent to merge.

#### `factory.ship.verified`

Required payload fields:

- `merge_event_id`
- `merge_commit_sha`
- `release_record_uri` and `release_record_sha256`
- `environment`
- `rollout_status`: `complete` or `rolled_back`
- `rollback_handle_ref`
- `monitoring_evidence_refs`

Only `rollout_status: complete` can support a successful pipeline completion.
`merge_event_id` binds the verified human merge evidence; it is not the causal
parent. The causal parent is the passing Ship gate for the same stage attempt
and runtime run.

#### `factory.pipeline.completed`

Required payload fields:

- `outcome`: `shipped`, `rolled_back`, `failed`, or `abandoned`
- `terminal_stage`
- `ship_event_id`, required for both `shipped` and `rolled_back`
- `total_latency_ms`
- `total_cost`, with the same honesty rules as stage cost

`awaiting_human` is not completion.

`total_latency_ms` is the whole number of elapsed milliseconds from
`factory.pipeline.started.occurred_at` through
`factory.pipeline.completed.occurred_at`, including retries and human wait.
Sub-millisecond remainder is floored.

`total_cost` aggregates every effective `factory.stage.completed` attempt,
including failed and retried attempts:

- if every attempt cost is `actual` and uses one currency, sum the amounts and
  emit `actual` with `derived_aggregate` evidence and meter version
  `stage-cost-sum-v1`;
- if every amount is known, currencies match, and any attempt is `estimated`,
  sum the amounts and emit `estimated`;
- per-attempt sources may differ; a known aggregate always uses
  `source: derived:stage-cost-sum-v1`;
- if any attempt cost is `unknown`, currencies differ, or no attempt cost
  exists, the aggregate is `unknown` with null amount, currency, source, and
  evidence;
- no currency conversion or configured-default cost is inferred.

Amounts are summed as exact base-10 decimals using each input JSON number's
RFC 8785-normalized numeric text, with no intermediate binary floating-point
rounding. The emitted JSON number is the canonical exact decimal result; for
example, `0.1` plus `0.2` is `0.3`, never `0.30000000000000004`.

#### `factory.escape.observed`

Required payload fields:

- `release_event_id`
- `incident_ref`
- `signature`
- `severity`
- `detected_at`
- `attributed_stage_attempt_ids`

An internal worker failure is not an escape. An escape is a defect that passed
the applicable gates and reached a shipped release. Its causal parent is the
`shipped` pipeline completion whose `ship_event_id` equals `release_event_id`.

#### `factory.fingerprint.transitioned`

Required payload fields:

- `fingerprint_id`
- `from_status` and `to_status`
- `gates_commit`
- `reproducer_ref`
- `regression_test_ref`
- `validation_evidence_event_ids`

Allowed transitions are `candidate -> validated -> active -> generalized`.
There is no direct `candidate -> active` transition. Candidate validation and
generalization parent the latest replay named by their evidence list.
Activation parents the immediately preceding validated transition for the same
fingerprint.

#### `factory.replay.evaluated`

Required payload fields:

- `fingerprint_id`
- `rule_id` and `rule_version`
- `fixture_id`
- `fixture_class`: `own_escape`, `known_clean`, or `next_similar`
- `matched`: boolean
- `blocked`: boolean
- `target_gate`

This is the proof used for validation, false-positive measurement, and the
"next similar blocked" criterion.

An `own_escape` replay parents the escape that triggered it. A `known_clean`
replay parents the latest earlier replay for the same fingerprint. A
`next_similar` replay parents the active transition for that fingerprint.

## Stream invariants

1. **Append only.** Existing lines are never edited, reordered, or deleted.
   Corrections append a new event with `supersedes_event_id` and a reason.
2. **Stable identity.** An event id is allocated before delivery and is reused
   across crashes, retries, reconciliations, and process boundaries.
3. **Idempotence.** Appending an existing event id with the same verified
   `draft_sha256` is a no-op and does not append a second physical line. The
   same id with a different immutable draft hash is a hard collision.
   `payload_sha256` alone is never sufficient for deduplication.
4. **Single order per stream.** `(stream_id, sequence)` is unique and strictly
   increasing, and `recorded_at` never regresses as sequence advances. A reset
   creates neither a new sequence origin nor reused run ids.
5. **Hash continuity.** Each event commits to the prior accepted event in its
   stream. A migration event may begin a new explicitly named imported stream.
6. **Atomic intent, recoverable delivery.** The Factory Runtime ledger may hold a
   transactional outbox, but a success claim is blocked while a relevant outbox
   entry is unexported. The outbox is a buffer, not history authority.
7. **Truthful nulls.** Unknown cost, tokens, model, or attribution remain null
   with an explicit status. They are never silently changed to zero or a
   configured default.
8. **Secret redaction.** Redaction runs before persistence. A rejected event goes
   to a dead-letter queue with no secret-bearing payload in its diagnostic.
9. **Complete causality.** Every gate event references a completed stage attempt;
   each worker selection references the exact current predecessor; a child fact
   cannot occur before its causal parent; every shipped completion references a
   verified human merge and Ship event; every active fingerprint references
   validation and a regression test.
10. **No synthetic achievement.** Imported historical data is marked imported
    and cannot alone satisfy a current acceptance scenario.
11. **Deterministic replay.** Rebuilding projections twice from the same event
    cursor and Gates commit produces byte-identical canonical projection output.
12. **Retention.** Raw evaluation events are never capped at the most recent 50.
    Bounded scorecards are views over the full stream.
13. **Independent provider verification.** Event fields such as verifier id,
    credential class, or evidence URI are not proof by themselves. A success
    manifest is invalid until Gates independently verifies the immutable
    provider bundle and prior append-only cursor using secrets or trust roots
    unavailable to Factory Runtime.
14. **Independent gate and cost verification.** Producer-authored gate verdicts,
    evidence hashes, and `actual` cost labels are not proof. A success manifest
    is invalid until Gates independently resolves or reruns gate artifacts and
    verifies cost-meter evidence against reviewed commits and trust unavailable
    to Factory Runtime.

## Gates projections

Gates may materialize worker scorecards, escape summaries, and rule-effectiveness
views. Every projection must contain:

- projection schema and generator version;
- source Episodic stream ids and inclusive sequence ranges;
- source event count and terminal cursor hash;
- Gates commit used for rule interpretation;
- generated timestamp;
- completeness flags for identity, usage, cost, and escape attribution.

Projection rules:

- First-pass rate is derived from attempt number 1 gate verdicts, not process
  exit status.
- Attempts are grouped by pipeline execution and stage, not resettable task id.
- Worker pass rate uses the worker actually selected for the attempt.
- Escape attribution comes only from `factory.escape.observed` and its linked
  stage attempts.
- Post-activation recurrence counts only an escape whose signature matches an
  active rule version after that rule's activation event.
- Cost comparisons use `actual` cost only. Estimated cost is reported
  separately; unknown cost makes the cost criterion unevaluable.
- Mutable `workers/*.json` files, if retained for compatibility, are generated
  caches and carry no authority.

Factory Runtime SQLite remains the operational source for queue recovery and live
inspection. It is not the source for cross-reset or cross-machine quality trends.

## Evidence manifest

Each acceptance execution produces a canonical evidence manifest with:

- `contract_version` and `scenario_id`;
- exact Factory Runtime, Episodic, Gates, Substrate, fixture, workflow, and managed-repo commits;
- event stream ids, inclusive sequence ranges, event count, and terminal hash;
- fixture ids and pre-registered random seed, if any;
- derived projection artifact URI and hash;
- each assertion, observed value, threshold, and result;
- verifier identity and whether it is independent of the producer;
- provider-verification bundle URI/hash, trust-root identity/version, and the
  Gates verdict bound to the merge event;
- start/end timestamps, result, and explicit caveats.

The manifest's own hash proves only self-consistency. It is non-authoritative
until a Gates-owned verifier emits a verdict or attestation over the exact
canonical manifest hash, reviewed Gates commit, trust-root identity/version,
and authoritative stream cursor. Factory Runtime and its workers must not possess the
attestation key or verifier credential.

The manifest result is one of `passed`, `failed`, `blocked`, or `invalid`.
Missing or incomplete telemetry makes a run `invalid`, not failed and never
passed.

## Acceptance scenarios

### Admission precondition

The current machine-readable plan has `acceptance_ready: false`. No scenario run
is admissible until a reviewed plan revision fills, without placeholders:

- immutable fixture/cohort manifest ids and SHA-256 values;
- all deterministic seeds;
- the approved canonical pipeline-template artifact and SHA-256;
- the approved gate-policy artifact and SHA-256;
- trusted Factory Runtime, Episodic, Gates, Substrate, workflow, and managed-repository
  commits; and
- the pre-assigned complexity/defect-class manifest and SHA-256.

Pins are typed, not merely non-empty: ids are bounded immutable identifiers;
SHA-256 values are canonical lowercase 64-hex strings; commits are canonical
lowercase 40-hex object ids; artifacts use traversal-free `commons://` URIs;
and seeds are a non-empty, unique, bounded list of string or non-negative
integer scalars.

SC-1, SC-2, and SC-3 must use that exact approved template and gate policy, not
merely matching producer-selected values. A missing preregistration field makes
the run `invalid`; it cannot be filled after results are observed.
Before any run, the harness must execute the Gates-owned
`check-factory-acceptance-plan --require-ready` control. Readiness is derived
from pins and verifier state; the `acceptance_ready` field cannot override a
missing prerequisite.

Version 1 is intentionally unable to derive a ready state. Gates does not yet
contain an independent verifier registry that binds each reviewed gate, cost,
provider, and manifest verifier to its artifact path, SHA-256, Gates commit,
trust-root registration, and trust-root attestation. Those registrations must
be controlled outside Factory Runtime. Consequently, a plan-authored
`independent_verification.implemented: true` assertion is invalid and
`--require-ready` remains fail-closed until Gates implements that registry and
its validation.

### SC-1 — Human and system intake converge

Use two fixtures with semantically identical intent:

- one enters through an authenticated human ticket;
- one enters through a scanner-owned system ticket.

Both must begin at Intake. Compare their canonical pipeline projections after
normalization.

Required equal fields:

- normalized intent hash;
- pipeline template hash;
- ordered stage and gate ids;
- workflow, Gates, Factory Runtime, and Substrate commits;
- risk and routing result for the controlled fixture.

Allowed differences are limited to event identity, timestamps, source reference,
origin kind/channel, and actor identity.

Pass conditions:

- both inputs are accepted exactly once;
- both create exactly one pipeline execution at Intake;
- the canonical pipeline diff is empty after removing the allowed differences;
- neither input takes a source-specific bypass path.

### SC-2 — The complete eight-stage SDLC ships

Run one controlled repository fixture through all eight stages.

At Review pass:

1. Factory Runtime emits `pipeline.awaiting_human`.
2. Factory Runtime has no usable merge credential or automatic-merge action.
3. Assert that no Merge or Ship event exists.
4. A designated human merges through the provider.
5. A Gates-owned verifier resolves and verifies the provider evidence with
   credentials or keys unavailable to Factory Runtime.
6. Factory Runtime appends `merge.attested` only with that bound verdict.
7. The Merge worker is caused by the verified merge attestation. Merge performs
   post-merge verification against the exact merge commit and its passing gate
   becomes the Ship worker's parent.
8. Ship produces a release record, rollback handle, and monitoring evidence;
   its passing gate becomes the `ship.verified` parent.
9. `ship.verified.merge_event_id` still binds the human merge attestation, and
   the pipeline completes with outcome `shipped` by parenting the Ship event.

Pass conditions:

- the stage order is exactly the canonical eight stages, once each on the
  first-pass fixture;
- the merge commit contains the accepted change and passes the configured
  post-merge checks;
- the merge actor is verified human and distinct from Factory Runtime credentials;
- Ship references the same merge commit;
- completion references the Ship event;
- no auto-merge attempt appears anywhere in the event range.

### SC-3 — Mid-pipeline worker swap

Use a pre-registered ten-ticket golden cohort, producing at least 50 stage gate
opportunities in both arms.

- Baseline arm: worker A handles all agent stages.
- Swap arm: worker A handles through Spec; worker B takes over at Implement.
- Both arms use identical input fixtures, base commits, workflow commits, gate
  commits, pipeline template, and deterministic-code-node versions.

Structural pass conditions:

- canonical pipeline diff is empty when the allowed worker identity, event id,
  and timing fields are removed;
- both workers satisfy the same worker contract;
- every swapped work order includes the same prior artifacts and rejection
  lineage as the baseline.

Quality pass conditions:

- both arms complete every ticket;
- absolute first-pass gate-rate delta is at most five percentage points;
- the swap arm introduces no additional escape;
- neither arm has missing worker/model identity.

### SC-4 — Escape becomes a blocking rule

Use a seeded defect that the initial Gates commit intentionally does not detect.

1. The baseline fixture ships and a real acceptance incident emits
   `escape.observed`.
2. A candidate fingerprint links to the release, lineage, minimal reproducer,
   and proposed executable check.
3. Validation replay must match its own escape and match zero known-clean
   fixtures in the registered false-positive corpus.
4. Gates records `candidate -> validated`, lands the regression test and
   executable rule, then records `validated -> active`.
5. A distinct fixture in the same defect class enters the pipeline after
   activation.
6. The active rule blocks it at the declared leftmost gate; it cannot Ship.

Pass conditions:

- every lifecycle transition has evidence and a Gates commit;
- the next-similar fixture is blocked by the active rule version;
- known-clean false positives remain zero;
- post-activation recurrence is zero;
- no status is inferred solely from a Markdown `Status` heading.

Candidate promotion currently fails closed because Gates has no trusted,
committed replay evaluator. SC-4 is therefore blocked until the versioned
evaluator contract described by the Gates promotion rule is implemented and
independently verified.

### SC-5 — Run 50 is materially better than run 5

Use a pre-registered 50-ticket benchmark. Every consecutive five-ticket window
has the same complexity and defect-class mix. Compare the first window
(executions 1–5) with the final window (46–50); also preserve cumulative
snapshots after executions 5 and 50.

The scenario is invalid unless all 50 executions have complete identity, gate,
usage, independently verified actual-cost, escape, and terminal-state events.

Pass conditions:

- final-window first-pass gate rate is at least ten percentage points above the
  first window;
- the first window contains at least one seeded escape;
- the final window has zero escapes and at least one fewer than the first;
- median actual cost per successfully shipped ticket in the final window is at
  most 85% of the first-window median;
- all quality gains use the same fixture distribution and Gates changes are
  linked to intervening fingerprints or reviewed policy changes;
- no failed, abandoned, or awaiting-human execution is counted as shipped.

If the first window is already perfect, has zero escapes, or has unknown cost,
the benchmark cannot demonstrate material improvement and is invalid.

## Phased remediation

### Phase 0 — Stop false claims

- Mark current worker JSON and SQLite-only trends non-authoritative.
- Inventory all current ledgers and the divergent Gates branches that contain
  worker history.
- Record the current candidate/active fingerprint contradictions.
- Keep Glance on mock data only.

Exit: one migration manifest names every source and explicitly identifies
duplicates, reset run ids, missing costs, missing escape attribution, and
unrecoverable gaps.

### Phase 1 — Establish conformance and history ownership

- Land the Commons Factory evaluation schema and lifecycle checker in Gates.
- Keep the controlled valid/invalid corpus and this acceptance contract in
  Factory Test.
- Govern the append-only `factory/YYYY/MM/DD.jsonl` path in Episodic.
- Add the typed Factory Runtime history collector to Substrate memory.
- Add stable stream identity, UUIDv7 event ids, monotonic sequence allocation,
  locking, deduplication, redaction, dead-letter handling, and hash continuity.
- Define the import form for legacy ledger and worker-record events.

Exit: schema fixtures validate; duplicate-id/different-payload and sequence-gap
fixtures fail deterministically. This exit establishes stream conformance only;
it does not activate an acceptance writer or provider-authenticity claim.

### Phase 2 — Emit and reconcile

- Add a transactional Factory Runtime outbox.
- Emit events at intake, selection, stage completion, gate evaluation, human
  boundary, merge observation, Ship, escape, and completion.
- Reconcile unexported events after crash and make success claims fail closed
  while relevant evidence is pending.

Exit: crash-before-append and append-before-ack tests each produce exactly one
accepted event.

### Phase 3 — Rebuild projections and repair Gates lifecycle

- Derive worker scorecards and metrics from Episodic.
- Migrate current and divergent historical records without pretending imported
  data is complete.
- Enforce fingerprint state transitions and require executable regression tests.
- Replace hardcoded zero cost and false escape fields with truthful event data.

Exit: two independent rebuilds are identical; current known contradictions are
either repaired with evidence or remain visibly invalid.

### Phase 4 — Add missing acceptance capabilities

- Canonicalize human/system intake.
- Add verified human-merge observation and the continuation through Merge and
  Ship.
- Add the canonical trace comparator and matched worker-swap runner.
- Add fingerprint validation and next-similar replay.

Exit: SC-1 through SC-4 produce valid manifests. They may fail thresholds during
development, but they may not be invalid from missing telemetry.

### Phase 5 — Run the compounding benchmark

- Freeze the 50-ticket fixture distribution and thresholds.
- Execute SC-5 without resetting or replacing the event stream.
- Publish both passing and failing evidence.

Exit: SC-5 has a valid manifest and its observed values are reproducible from
the authoritative cursor range.

### Phase 6 — Glance

Glance implementation against real Commons data starts only after the telemetry
readiness gate below passes. UI scaffolding may use clearly labeled synthetic
fixtures earlier, but it must not be connected to mutable worker JSON or a
single Factory Runtime SQLite ledger.

## Telemetry readiness gate for Glance

All conditions are mandatory:

1. The Gates schema/check and Episodic stream path are active and versioned.
2. The historical migration manifest is complete, including divergent branches
   and reset run ids.
3. There are no duplicate event ids, sequence reuse, hash-chain gaps, or
   unexported acceptance outbox entries.
4. Projection replay is byte-identical from the same cursor and Gates commit.
5. Identity, gate result, and terminal status completeness are 100% for
   acceptance cohorts.
6. Cost and escape completeness are displayed explicitly; an incomplete metric
   renders `unknown`, not zero.
7. At least SC-1 through SC-4 can produce valid evidence manifests.
8. Every Glance card links to its event cursor, projection version, freshness,
   and evidence manifest.

Glance may display `not implemented`, `implemented`, `evidenced`, `achieved`,
`failed`, `blocked`, `invalid`, or `unknown`. It must never convert missing data
into success.
