"""Small typed interchange model; RDF is only one possible contract frontend."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def instant(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError('Timestamp must be a string')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamp requires an explicit timezone')
    return result


class Truth(str, Enum):
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    UNKNOWN = 'UNKNOWN'


@dataclass(frozen=True)
class Goal:
    start_time: str
    end_time: str
    title: str
    forbid_other_changes: bool = True
    max_evidence_age_seconds: float = 30.0

    def __post_init__(self):
        if instant(self.end_time) <= instant(self.start_time):
            raise ValueError('Goal interval must be positive')
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError('Goal title must be nonempty')
        if type(self.forbid_other_changes) is not bool:
            raise ValueError('Goal side-effect constraint must be boolean')
        if not 0 < self.max_evidence_age_seconds <= 300:
            raise ValueError('Invalid goal evidence age')

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class Contract:
    artifact_id: str
    operation_id: str
    capability_id: str
    inputs: tuple[str, ...]
    preconditions: tuple[str, ...]
    declared_effects: tuple[str, ...]
    method: str
    path: str
    observation_path: str
    max_evidence_age_seconds: float


@dataclass(frozen=True)
class Condition:
    name: str
    verdict: Truth
    reason: str
    evidence: dict


@dataclass(frozen=True)
class Validation:
    valid: bool
    errors: tuple[str, ...]


@dataclass(frozen=True)
class ApiResult:
    status: int | None
    body: dict
    error: str | None = None

    @property
    def success(self):
        return self.status is not None and 200 <= self.status < 300


@dataclass(frozen=True)
class Observation:
    event: dict | None
    state: dict | None
    error: str | None = None


@dataclass(frozen=True)
class OracleVerdict:
    achieved: bool
    reasons: tuple[str, ...]


class SubstitutionChecker(Protocol):
    """Future interface only; no planner or equivalence by operation name.

    Must consider applicability, required goal effects, input/output types,
    mandatory constraints, and sufficient observation evidence. UNKNOWN blocks.
    """
    def check(self, original: Contract, candidate: Contract, goal: Goal,
              evidence: dict) -> Truth: ...
