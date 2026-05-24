from pathlib import Path
f1=Path(r'experiments/instances/Battery-Last/cork-1-line_Battery-Last20_0.dzn')
f2=Path(r'experiments/instances/battery-java-aligned/cork-1-line_battery-java20_0.dzn')
if not f1.exists() or not f2.exists():
    print('MISSING FILES')
    raise SystemExit(1)
s1=f1.read_text(encoding='utf-8').splitlines()
s2=f2.read_text(encoding='utf-8').splitlines()
maxl=max(len(s1),len(s2))
diffs=[]
for i in range(maxl):
    a=s1[i] if i<len(s1) else ''
    b=s2[i] if i<len(s2) else ''
    if a!=b:
        diffs.append((i+1,a,b))
        if len(diffs)>=200:
            break
print('Total different lines:', sum(1 for i in range(maxl) if (s1[i] if i<len(s1) else '') != (s2[i] if i<len(s2) else '')))
for ln,a,b in diffs:
    print('Line',ln)
    print('A:',a)
    print('B:',b)
    print('---')
