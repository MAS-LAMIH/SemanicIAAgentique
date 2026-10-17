"""Append-only engineering activity records; unknown effort remains unknown."""
from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class WorkEntry:
    activity: str
    contributor: str
    files: tuple[str, ...] = ()
    started_at: str | None = None
    ended_at: str | None = None
    elapsed_minutes: float | None = None
    semantic_mappings_added: int | None = None
    validation_rules_added: int | None = None
    test_cases_added: int | None = None
    failed_attempts: int | None = None
    debugging_minutes: float | None = None
    ai_assistance_used: bool = False
    measurement_source: str = 'human_entry_required'
    notes: str = ''


def log_work(path: str | Path, entry: WorkEntry):
    if not entry.activity or not entry.contributor:
        raise ValueError('Activity and contributor are required')
    for name in ('elapsed_minutes', 'debugging_minutes', 'failed_attempts',
                 'semantic_mappings_added', 'validation_rules_added', 'test_cases_added'):
        value = getattr(entry, name)
        if value is not None and value < 0:
            raise ValueError('Measurements cannot be negative')
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(asdict(entry), sort_keys=True, allow_nan=False) + '\n')
