import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE))

from core.runner.core.executor import MiniZincExecutor
from core.runner.core.solvers import SolverType
MODEL_INT = BASE / 'core' / 'models' / 'clp_model.mzn'
MODEL_FLOAT = BASE / 'core' / 'models' / 'clp_model_float.mzn'
DZN = BASE / 'experiments' / 'instances' / 'Battery-Decided' / 'cork-1-line_Battery-Decided20_0.dzn'

for model in [MODEL_INT, MODEL_FLOAT]:
    print('---')
    print('Model:', model)
    exec = MiniZincExecutor(str(model), timeout_seconds=60)
    # Use local available solver for diagnostics
    success, result, elapsed = exec.execute(str(DZN), SolverType.CHUFFED)
    print('success:', success, 'elapsed:', elapsed)
    if not success:
        print('No solution or timeout')
        continue
    # xst variable holds stations installed
    xst = result.get('xst')
    if xst is None:
        print('xst not present in result keys:', list(result.keys()))
    else:
        try:
            idx = xst.index(1) if 1 in xst else None
        except Exception:
            # some solvers return floats 1.0
            try:
                idx = xst.index(1.0) if 1.0 in xst else None
            except Exception:
                idx = None
        print('first_installed_index (1-based):', idx)
        print('xst sample:', xst[:40])
    print('\n')
