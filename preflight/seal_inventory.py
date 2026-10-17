"""Hash only the new evaluator revision; never create a new V3 candidate."""
from datetime import datetime,timezone
from .driver import ROOT,save
from .guard import sha,CANDIDATE,MANIFEST_SHA
AREA=ROOT/'docs/artifacts/milestone4_5'
if __name__=='__main__':
    paths=[p for p in (ROOT/'preflight').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [ROOT/'docs/MILESTONE_4_5_PREFLIGHT.md',ROOT/'docs/COMBINED_DRIVER_PREFLIGHT_REPORT.md']
    paths += [p for p in AREA.rglob('*') if p.is_file() and p.name!='preflight-manifest.json']
    save(AREA/'preflight-manifest.json',dict(schema_version='1.0',kind='evaluator-only evidence index',
        recorded_at=datetime.now(timezone.utc).isoformat(),candidate_commit=CANDIDATE,manifest_sha256=MANIFEST_SHA,
        new_implementation_candidate=False,scientific_freeze_approved=False,unseal_authorized=False,
        human_active_minutes=None,ai_supervision_minutes=None,tool_model_wait_minutes=None,
        self_hash_excluded=True,files={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}))
