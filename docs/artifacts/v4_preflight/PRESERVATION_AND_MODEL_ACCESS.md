# Preflight preservation and model-access diagnosis

This archive preserves the synthetic preflight from implementation/protocol base `285e7a7f107639ac9d3ba834692c08696367189a`. It is technical preparation, not a prospective integration or confirmatory result. The original README and scripts are historical evidence: their external absolute paths are unchanged. Do not rerun them against this archive; scripts create files and some refuse existing directories.

## Preservation

All 36 regular files in the original `evidence-sha256.json` were copied byte-for-byte, along with the original manifest. Every original and preserved file matched that manifest. Three trailing-whitespace lines in captured `codex-help.txt` are intentionally retained; they are the only `git diff --check` warnings. See `preservation-verification.json`. CLI home/state, authentication/configuration files, directories not in the manifest, and the escaping symlink were excluded. Contents were reviewed as synthetic canaries, visible A/B fixtures, process commands/results, CLI help and error logs; an additional credential-pattern scan found no flags. No full environment, credential, identity-manifest or managed-status dump is retained. Workspace paths, ephemeral loopback ports, thread IDs and error timestamps are retained as non-secret reproducibility metadata.

To verify the original evidence from repository root (read-only):

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, json
p = Path('docs/artifacts/v4_preflight')
d = json.loads((p / 'evidence-sha256.json').read_text())
for name, expected in d.items():
    f = p / name
    assert not f.is_symlink() and hashlib.sha256(f.read_bytes()).hexdigest() == expected, name
print(f'{len(d)} original evidence hashes verified')
PY
```

The original manifest intentionally does not cover the newly added preservation/diagnosis files. `preservation-sha256.json` covers the complete retained set except itself.

## Supported access checks and blocker

Checked 2026-10-28 UTC. Commands/results are in `model-access-diagnosis.json`.

- Managed status is current, connected and policy enforced. `api.openai.com` is not allowed. No model capability, credential binding, runtime-variable binding or alternative outbound identity is advertised.
- The non-secret identity manifest has version 1 and zero connections.
- `codex login status` exits 0 and reports `Logged in using ChatGPT`. This confirms a local configured login, not credential validity, model entitlement, or a supported means to authenticate isolated workers. No login file was read or copied.
- A credential-free HEAD request to `https://api.openai.com/v1/responses`, using inherited proxy settings and normal TLS verification, exits 56: `CONNECT tunnel failed, response 403`. HTTP status is 000 and CONNECT status 403. The request fails before origin authentication; this is not evidence of an invalid login.

The earlier CLI failure in `codex-writable-*` is consistent with this enforced network denial. Its separate writable home deliberately ignored user config, so its default endpoint is not proof that the environment authorizes that endpoint. No bypass, policy/configuration edit, new credential or additional inference attempt was made. No approved usable endpoint/authentication combination can currently be verified. Stop model testing here.

The administrator must enable an approved route to the intended model service through the supported environment policy/configuration workflow, or supply an approved alternative endpoint with supported CLI configuration. They must also confirm authorized noninteractive authentication for the selected model inside isolated workers without copying existing login files. Writable per-worker CLI state, proxy and CA setup must be supplied. After those prerequisites, run one harmless inference inside the pinned worker image and verify completion plus usage export. Do not treat a host-side CLI login as an isolated-worker readiness test.

## Readiness

Original container boundary and visible A/B native-evaluation smoke evidence is preserved. Successful model inference and token telemetry remain **blocked/unverified**; absent usage stays null. Model compute time, live quota enforcement and combined CLI-in-worker operation remain unverified. Process elapsed time, exit codes and failure logs were measured, as recorded originally. No integrations, Provider C materials, hidden answers, V4 runtime or existing pilot evidence were touched. Nothing was pushed or merged. This documentation-only local commit does not create a new tested implementation candidate or grant execution/unsealing approval.
