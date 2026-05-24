import re
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE))
from core.runner.core.executor import MiniZincExecutor
from core.runner.core.solvers import SolverType

MODEL = BASE / 'core' / 'models' / 'clp_model.mzn'
DZN = BASE / 'experiments' / 'instances' / 'Battery-Decided' / 'cork-1-line_Battery-Decided20_0.dzn'

base_text = MODEL.read_text(encoding='utf-8')
variants = {
    'base': base_text,
    'xbi_input_min': re.sub(r'solve :: int_search\(\[xbi\[b,i\] \| b in B, i in 1\.\.[^\]]+\], input_order, indomain_min, complete\)\s*minimize \(sum\(st in ST\)\(xst\[st\]\) \* TIE_BREAK_WEIGHT \+ sum\(st in ST\)\(st \* xst\[st\]\)\);',
        'solve :: int_search([xbi[b,i] | b in B, i in 1..max_stops], input_order, indomain_min, complete)\n    minimize sum(st in ST)(xst[st]);',
        base_text, flags=re.S),
    'xst_input_min': re.sub(r'solve :: int_search\(\[xbi\[b,i\] \| b in B, i in 1\.\.[^\]]+\], input_order, indomain_min, complete\)\s*minimize \(sum\(st in ST\)\(xst\[st\]\) \* TIE_BREAK_WEIGHT \+ sum\(st in ST\)\(st \* xst\[st\]\)\);',
        'solve :: int_search([xst[st] | st in ST], input_order, indomain_min, complete)\n    minimize sum(st in ST)(xst[st]);',
        base_text, flags=re.S),
    'xst_input_max': re.sub(r'solve :: int_search\(\[xbi\[b,i\] \| b in B, i in 1\.\.[^\]]+\], input_order, indomain_min, complete\)\s*minimize \(sum\(st in ST\)\(xst\[st\]\) \* TIE_BREAK_WEIGHT \+ sum\(st in ST\)\(st \* xst\[st\]\)\);',
        'solve :: int_search([xst[st] | st in ST], input_order, indomain_max, complete)\n    minimize sum(st in ST)(xst[st]);',
        base_text, flags=re.S),
    'xbi_input_max': re.sub(r'solve :: int_search\(\[xbi\[b,i\] \| b in B, i in 1\.\.[^\]]+\], input_order, indomain_min, complete\)\s*minimize \(sum\(st in ST\)\(xst\[st\]\) \* TIE_BREAK_WEIGHT \+ sum\(st in ST\)\(st \* xst\[st\]\)\);',
        'solve :: int_search([xbi[b,i] | b in B, i in 1..max_stops], input_order, indomain_max, complete)\n    minimize sum(st in ST)(xst[st]);',
        base_text, flags=re.S),
}

for name, text in variants.items():
    with tempfile.NamedTemporaryFile('w', suffix='.mzn', delete=False, encoding='utf-8') as f:
        temp_model = Path(f.name)
        f.write(text)
    try:
        executor = MiniZincExecutor(str(temp_model), timeout_seconds=120)
        success, result, elapsed = executor.execute(str(DZN), SolverType.CPLEX)
        idx = None
        if success and result and 'charging_locations' in result:
            idx = next((i+1 for i, v in enumerate(result['charging_locations']) if v == 1), None)
        print(name, 'success=', success, 'selected=', idx, 'charged=', result.get('charged_stations') if result else None, 'dev=', result.get('time_deviation') if result else None, 'elapsed=', elapsed)
    finally:
        try:
            temp_model.unlink()
        except Exception:
            pass
