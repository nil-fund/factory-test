# Verify a pull request

## Work order context

You are working on stage **verify** of the SDLC pipeline. The following context has been assembled for you:

- **Prior stage artifacts**: injected in your work order context under "Prior stage artifacts" — the changeset artifact, the spec artifact, and the triage artifact are there. Do not rely on reading artifact files from disk; the injected context is the canonical handoff mechanism. You must use all three before writing evidence.
- **Gate criteria**: the following checks will be applied to your output:
  - `repro-from-clean` — a fresh checkout reproduces the claimed fix; checkout the PR branch, run the tests, they pass
  - `security-scan` — no new CVEs, secrets, or unsafe patterns introduced; scanner output has no new findings
- **Fingerprints**: active bug fingerprints for verify are in your context — learn from past verification escapes (clean-checkout-only bugs, missing security scans, unvetted deps)
- **Attempt history**: if this is a retry, prior failure reasons are in your context

## Claim the work

If the issue carries this stage's trigger label (`factory:verify`), remove it
so the source trigger cannot refire. In pipeline mode the daemon advances
stages itself; never apply any label to move the ticket forward.

## Output format

Your output should conform to the JSON schema at
`/Users/jai/Desktop/gates/schemas/evidence.json` (local gates repo checkout).
Output your artifact as valid JSON wrapped in a fenced code block tagged ```json

The evidence artifact must include at minimum:
- `id`: unique identifier for this evidence pack
- `changeset_id`: ID of the changeset being verified (links to prior stage)
- `spec_id`: ID of the spec whose acceptance criteria are being checked
- `criterion_results`: array of objects, each with `criterion_id` (string), `passed` (boolean), and `evidence` (string with logs, test output, or reproduction steps)
- `generated_tests`: array of test code strings generated for this changeset
- `adversarial_probes`: array of probe strings attempted against the changeset
- `static_analysis`: object with results from linters, type checkers, security scanners
- `worker_id`: ID of the verifying worker (must differ from the changeset worker — separation of duties)
- `created_at`: ISO 8601 timestamp

## Read prior stage artifacts

From the injected prior-stage artifacts:
1. triage artifact — understand the risk tier and route
2. spec artifact — understand the acceptance criteria you must verify
3. changeset artifact — understand the diff and traceability map

The changeset's `traceability_map` links each diff hunk to an acceptance criterion. You must verify that each criterion is actually met by the corresponding code — do not trust the traceability map blindly; verify independently.

## Reproduce from clean

Check out the PR branch in a fresh clone (no cached state, no stale build artifacts). Run the spec's acceptance tests. All must pass. If tests pass in the worker's environment but fail in your clean checkout, the `repro-from-clean` gate check fails — the fix depends on uncommitted state and is not real.

## Security scan

Run the security scanner (`cargo audit`, `npm audit`, `gitleaks`, `semgrep`, or the repository's configured scanner — for this Python-only test repo, read the diff for secrets and unsafe patterns). Compare findings against the baseline (known findings from before the change). Any new finding — CVE, leaked secret, unsafe code pattern — fails the `security-scan` gate check. Record results in the `static_analysis` field of the evidence.

## Dependency audit

Diff the dependency manifests against the target branch. For each new dependency, verify a review record exists (audit, license, necessity). If any new dependency lacks a review record, note it in the evidence.

## Adversarial probes

Attempt to break the implementation. Generate adversarial inputs, edge cases, and stress conditions. Record probes attempted and results in the `adversarial_probes` field. The goal is to find weaknesses the implementer missed — you are the independent verifier, not a rubber stamp.

## Separation of duties

You must be a different worker than the one who produced the changeset. The `worker_id` in your evidence must differ from the changeset's worker. If you are the same worker, note it in the evidence — with a single-worker pool this is expected; record it explicitly so a human can judge.

## Hand off

Comment on the issue with the verification verdict and the evidence summary.
Do not merge the pull request and do not apply any label: in pipeline mode the
daemon advances the ticket to review when the verify gate passes.
