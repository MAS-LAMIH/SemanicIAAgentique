"""Plain data only. HTTP success is not domain correctness."""
from dataclasses import dataclass

NAMESPACE = 'https://example.org/capability/v4/1#'
EVENT_CREATION = NAMESPACE + 'EventCreation'
INPUT_ROLES = ('start_time', 'end_time', 'title')


@dataclass(frozen=True)
class OperationDescription:
    description_version: int
    provider_id: str
    operation_id: str
    capability_id: str
    method: str
    path: str
    # Sorted (canonical role, native field, conversion) tuples.
    input_mapping: tuple[tuple[str, str, str], ...]
    output_mapping: tuple[tuple[str, str, str], ...]
    title_max_length: int
    max_duration_seconds: int
    time_grid_seconds: int


@dataclass(frozen=True)
class InvocationResult:
    operation_id: str | None = None
    http_status: int | None = None
    http_ok: bool = False
    output: dict | None = None
    error_kind: str | None = None
    diagnostics: tuple[str, ...] = ()
    remote_outcome_unknown: bool = False
