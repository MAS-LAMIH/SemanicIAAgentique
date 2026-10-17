# Milestone 4.4 — independent scientific freeze audit preparation

Status: **review preparation complete; scientific approval pending; Provider C sealed**.
This is documentation and verification of existing V3, not a new implementation
candidate, independent human review, confirmatory experiment or unsealing decision.
No generic code, contract, test, historical evidence or candidate tag/manifest changed.
No push or merge was performed. Working branch: `codex/milestone-4-4-audit`.

## Exact immutable identity

| Item | Verified identity |
| --- | --- |
| Candidate/evidence commit | `752da7b8de85dd38c7eee30a101b786ea4743821` |
| Implementation commit | `2d264169a5ec363b78d4bf78b3f40e82d7b59f85` |
| Annotated local tag | `candidate/milestone-4.3-pre-freeze`, peeled to candidate commit |
| [V3 manifest](SCIENTIFIC_FREEZE_MANIFEST_V3.json) SHA-256 | `53049d7921c31e7f3081606d5f2c6ca327eccf91fbab42152826655cbeeda352` |
| Source-tree SHA-256 | `bd14f5b4839ac7a49e1bfca01b1adff29fbde6f17497723fac7186cfb6137368` |
| [Retained source archive](artifacts/milestone4_3/candidate-source-v3.tar.gz) SHA-256 | `b659c852d78ff2bad99f6ec743b5b0bd0a16ad88bbcd20af5e8e6e091089c27d` |
| [Retained wheel](artifacts/milestone4_3/tutorieliaagentique-0.1.0-py3-none-any.whl) SHA-256 | `538f5acdb7366300f81166232f8877c31c9260e6dbb7dbb226150ea35621cc1b` |

Entry was clean at candidate commit on `codex/milestone-4-3-multistep`. The new audit
branch contains only review documents/evidence; no implementation commit/tag was created.
All 2,231 candidate-tracked files were hashed before work and remain unchanged. The
manifest's 248 source files and 1,984 artifacts verify, including earlier candidates
and M4.2 approval records. The existing annotated tag is not investigator approval
or a detached scientific signature.

## Actual new verification

Fresh isolated copies were created using `git archive` of the candidate commit and
extraction of the exact retained V3 source tarball. Three fresh Python environments
were installed offline from the existing cache and pinned evaluation requirements:
source editable install from the exact candidate; installation of the retained wheel;
and source installation rebuilt from the extracted archive. Installed paths and all
nine package versions match the recorded runtime environment (Python 3.12.14).

| M4.4 command ID | New result | Runner duration | Evidence |
| --- | --- | --- | --- |
| `candidate_history` | exit 0; 134 preserved files, V2 archive 104 members, M4 archive 74 members/14 historic files | command runtime in JSON | [history log](artifacts/milestone4_4/candidate_history.log) |
| `candidate_verify` | exit 0; V3 source/artifacts valid | command runtime in JSON | [candidate log](artifacts/milestone4_4/candidate_verify.log) |
| `source_tests` | 87 tests, exit 0, no failures/errors/skips | 208.762 s | [source log](artifacts/milestone4_4/source_tests.log) |
| `wheel_tests` | 87 tests, exit 0, no failures/errors/skips | 209.282 s | [wheel log](artifacts/milestone4_4/wheel_tests.log) |
| `restored_tests` | 87 tests, exit 0, no failures/errors/skips | 207.014 s | [restored log](artifacts/milestone4_4/restored_tests.log) |
| `fresh_pilot` | exit 0; no diagnostic failures | command runtime in JSON | [pilot log](artifacts/milestone4_4/fresh_pilot.log), [fresh machine results](artifacts/milestone4_4/pilot-reproduction/pilot-results.json) |
| `restored_verify`, `source_post_tests_verify` | exit 0 after tests; frozen files remain valid | command runtime in JSON | [restored verification](artifacts/milestone4_4/restored_verify.log), [post-test verification](artifacts/milestone4_4/source_post_tests_verify.log) |
| `dependency_check` | exit 0 | command runtime in JSON | [dependency consistency](artifacts/milestone4_4/dependency_check.log) |
| `expanded_checkout_scope` | expected exit 1: new review documents lie outside V3's source inventory | command runtime in JSON | [scope rejection](artifacts/milestone4_4/expanded_checkout_scope.log) |

