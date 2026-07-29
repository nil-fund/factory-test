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

It does not change the legacy trigger-only Factory mode. It does not authorize
an agent to merge. A human remains the only actor allowed to perform the merge;
Factory may observe and attest that merge, then perform deterministic post-merge
verification and the configured Ship workflow.

## Authority and derivation boundaries

| Concern | Authority | May be rebuilt? | Must not become authority |
|---|---|---:|---|
| Raw Factory experience events | Episodic | No | Factory SQLite, Gates projections, Glance cache |
| Event envelope and lifecycle conformance | Gates | No | Factory producer types, Episodic directory layout |
| Acceptance scenarios, thresholds, fixtures, and harness | Factory Test | No | Runtime unit tests, dashboard labels |
| Queue, leases, workspaces, retries, delivery outbox | Factory Runtime | Yes, except an unexported outbox entry | Episodic readers |
| Fingerprints, executable checks, guardrails, promotion state | Gates | No | Factory prompts or dashboard labels |
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
Factory experience is queryable until those path, content-identity, and query
tests pass.

The target logical stream is:

```text
commons://episodic/factory/YYYY/MM/DD.jsonl
```

The schema and conformance checker must land in Gates, and the append-only
physical path must be governed in Episodic, before Factory emits production
events. This document is the Factory Test acceptance contract. It is not a
substitute for a Gates control, an approved Episodic writer, or independent
provider verification.

## Event envelope

Every line is one complete JSON object. These fields are required for every
Factory evaluation event:

| Field | Type | Contract |
|---|---|---|
| `schema_version` | string | Exactly `commons.factory.evaluation.v1` for this contract. |
| `event_id` | UUIDv7 string | Allocated once, persisted in the Factory outbox, and reused on every retry. |
| `event_type` | string | One of the event types defined below. |
| `occurred_at` | RFC 3339 timestamp | Time the represented fact occurred. |
| `recorded_at` | RFC 3339 timestamp | Time Episodic durably appended the event. Never substitutes for `occurred_at`. |
| `stream_id` | string | Stable Factory installation and managed-repository stream identifier. |
| `sequence` | integer | Strictly increasing within `stream_id`, with no reuse after reset or restore. |
| `producer` | object | `component`, `version`, `instance_id`, and `process_id`. |
| `source` | object | `kind`, stable `id`, optional `revision`, and optional immutable `uri`. |
| `correlation` | object | Stable Commons and Factory identities described below. |
| `actor` | object | `kind`, stable `id`, and agent/model fields when applicable. |
| `payload` | object | Event-specific facts. |
| `integrity` | object | `payload_sha256`, `previous_event_sha256`, and redaction policy version. |

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
| `runtime_run_id` | worker events | Factory-local run id, qualified by `stream_id`; diagnostic only. |
| `parent_event_id` | dependent events | The immediately causal event, not merely the prior line. |

### Actor fields

`actor.kind` is one of `human`, `system`, or `agent`.

- A human actor includes canonical provider identity plus `provider_evidence`
  references and hashes. Those fields are recorded claims until a separate
  Gates-owned verifier resolves them against a trust root and credential
  unavailable to Factory.
- A system actor includes the component and rule or schedule that caused the
  action.
- An agent actor includes `worker_id`, `runtime`, `model_id`,
  `worker_config_hash`, and, when exposed by the provider, model revision.

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
- `cost`: amount, ISO currency, source, and status

Cost status is one of `actual`, `estimated`, or `unknown`. Unknown is represented
by `amount: null`; it is never represented as zero. Zero is valid only when the
provider or local deterministic runner measured an actual zero cost.

#### `factory.gate.evaluated`

Required payload fields:

- `stage`, `gate_id`, and `gate_version`
- `gates_commit`
- `verdict`: `pass`, `fail`, or `escalate`
- `checks`: ordered objects containing check id, rule version, result, and evidence references
- `input_artifact_sha256`

A passing record proves that executable checks ran. The existence of Markdown
rule text alone never produces a pass.

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
Factory could self-author those fields. A separate Gates-owned verifier must
fetch and verify the provider evidence using a trust root, key, or provider
credential unavailable to Factory and its workers; reject known Factory and
worker principals; and emit a verdict bound to the exact evidence hashes.
This proves provider attribution to a governed human-controlled account, not a
physical click if that account or token could be automated. The event observes
a merge; it never instructs Factory or an agent to merge.

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

#### `factory.pipeline.completed`

Required payload fields:

- `outcome`: `shipped`, `rolled_back`, `failed`, or `abandoned`
- `terminal_stage`
- `ship_event_id`, required only for `shipped`
- `total_latency_ms`
- `total_cost`, with the same honesty rules as stage cost

`awaiting_human` is not completion.

#### `factory.escape.observed`

Required payload fields:

- `release_event_id`
- `incident_ref`
- `signature`
- `severity`
- `detected_at`
- `attributed_stage_attempt_ids`

