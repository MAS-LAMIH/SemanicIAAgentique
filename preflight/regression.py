"""Re-run exact frozen suites using retained isolated installations."""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def one(kind):
    interpreter=f'/tmp/m44-{kind}-env/bin/python'
    source='/tmp/m45-restored-ofr99itm' if kind=='restored' else '/tmp/m45-v3-g59s7wl8'
    return subprocess.run([sys.executable,'-m','preflight.record_command','--id','regression-'+kind,'--cwd',source,'--',interpreter,'-m','unittest','discover','-s','tests/semantic_action','-v'],cwd=ROOT).returncode
if __name__=='__main__':
    with ThreadPoolExecutor(3) as pool: results=list(pool.map(one,['source','wheel','restored']))
    raise SystemExit(any(results))
