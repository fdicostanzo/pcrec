import json,re,sys
S=json.load(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/census/work/spans.json'))
def strip_rx(t):
    t=re.sub(r'(?<![\w)\]])/(?:\\.|[^/])+/','<RX>',t)
    return t
for ln,k,t in S:
    s=strip_rx(t)
    s2=re.sub(r':=|==|<=|>=|!=|=>','  ',s)
    if k=='B': s2=s2.split('#')[0]
    if '=' in s2: print(ln,k,t)
