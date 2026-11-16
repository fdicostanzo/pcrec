import json,re
S=json.load(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/census/work/spans.json'))
for ln,k,t in S:
    if ln>=5007: continue
    for m in re.finditer(r'(?<![:<>=!])(<=|>=|==|<|>)\s*([a-z_][a-z_0-9.]*)\b(?!\()',t):
        print(ln,m.group(0),'|',t[:110])