The expected last result is **not an implementation defect or an identity mismatch**.
V3 verifies its exact candidate, not an enlarged documentation working tree. Keep using
the exact Git snapshot/restored candidate for full coverage verification; do not edit
`source_paths`, regenerate V3 or exclude unknown engine files to make an expanded
checkout pass. Historical verification still applies to preserved artifact bytes.
No unexpected command/test failure was observed in this audit.

[verification-results.json](artifacts/milestone4_4/verification-results.json) records exact
commands, working directories, exit codes, expected-status classification, runtimes,
log hashes and environment pointers. [environments.json](artifacts/milestone4_4/environments.json)
records module locations, Python/platform and dependency inventories. Source/wheel/
archive runs are independent installations, not independent providers or human reviewers.

## Final pilot provenance, not the 86-test intermediate

[provenance-assessment.json](artifacts/milestone4_4/provenance-assessment.json) confirms:

- The original final suite IDs select 87 tests with `original_reported_id` values
  `source_after_relation`, `wheel_after_relation`, `restored_after_relation` and logs
  containing the synthetic curator-owned relation extension test.
- Original `validation.pilot_results_path` is `pilot-final/pilot-results.json`; the
  retained command is `retained_pilot_after_relation`, not the pre-extension `pilot/`.
- All 28 packaged semantic-action wheel members match frozen source bytes; the wheel
  contains `ChainInterpretation`. The exact source archive/digest matches the manifest.
- Fresh reproduction used the exact candidate source and reproduced all 71 indexed
  pilot attempt rows with identical normalized summaries/statuses: 60 main matrix
  runs, six positive reset repetitions, three in-flight timeouts, one HTTP timeout
  and one rejected reset. The separate isolated-stall control also passed.

These observations establish consistency of the final evidence with the final 87-test
candidate. They do not provide a signed per-process historical source attestation or
independent human authorship. Hashing/reproduction cannot retrospectively establish
organizational independence or blinding. Earlier 86-test logs/archives remain preserved
and explicitly excluded from final-stage selection.

## Review documents and decision gates

1. [INDEPENDENT_SEMANTIC_REVIEW_V3.md](INDEPENDENT_SEMANTIC_REVIEW_V3.md): source/test/
   evidence matrix; reviewer conclusions and signature blanks remain unfilled.
2. [PROSPECTIVE_COST_POLICY_V3.md](PROSPECTIVE_COST_POLICY_V3.md): proposed P1 standalone
   cold start, P2 joint deployment and P3 amortization sensitivities, separate resources,
   missingness and provider-unit rules.
3. [CONFIRMATORY_EVALUATION_PROTOCOL_V3.md](CONFIRMATORY_EVALUATION_PROTOCOL_V3.md):
   proposed task-family/parameter lock, metrics, ordering, adjudication, cost collection,
   stopping and small-provider analysis; no confirmatory results claimed.
4. [PROVIDER_C_CUSTODY_AND_ROLES.md](PROVIDER_C_CUSTODY_AND_ROLES.md): independent author,
   curator, integrator, reviewer and investigator duties/access, exposure and conflicts.
5. [SCIENTIFIC_FREEZE_DECISION_V3.json](SCIENTIFIC_FREEZE_DECISION_V3.json): all eight
   approval gates pending, all human identities/signatures/approval timestamps null;
   separate later unsealing decision.
6. This report and the separate M4.4 evidence directory.

