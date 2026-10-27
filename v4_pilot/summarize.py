"""Read-only comparison/accounting of retained pilot evidence; no answer generation."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
from .driver import ROOT, save

AREA = ROOT / 'docs/artifacts/v4_pilot'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalized(row, directory):
    invocation = row['invocation']
    runtime = ({key: value for key, value in invocation.items() if key != 'diagnostics'} if invocation else None)
    calls = json.loads((directory / 'http-calls.json').read_text()) if (directory / 'http-calls.json').exists() else []
    state = {key:value for key,value in row['native_after'].items() if key != 'observed_at'}
    return dict(summary=row['summary'], invocation=runtime, native=row['native'], native_state=state,
                calls=calls, uncertainty_at_stop=row['uncertain_remote_outcome_at_stop'],
                uncertain_after_observation=row['state_uncertain_after_observation'], creation_accepted=row['creation_accepted'])


def main():
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--run', type=Path, required=True)
    args = parser.parse_args(); run = args.run.resolve()
    rows = json.loads((run / 'attempt-inventory.json').read_text())
    differences, incomplete, source_bundles, pids = [], [], set(), []
    for row in rows:
        directory = run / row['path']
        for required in ('evaluation.json','reset.json','curator-expectation.json','subject-input.json',
                         'supervision.json','subject.stdout','subject.stderr'):
            if not (directory / required).is_file(): incomplete.append(str(directory / required))
        if not json.loads((directory / 'reset.json').read_text())['passed']: incomplete.append(row['path']+': reset failed')
        if row['process']['process_alive_after_stop']: incomplete.append(row['path']+': live subject')
        if row['native']['post_attempts'] and not (directory/'native-transitions.json').exists(): incomplete.append(row['path']+': missing native journal')
        source_bundles.add(row['metadata']['reproducibility']['source_bundle_sha256']); pids.append(row['process']['pid'])
    for task in range(1,17):
        for provider in ('a','b'):
            group = [r for r in rows if r['task_id']==f'T{task:02d}' and r['provider']==provider]
            if {r['condition'] for r in group} != set('ABC') or len(group)!=3:
                incomplete.append(f'T{task:02d}-{provider}: incomplete conditions'); continue
            comparable = [normalized(r,run/r['path']) for r in group]
            if any(value!=comparable[0] for value in comparable[1:]): differences.append([f'T{task:02d}',provider])
    before = json.loads((AREA/'start-state.json').read_text())['files']
    allowed = {'src/semantic_capability_v4/http.py','src/semantic_capability_v4/invoke.py','tests/v4/test_capabilities.py'}
    changed = [p for p,h in before.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    forbidden_changes = sorted(set(changed)-allowed)
    core = sorted((ROOT/'src/semantic_capability_v4').glob('*.py'))
    baseline_shared = [ROOT/'src/api_local_v4/__init__.py', ROOT/'src/api_local_v4/common.py']
    adapters = {p:ROOT/f'src/api_local_v4/{p}.py' for p in 'ab'}
    evaluation = sorted((ROOT/'v4_pilot').glob('*.py'))
    count = lambda files: {str(p.relative_to(ROOT)):len(p.read_text().splitlines()) for p in files}
    costs = {p.stem:json.loads(p.read_text()) for p in AREA.glob('*.json')
             if isinstance(json.loads(p.read_text()),dict) and 'automated_runtime_seconds' in json.loads(p.read_text())}
    controls = json.loads((run/'reset-controls.json').read_text())
    safety = dict(reset_controls=len(controls),reset_rejected=sum(r['status']=='RESET_REJECTED' and not r['subject_launched'] for r in controls),
                  timeouts=sum(r['process']['status']=='TIMEOUT' for r in rows),
                  uncertain_at_stop=sum(r['uncertain_remote_outcome_at_stop'] for r in rows),
                  unsettled_after_observation=sum(r['state_uncertain_after_observation'] for r in rows),
                  timeout_accepted=[r['path'] for r in rows if r['process']['status']=='TIMEOUT' and r['creation_accepted']])
    good = (len(rows)==96 and all(r['diagnostic_passed'] for r in rows) and not differences and not incomplete and
            not forbidden_changes and len(set(pids))==96 and len(source_bundles)==1 and safety['reset_rejected']==6 and not safety['timeout_accepted'])
    summary = dict(verdict='PASS' if good else 'FAIL',base_commit=json.loads((AREA/'start-state.json').read_text())['base_commit'],
        planned=96,executed=len(rows),diagnostic_passed=sum(r['diagnostic_passed'] for r in rows),
        classification_counts=dict(Counter(r['summary']['classification'] for r in rows)),
        condition_counts=dict(Counter(r['condition'] for r in rows)),
        creation_counts_by_condition={c:sum(r['creation_accepted'] for r in rows if r['condition']==c) for c in 'ABC'},
        parity_comparisons=32,parity_differences=differences,incomplete=incomplete,safety=safety,
        native_state_correct=sum(r['native']['native_state_correct'] for r in rows),
        unexpected_mutation_attempts=sum(r['native']['unexpected_mutations'] for r in rows),
        source_bundles=sorted(source_bundles),fresh_subject_pids=len(set(pids)),
        preservation=dict(pre_existing_files=len(before),unchanged=len(before)-len(changed),authorized_v4_changes=changed,forbidden_changes=forbidden_changes),
        size=dict(shared_vocabulary=count([ROOT/'v4/vocabulary.json']),shared_runtime=count(core),shared_baseline_glue=count(baseline_shared),
                  provider_adapters=count(adapters.values()),evaluation_infrastructure=count(evaluation),
                  tests=count([ROOT/'tests/v4_pilot/test_comparison.py']),
                  provider_descriptions={p:count([ROOT/f'v4/descriptions/{p}.{s}' for s in ('json','ttl')]) for p in 'ab'}),
        automation=costs,run_timing=json.loads((run/'run-timing.json').read_text()),
        independent_provider_units=2,human_active_minutes=None,ai_supervision_minutes=None,tool_model_wait_minutes=None,
        observed_onboarding_effort=False,confirmatory=False,provider_c_accessed=False)
    save(run/'summary.json',summary)
    save(run/'evidence-index.json', {str(p.relative_to(run)):sha(p) for p in sorted(run.rglob('*')) if p.is_file() and p.name!='evidence-index.json'})
    print(json.dumps({k:summary[k] for k in ('verdict','executed','diagnostic_passed','classification_counts','parity_differences','safety','preservation')},indent=2))
    return 0 if good else 1


if __name__=='__main__': raise SystemExit(main())
