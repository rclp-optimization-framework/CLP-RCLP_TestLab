from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from core.runner.core.executor import MiniZincExecutor
from core.runner.core.solvers import SolverType, SolverManager
import logging
logging.basicConfig(level=logging.DEBUG)

model = ROOT / 'core' / 'models' / 'clp_model_float.mzn'
inst = ROOT / 'experiments' / 'instances' / 'battery-new' / 'cork-1-line_battery-new20_0.dzn'
print('Model exists:', model.exists())
print('Instance exists:', inst.exists())
exe = MiniZincExecutor(str(model), timeout_seconds=300)
solver = SolverType.CPLEX
success, result, etime = exe.execute(str(inst), solver)
print('SUCCESS:', success)
print('ETIME:', etime)
print('RESULT TYPE:', type(result))
if result is None:
    print('Result is None')
else:
    for k in ['charged_stations','charging_locations','time_deviation','execution_time','solver']:
        print(k, '->', result.get(k))

# For debugging, run minizinc directly too
import subprocess
cmd = ['minizinc','--solver', SolverManager.get_minizinc_solver_name(solver), str(model), str(inst)]
print('\nRunning minizinc directly:')
print('CMD:', ' '.join(cmd))
proc = subprocess.run(cmd, capture_output=True, text=True)
print('RET:', proc.returncode)
print('STDOUT:\n', proc.stdout[:1000])
print('STDERR:\n', proc.stderr[:1000])