The decision file's document digests identify this review revision. They do not replace
the immutable implementation/archive/manifest digests. No new V3 candidate is generated
merely because review documentation was added.

## Decisions and methodological blockers

- Obtain actual independent semantic and native-oracle reviews, signed against exact
  artifacts. Shared authoring of fixtures, mappings, tasks and expected results is
  still a common-mode risk. The software observer is separate from subject mappings,
  not independent human curation or cryptographic service attestation.
- Approve P1 scope/starting point and evaluation-overhead boundary, P2 weights, P3
  assumptions, prospective timers/assistance, budget/censoring and missingness policy.
  Missing historical human costs remain null and prevent complete empirical cold-start
  totals; approving future collection does not reconstruct them.
- Resolve the public-task/hidden-task contradiction. The exact 30 public families
  (D01–D20, M01–M10) are known to the author. Approve independently sealed instances
  under those families before release, or explicitly limit the claim to public-task
  provider holdout and register that scope deviation. No hidden task answers are
  generated or inspected here; the custody manifest remains pending.
- Approve proposed 3 repetitions, seeds 20271017/18/19, actual schedule/roster hashes,
  budgets, correctness thresholds, outcome denominators, stopping/restart and analysis.
  One held-out provider is n=1; repetitions do not create provider-level evidence.
- Establish named independent roles, custody and exposure/conflict declarations.
  Public fixtures and prior author knowledge cannot be made blind retrospectively.
- Validate/approve a provider-local evaluation driver applying frozen timeout/reset
  rules to the whole task set. The multi-step supervisor is demonstrated; the public
  single-action runner has no built-in outer supervisor. The public runners are A/B-only;
  future additions must use frozen interfaces and supported semantics. Loopback-only
  transport and bounded event chains may leave tasks unsupported. No generic repair
  after unsealing can retain the original confirmatory baseline.
- Investigator must separately approve V3 and, only after prerequisites are satisfied,
  decide whether to authorize a named, bounded release. No signature or approval is
  supplied by this assistant.

These are disclosed scope/design/preflight and human-review gates, not silently fixed
code defects. The proposed protocol cannot honestly be called fully locked or ready
for confirmation while task custody, schedule/roster, reviews and signatures are null.
Preparation is ready for investigator review; scientific freeze approval and release
remain pending.

## Reproduction without changing V3

```sh
# Verify from the exact candidate, independent of the new review files.
audit_candidate=$(mktemp -d /tmp/m44-candidate.XXXXXX)
git archive 752da7b8de85dd38c7eee30a101b786ea4743821 | tar -x -C "$audit_candidate"
python3 "$audit_candidate/scripts/candidate_v3.py" --verify-history
python3 "$audit_candidate/scripts/candidate_v3.py" --verify

# Fresh source installation, then the full 87-test suite.
python3 -m venv /tmp/m44-new-source-env
/tmp/m44-new-source-env/bin/python -m pip install -r "$audit_candidate/docs/artifacts/milestone4_3/evaluation-requirements.txt" -e "$audit_candidate"
cd "$audit_candidate"
/tmp/m44-new-source-env/bin/python -m unittest discover -s tests/semantic_action -v
```

Exact actual offline `uv` commands for all three environments, wheel and source archive
restoration are recorded in the command JSON/logs. Use fresh paths for additional
runs. A restored tree needs the immutable final V3 manifest and full M4.3 artifact
directory copied in to run its complete verifier; neither is regenerated. No external
API/model/credentials are needed for these controlled checks.

[New audit resource records](artifacts/milestone4_4/resource-summary.json) contain actual
automation and bounded elapsed observations, not human labor or experimental integration
costs. Tool/model waits and human-active/supervision remain null. Initial uninstrumented
inspection and final serialization/reporting are excluded from the elapsed scope.
All old resource ledgers remain immutable; nested pilot parent duration is metadata,
with child runtimes accounted separately. No historical cost is invented.
