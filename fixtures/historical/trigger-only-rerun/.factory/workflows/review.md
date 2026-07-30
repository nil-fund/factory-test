# Review a verified pull request

## Work order context

You are working on stage **review** of the SDLC pipeline. The following context has been assembled for you:

- **Prior stage artifacts**: injected in your work order context under "Prior stage artifacts" — the evidence artifact, the changeset artifact, the spec artifact, and the triage artifact are there. Do not rely on reading artifact files from disk; the injected context is the canonical handoff mechanism. You must use all prior artifacts before issuing a verdict.
- **Gate criteria**: the following checks will be applied to your output:
  - `spec-satisfied` — each acceptance criterion from the spec is met by the changeset
  - `ci-green` — CI is green on the PR head commit (or no CI is configured and the local verification evidence substitutes for it — say which)
- **Fingerprints**: active bug fingerprints for review are in your context — learn from past review escapes (rubber-stamping, unresolved comments, untracked spec drift)
- **Attempt history**: if this is a retry, prior failure reasons are in your context

## Claim the work

If the issue carries this stage's trigger label (`factory:review`), remove it
so the source trigger cannot refire. In pipeline mode the daemon advances
stages itself; never apply any label to move the ticket forward.

## Output format

Your output should conform to the JSON schema at
`/Users/jai/Desktop/gates/schemas/verdict.json` (local gates repo checkout).
Output your artifact as valid JSON wrapped in a fenced code block tagged ```json

The verdict artifact must include at minimum:
- `id`: unique identifier for this verdict
- `changeset_id`: ID of the changeset being verdicted (links to prior stage)
- `evidence_id`: ID of the evidence pack this verdict is based on
- `decision`: "approve" or "reject"
- `reasons`: array of objects, each with `criterion_id` (string), `finding` (string), and `severity` ("info", "warning", or "error")
- `reviewer_id`: ID of the reviewer issuing this verdict
- `created_at`: ISO 8601 timestamp
- `rationale`: written rationale for the decision, > 50 characters, referencing specific criteria, test results, or design decisions

## Read prior stage artifacts

From the injected prior-stage artifacts:
1. triage artifact — understand the risk tier to calibrate review depth
2. spec artifact — understand the acceptance criteria the changeset must satisfy
3. changeset artifact — understand the diff, rationale, and traceability map
4. evidence artifact — understand the verification results, adversarial probes, and static analysis

You are reviewing the verifier's work, not re-implementing. Focus on whether the evidence convincingly demonstrates the spec is satisfied and whether the changeset is safe to merge.

## Write a real rationale

The `rationale` field must contain more than 50 characters of substantive reasoning. "LGTM" or "Looks good" is not a rationale. Explain *why* the changeset is acceptable: reference specific criteria that passed, evidence that convinced you, and any residual risks. The rationale is the audit trail that shows the review actually happened.

## Check spec drift

Compare the changeset against the spec. If the implementation does anything the spec didn't call for, or omits something the spec required, that's drift. The changeset should have a `drift_explanation` field. If drift exists and no explanation is present, record it as a finding. If the implementation matches the spec exactly, drift is nil.

## Issue the verdict

Based on the evidence, the changeset, the spec, and your own review:
- **Approve**: the changeset satisfies all acceptance criteria, evidence is convincing, no unresolved issues remain.
- **Reject**: specific criteria are not met, evidence is insufficient, or the changeset introduces unacceptable risk.

Provide reasons tied to specific criterion IDs. Use severity levels: `info` (minor observations), `warning` (should fix but not blocking), `error` (must fix before merge).

## Halt for the human

Comment on the issue with the verdict, rationale summary, and the PR link.
**Never merge the pull request, never enable auto-merge, and never apply any
label.** The pipeline halts after this stage by design (D30): a human merges
and ships.
