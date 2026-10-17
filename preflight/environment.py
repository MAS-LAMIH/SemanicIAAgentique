"""Read-only environment and installed-byte provenance capture."""
import importlib.metadata as m
import json
import platform
import subprocess
from pathlib import Path
from .driver import ROOT,save
from .guard import sha,verify_runtime
AREA=ROOT/'docs/artifacts/milestone4_5'
def main():
    rows={}
    script="import json,platform,importlib.metadata as m,semantic_action; print(json.dumps({'python':platform.python_version(),'platform':platform.platform(),'module':semantic_action.__file__,'packages':{x.metadata['Name']:x.version for x in m.distributions()}}))"
    for kind in ('source','wheel','restored'):
        command=[f'/tmp/m44-{kind}-env/bin/python','-c',script]
        result=subprocess.run(command,capture_output=True,text=True,check=True)
        observed=json.loads(result.stdout)
        package=Path(observed['module']).parent
        manifest=json.loads((ROOT/'docs/SCIENTIFIC_FREEZE_MANIFEST_V3.json').read_text())
        files={p:h for group in manifest['file_groups'].values() for p,h in group.items() if p.startswith('src/semantic_action/')}
        mismatches=[p for p,h in files.items() if sha(package/p.removeprefix('src/semantic_action/'))!=h]
        if mismatches: raise RuntimeError('STOP runtime mismatch '+str(mismatches))
        rows[kind]=dict(command=command,exit_code=result.returncode,observed=observed,runtime_files_checked=len(files),runtime_mismatches=mismatches)
    rows['driver']=verify_runtime(ROOT)
    rows['retained_artifacts']={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'docs/artifacts/milestone4_3').iterdir() if p.suffix in ('.whl','.gz')}
    rows['tag']=subprocess.check_output(['git','rev-parse','candidate/milestone-4.3-pre-freeze^{}'],cwd=ROOT,text=True).strip()
    save(AREA/'environments.json',rows)
if __name__=='__main__':main()
