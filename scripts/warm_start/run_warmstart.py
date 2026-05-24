#!/usr/bin/env python3
"""Run a MiniZinc model in the warm_start research folder.

Usage examples:
  python run_warmstart.py --model clp_model_warmstart.mzn --instance instances/cork-1-line_Battery-Decided20_0.dzn --out tmp/out.txt

This wrapper executes `minizinc --solver cplex` and writes solver output to `--out` if provided.
"""
import argparse
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).parent

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model', default=str(ROOT / 'clp_model_warmstart.mzn'))
    p.add_argument('--instance', required=True)
    p.add_argument('--out', help='File to write solver output to')
    p.add_argument('--solver', default='cplex')
    p.add_argument('--minizinc', default='minizinc')
    p.add_argument('--time', type=int, help='Time limit in seconds (optional)')
    args = p.parse_args()

    model_path = Path(args.model)
    instance_path = Path(args.instance)
    if not model_path.exists():
        model_path = ROOT / args.model
    if not instance_path.exists():
        instance_path = ROOT / args.instance
    if not model_path.exists() or not instance_path.exists():
        print('Model or instance not found: ', model_path, instance_path)
        raise SystemExit(2)

    cmd = [args.minizinc, '--solver', args.solver, str(model_path), str(instance_path)]
    if args.time:
        # minizinc uses milliseconds for --time-limit
        cmd += ['--time-limit', str(int(args.time * 1000))]

    print('Running:', ' '.join(cmd))
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if args.out:
        outp = Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(proc.stdout)
        print('Wrote', outp)
    else:
        print(proc.stdout)

    if proc.returncode != 0:
        print('MINIZINC STDERR:')
        print(proc.stderr)
        raise SystemExit(proc.returncode)

if __name__ == '__main__':
    main()
