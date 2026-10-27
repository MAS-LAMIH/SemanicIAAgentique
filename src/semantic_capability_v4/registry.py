"""Finite exact-ID lookup. No provider requests or inferred equivalence."""

class ResolutionError(ValueError):
    pass


class NotFound(ResolutionError):
    pass


class Ambiguous(ResolutionError):
    pass


def resolve(operations, capability_id, *, provider_id=None, operation_id=None):
    operations = tuple(operations)
    ids = [item.operation_id for item in operations]
    if len(set(ids)) != len(ids):
        raise Ambiguous('Duplicate operation identity')
    candidates = [item for item in operations if item.capability_id == capability_id
                  and (provider_id is None or item.provider_id == provider_id)
                  and (operation_id is None or item.operation_id == operation_id)]
    if not candidates:
        raise NotFound('No matching capability/selector')
    if len(candidates) != 1:
        raise Ambiguous('Multiple matching operations; supply an explicit selector')
    return candidates[0]
