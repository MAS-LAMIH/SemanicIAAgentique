# V3 preservation and recovery

V3 remains the complete action-contract research prototype. V4 is a separate
proposal, not a replacement candidate or an amendment of the frozen protocol.
This branch adds documentation and new recovery evidence only. M4.4/M4.5 records,
original source, tutorial, archives, manifests, tags and approval fields are retained.
No scientific approval or Provider C access follows from this preservation.

## Exact identities

| Item | Preserved identity or path |
| --- | --- |
| V3 candidate commit | `752da7b8de85dd38c7eee30a101b786ea4743821` |
| Implementation commit | `2d264169a5ec363b78d4bf78b3f40e82d7b59f85` |
| Candidate tag | `candidate/milestone-4.3-pre-freeze` (peels to candidate commit) |
| Earlier retained candidate tag | `candidate/milestone-4.1-pre-freeze` (historical V2, not V3) |
| V3 manifest | `docs/SCIENTIFIC_FREEZE_MANIFEST_V3.json` |
| Manifest SHA-256 | `53049d7921c31e7f3081606d5f2c6ca327eccf91fbab42152826655cbeeda352` |
| Manifest source-tree digest | `bd14f5b4839ac7a49e1bfca01b1adff29fbde6f17497723fac7186cfb6137368` |
| Source archive | `docs/artifacts/milestone4_3/candidate-source-v3.tar.gz` |
| Archive SHA-256 | `b659c852d78ff2bad99f6ec743b5b0bd0a16ad88bbcd20af5e8e6e091089c27d` |
| Retained wheel | `docs/artifacts/milestone4_3/tutorieliaagentique-0.1.0-py3-none-any.whl` |
| Wheel SHA-256 | `538f5acdb7366300f81166232f8877c31c9260e6dbb7dbb226150ea35621cc1b` |
| Dependency pins | `docs/artifacts/milestone4_3/evaluation-requirements.txt` |
| Packaging/build requirements | Candidate `pyproject.toml`: Python >=3.11, hatchling build backend |
| Review and operational backup revision | `ee3aa0bac538bf71b2acd1d26af22a1bcb913e60` (includes M4.4 and M4.5) |

The dependency file pins the eight evaluation/runtime libraries; it is not a
complete platform/build lock: Python, OS, hatchling and dependency artifact hashes
are not locked there. Recorded validation used Python 3.12.14. Preserve the wheel
and recorded environment as well as the pins; do not describe this as hermetic.
A clone containing these objects is a recoverable repository copy, not a promise
of an independently administered off-site backup.

## Restore and run

From this repository, extract the exact candidate to a new directory. This avoids
switching or overwriting the active V4 checkout. Use a fresh destination each time.

```sh
mkdir /tmp/semanic-v3-recovery
git archive 752da7b8de85dd38c7eee30a101b786ea4743821 | tar -x -C /tmp/semanic-v3-recovery
cd /tmp/semanic-v3-recovery
python3 scripts/candidate_v3.py --verify-history
python3 scripts/candidate_v3.py --verify
uv venv --python 3.12 /tmp/semanic-v3-env
UV_CACHE_DIR=/workspace/.cache/uv uv pip install --python /tmp/semanic-v3-env/bin/python \
  -r docs/artifacts/milestone4_3/evaluation-requirements.txt \
  docs/artifacts/milestone4_3/tutorieliaagentique-0.1.0-py3-none-any.whl
/tmp/semanic-v3-env/bin/python -m unittest discover -s tests/semantic_action -v
/tmp/semanic-v3-env/bin/python -m semantic_action.evaluation \
  --provider a --condition B --task D01 --output-dir /tmp/v3-single-fresh
/tmp/semanic-v3-env/bin/python -m semantic_action.multistep_evaluation \
  --provider b --condition C --task M09 --output-dir /tmp/v3-chain-fresh
```

The 87-test suite starts its own loopback fixtures; no external API, model or
Provider C is required. Output directories must not already exist. For editable
source validation, install `-e .` instead of the wheel in a separate environment.
For the independent archive route, extract `candidate-source-v3.tar.gz` into a
new directory and run the same suite with that directory's `src` on PYTHONPATH,
or install that restored source. The archive contains the 248 manifest-listed
source members, not the later manifest itself or the full historical evidence
bundle. Use the exact Git candidate for the complete verifier and retained
artifacts; the manifest verifies the archive member bytes separately.

Do not run `--prepare`, `--archive-only`, `scripts/validate_v3.py`, or historical
pilot-recording scripts against the preserved checkout: those write old evidence
locations. Read-only verification should run in the exact extraction, because
additional V4/review documents intentionally fall outside V3's closed inventory.
For the complete M4.4/M4.5 working backup, extract commit `ee3aa0b` into another
fresh directory; do not confuse that revision with the V3 implementation identity.

## Evidence retained and recovery check

- V3: `docs/MILESTONE_3.md`, `docs/MILESTONE_4_FREEZE_AUDIT.md`,
  `docs/artifacts/milestone4_3/validation-results.json`, `pilot-final/`, final
  source/wheel/restored logs and `events.jsonl`; earlier manifests remain present.
- M4.4: `docs/MILESTONE_4_4.md`, its semantic review, cost/evaluation/custody
  proposals, `docs/SCIENTIFIC_FREEZE_DECISION_V3.json`, and
  `docs/artifacts/milestone4_4/`.
- M4.5: `docs/MILESTONE_4_5_PREFLIGHT.md`,
  `docs/COMBINED_DRIVER_PREFLIGHT_REPORT.md`, `preflight/`, and
  `docs/artifacts/milestone4_5/` (180 protected attempts, separately labeled
  controls/references and original command evidence).

Fresh recovery verification for this proposal is recorded in
[recovery-verification.json](artifacts/v4_proposal/recovery-verification.json)
and [restored-tests.log](artifacts/v4_proposal/restored-tests.log). It verifies
the tag, exact candidate and history, all 248 archive members, retained artifact
hashes, and a new restored-source test execution: **87/87 passed in 203.073 seconds**.
All 7,348 pre-existing tracked files were unchanged; all 28 retained-wheel runtime
source members matched V3. The source test uses the existing
Python environment's dependencies, explicitly recorded in the JSON; it is not a
new installed-wheel test. Prior source/wheel/restored 87-test results remain
historical evidence, unchanged. Final comparison checks every one of the 7,348
pre-existing tracked files. No new freeze manifest or approval process is created.
