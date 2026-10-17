"""Declared two/three-step event chains. No planning, retries or oracle answers."""
from dataclasses import dataclass
import json
from pathlib import Path
from .model import Goal, Truth, instant, now
from .oracle import current


@dataclass(frozen=True)
class SequencePlan:
    goals: tuple[Goal, ...]

    def __post_init__(self):
        if type(self.goals) is not tuple or len(self.goals) not in {2, 3} or any(not isinstance(g, Goal) for g in self.goals):
            raise ValueError('Exactly two or three declared event goals required')
        if any(not g.forbid_other_changes for g in self.goals):
            raise ValueError('Sequence preservation is mandatory')
        if any(instant(b.start_time) < instant(a.end_time) for a, b in zip(self.goals, self.goals[1:])):
            raise ValueError('Follow-up intervals must respect predecessor order')


def dependency(goal, previous_goal, predecessor, evidence, since):
    if not current(evidence, goal.max_evidence_age_seconds, since) or not isinstance(evidence.get('events'), dict):
        return Truth.UNKNOWN, 'Missing/stale complete dependency observation'
    item = evidence['events'].get(predecessor)
    if not isinstance(item, dict):
        return Truth.FALSE, 'Required predecessor absent'
    try:
        equal = (item['id'] == predecessor and item['title'] == previous_goal.title and
                 instant(item['start_time']) == instant(previous_goal.start_time) and
                 instant(item['end_time']) == instant(previous_goal.end_time) and
                 instant(goal.start_time) >= instant(item['end_time']))
    except (KeyError, TypeError, ValueError):
        return Truth.UNKNOWN, 'Insufficient predecessor properties'
    return (Truth.TRUE, 'Current predecessor establishes temporal dependency') if equal else (Truth.FALSE, 'Predecessor does not meet dependency')


class SequenceExecutor:
    def run(self, plan, binding, output):
        output = Path(output)
        target = output / 'sequence.json'
        if target.exists():
            raise FileExistsError('Sequence evidence already exists')
        result = {'profile_version': 1, 'started_at': now(), 'status': 'RUNNING',
                  'formal_goals': [g.to_dict() for g in plan.goals], 'steps': [],
                  'runtime_verified': False, 'automatic_retries': 0, 'repair_iterations': 0}
        def save():
            temporary = target.with_suffix('.tmp')
            with temporary.open('w') as stream:
                json.dump(result, stream, indent=2, allow_nan=False)
                stream.flush()
                import os
                os.fsync(stream.fileno())
            temporary.replace(target)
        save()
        predecessor = None
        for index, goal in enumerate(plan.goals):
            step = {'index': index, 'started_at': now(), 'predecessor_id': predecessor,
                    'dependency_verdict': None, 'dependency_evidence': None, 'action': None}
            result['steps'].append(step)
            save()
            if index:
                if not binding.compatible:
                    step.update(dependency_verdict=Truth.FALSE, reason='Non-equivalent follow-up effect')
                    result['status'] = 'REJECTED'
                    break
                evidence = binding.read_state()
                truth, reason = dependency(goal, plan.goals[index - 1], predecessor, evidence,
                                           step['started_at'])
                step.update(dependency_verdict=truth, dependency_evidence=evidence, reason=reason)
                save()
                if truth != Truth.TRUE:
                    result['status'] = 'BLOCKED' if truth == Truth.UNKNOWN else 'REJECTED'
                    break
            directory = output / f'step-{index + 1}'
            directory.mkdir(exist_ok=False)
            action = binding.execute(index, predecessor, goal, directory)
            step['action'] = action
            step['completed_at'] = now()
            if not (action.get('oracle_verdict') or {}).get('achieved'):
                result['status'] = ('BLOCKED' if action.get('execution_decision') == 'BLOCK' else
                                    'REJECTED' if action.get('execution_decision') == 'REJECT' else 'INCOMPLETE')
                break
            predecessor = (action.get('api_response') or {}).get('body', {}).get('id')
            # Local response IDs are provider-specific; infer the independently queried
            # canonical event ID already retained by its validated observation adapter.
            if predecessor is None:
                observed = (action.get('observed_effects') or {}).get('event') or {}
                predecessor = (observed.get('event') or {}).get('id')
            save()
        else:
            result['status'] = 'COMPLETE'
            result['runtime_verified'] = True
        result['completed_at'] = now()
        save()
        return result


def main():
    import argparse
    from .sequence_bindings import LocalSequenceBinding, SharedSequenceBinding
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text())
    plan = SequencePlan(tuple(Goal(**g) for g in data['formal_goals']))
    output = Path(data['output'])
    if data['condition'] == 'A':
        binding = LocalSequenceBinding(data['root'], data['profile'], data['origin'])
    elif data['condition'] in {'B', 'C'}:
        binding = SharedSequenceBinding(data['root'], data['profile'], data['origin'], output)
    else:
        raise ValueError('Unknown condition')
    SequenceExecutor().run(plan, binding, output)


if __name__ == '__main__':
    main()
