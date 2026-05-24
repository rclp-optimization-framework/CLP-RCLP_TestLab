"""
Run specified model with CPLEX via the project's MiniZincExecutor and save JSON results.
Requires a CPLEX-capable MiniZinc installation and CPLEX available on PATH.
Usage:
    python scripts/runner/run_with_cplex.py --model core/models/clp_model.mzn --dzn experiments/instances/Battery-Decided/cork-1-line_Battery-Decided20_0.dzn --out results/cplex_int_20_0.json
"""
import argparse
import json
import tempfile
import sys
import re
from pathlib import Path
BASE = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = BASE / 'scripts'
sys.path.insert(0, str(BASE))
from core.runner.core.executor import MiniZincExecutor
from core.runner.core.solvers import SolverType

parser = argparse.ArgumentParser()
parser.add_argument('--model', required=True)
parser.add_argument('--dzn', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--time', type=int, default=600)
parser.add_argument('--solver_time_limit_ms', type=int, default=None)
parser.add_argument('--warm-start-json', default=None)
args = parser.parse_args()

executor = MiniZincExecutor(args.model, timeout_seconds=args.time)
solver_options = {}
if args.solver_time_limit_ms:
    solver_options['solver_time_limit'] = args.solver_time_limit_ms

data_file = Path(args.dzn)
temp_model_file = None
temp_warmstart_data_file = None

if args.warm_start_json:
    warm_dir = SCRIPTS_DIR / 'warm_start'
    warm_dir.mkdir(parents=True, exist_ok=True)
    generated_dir = warm_dir / 'generated'
    generated_dir.mkdir(parents=True, exist_ok=True)
    temp_model_file = generated_dir / f"{Path(args.model).stem}_{data_file.stem}_warmstart.mzn"
    temp_warmstart_data_file = generated_dir / f"{data_file.stem}_warmstart.dzn"

    warm_path = Path(args.warm_start_json)
    warm_data = json.loads(warm_path.read_text(encoding='utf-8'))
    charging_locations = warm_data['result']['charging_locations']
    xst_init = ', '.join(str(int(v)) for v in charging_locations)
    model_text = Path(args.model).read_text(encoding='utf-8')
    model_text = model_text.replace(
        'solve :: int_search([xbi[b,i] | b in B, i in 1..max_stops], input_order, indomain_min, complete)',
        f'array[ST] of int: xst_init = [{xst_init}];\n\nsolve :: warm_start(xst, xst_init) :: int_search([xbi[b,i] | b in B, i in 1..max_stops], input_order, indomain_min, complete)',
    )
    with open(temp_model_file, 'w', encoding='utf-8') as temp:
        temp.write(model_text)
    with open(temp_warmstart_data_file, 'w', encoding='utf-8') as temp:
        temp.write(f"xst_init = [{xst_init}];\n")
    print(f"Wrote warm-start model: {temp_model_file}")
    print(f"Wrote warm-start data: {temp_warmstart_data_file}")
try:
    if temp_model_file is not None:
        warm_executor = MiniZincExecutor(str(temp_model_file), timeout_seconds=args.time)
        success, result, elapsed = warm_executor.execute(str(data_file), SolverType.CPLEX, solver_options)
    else:
        success, result, elapsed = executor.execute(str(data_file), SolverType.CPLEX, solver_options)
finally:
    # Only remove temp file on success; keep it for debugging on failure
    try:
        if temp_model_file and temp_model_file.exists() and 'success' in locals() and success:
            temp_model_file.unlink()
        if temp_warmstart_data_file and temp_warmstart_data_file.exists() and 'success' in locals() and success:
            temp_warmstart_data_file.unlink()
    except Exception:
        pass

output = {
    'success': success,
    'result': result,
    'elapsed': elapsed
}

out_path = Path(args.out)
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print('Wrote', out_path)