An internal worker failure is not an escape. An escape is a defect that passed
the applicable gates and reached a shipped release.

#### `factory.fingerprint.transitioned`

Required payload fields:

- `fingerprint_id`
- `from_status` and `to_status`
- `gates_commit`
- `reproducer_ref`
- `regression_test_ref`
- `validation_evidence_event_ids`

Allowed transitions are `candidate -> validated -> active -> generalized`.
There is no direct `candidate -> active` transition.

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

## Stream invariants

1. **Append only.** Existing lines are never edited, reordered, or deleted.
   Corrections append a new event with `supersedes_event_id` and a reason.
2. **Stable identity.** An event id is allocated before delivery and is reused
   across crashes, retries, reconciliations, and process boundaries.
3. **Idempotence.** Appending an existing event id with the same payload hash is
   a no-op. The same id with a different hash is a hard integrity error.
4. **Single order per stream.** `(stream_id, sequence)` is unique and strictly
   increasing. A reset creates neither a new sequence origin nor reused run ids.
5. **Hash continuity.** Each event commits to the prior accepted event in its
   stream. A migration event may begin a new explicitly named imported stream.
6. **Atomic intent, recoverable delivery.** The Factory ledger may hold a
   transactional outbox, but a success claim is blocked while a relevant outbox
   entry is unexported. The outbox is a buffer, not history authority.
7. **Truthful nulls.** Unknown cost, tokens, model, or attribution remain null
   with an explicit status. They are never silently changed to zero or a
   configured default.
8. **Secret redaction.** Redaction runs before persistence. A rejected event goes
   to a dead-letter queue with no secret-bearing payload in its diagnostic.
9. **Complete causality.** Every gate event references a completed stage attempt;
   every shipped completion references a verified human merge and Ship event;
   every active fingerprint references validation and a regression test.
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
    unavailable to Factory.

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

Factory SQLite remains the operational source for queue recovery and live
inspection. It is not the source for cross-reset or cross-machine quality trends.

## Evidence manifest

Each acceptance execution produces a signed or hashed evidence manifest with:

- `contract_version` and `scenario_id`;
- exact Factory, Episodic, Gates, Substrate, fixture, workflow, and managed-repo commits;
- event stream ids, inclusive sequence ranges, event count, and terminal hash;
- fixture ids and pre-registered random seed, if any;
- derived projection artifact URI and hash;
- each assertion, observed value, threshold, and result;
- verifier identity and whether it is independent of the producer;
- provider-verification bundle URI/hash, trust-root identity/version, and the
  Gates verdict bound to the merge event;
- start/end timestamps, result, and explicit caveats.

The manifest result is one of `passed`, `failed`, `blocked`, or `invalid`.
Missing or incomplete telemetry makes a run `invalid`, not failed and never
passed.

## Acceptance scenarios

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
- workflow, Gates, Factory, and Substrate commits;
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

1. Factory emits `pipeline.awaiting_human`.
2. Factory has no usable merge credential or automatic-merge action.
3. Assert that no Merge or Ship event exists.
4. A designated human merges through the provider.
5. A Gates-owned verifier resolves and verifies the provider evidence with
   credentials or keys unavailable to Factory.
6. Factory appends `merge.attested` only with that bound verdict.
7. Merge performs post-merge verification against the exact merge commit.
8. Ship produces a release record, rollback handle, and monitoring evidence.
9. The pipeline completes with outcome `shipped`.

Pass conditions:

- the stage order is exactly the canonical eight stages, once each on the
  first-pass fixture;
- the merge commit contains the accepted change and passes the configured
  post-merge checks;
- the merge actor is verified human and distinct from Factory credentials;
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

### SC-5 — Run 50 is materially better than run 5

Use a pre-registered 50-ticket benchmark. Every consecutive five-ticket window
has the same complexity and defect-class mix. Compare the first window
(executions 1–5) with the final window (46–50); also preserve cumulative
snapshots after executions 5 and 50.

The scenario is invalid unless all 50 executions have complete identity, gate,
usage, actual-cost, escape, and terminal-state events.

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

- Land the Factory evaluation schema and lifecycle checker in Gates.
- Keep the controlled valid/invalid corpus and this acceptance contract in
  Factory Test.
- Govern the append-only `factory/YYYY/MM/DD.jsonl` path in Episodic.
- Add the typed Factory history collector to Substrate memory.
- Add stable stream identity, UUIDv7 event ids, monotonic sequence allocation,
  locking, deduplication, redaction, dead-letter handling, and hash continuity.
- Define the import form for legacy ledger and worker-record events.

Exit: schema fixtures validate; duplicate-id/different-payload and sequence-gap
fixtures fail deterministically. This exit establishes stream conformance only;
it does not activate an acceptance writer or provider-authenticity claim.

### Phase 2 — Emit and reconcile

- Add a transactional Factory outbox.
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
single Factory SQLite ledger.

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
