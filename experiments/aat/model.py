"""Immutable records for the finite room-step/1 metamodel."""
from dataclasses import dataclass
import math
from semantic_action.model import Truth

NS='urn:eswc:aat:prototype:1#'
ROOM='urn:example:room:thing'

@dataclass(frozen=True)
class Thing:
    id: str

@dataclass(frozen=True)
class Operation:
    id: str
    artifact: str
    method: str
    path: str
    request_schema: str
    response_schema: str
    media_type: str

@dataclass(frozen=True)
class Artifact:
    id: str
    thing: str
    operations: tuple[str,...]
    observation_path: str

@dataclass(frozen=True)
class Usage:
    id: str
    artifact: str
    operation: str
    pre_context: str
    post_context: str
    ready_property: str
    minimum: int
    maximum: int
    delta: int
    frame: tuple[str,...]
    review_ref: str

@dataclass(frozen=True)
class ContextSnapshot:
    id: str
    thing: str
    temperature: int | None
    heater_ready: bool | None
    cooler_ready: bool | None
    revision: int | None
    mutations: int | None
    sentinel_json: str
    observed_at: str | None
    raw_json: str

@dataclass(frozen=True)
class StateGoal:
    thing: str
    temperature: int
    max_age: float = 10.0
    def __post_init__(self):
        if self.thing!=ROOM or type(self.temperature) is not int or not 18<=self.temperature<=26:
            raise ValueError('Unsupported room goal')
        if type(self.max_age) not in (int,float) or not math.isfinite(self.max_age) or not 0<self.max_age<=30:raise ValueError('Unsupported evidence age')

@dataclass(frozen=True)
class Candidate:
    handle: str
    operation: str
    applicable: Truth
    contributes: bool
    predicted_temperature: int | None
    reasons: tuple[str,...]

@dataclass(frozen=True)
class Proposal:
    tool: str
    handle: str | None = None
    snapshot_ref: str | None = None

@dataclass(frozen=True)
class Feedback:
    code: str
    reasons: tuple[str,...]
    context: ContextSnapshot | None

@dataclass(frozen=True)
class ControllerView:
    goal: StateGoal
    discovered: bool
    context: ContextSnapshot | None
    descriptions: tuple[Usage,...]
    candidates: tuple[Candidate,...]
    feedback: tuple[Feedback,...]

@dataclass(frozen=True)
class Permit:
    nonce: str
    handle: str
    revision: int
    graph_hash: str
