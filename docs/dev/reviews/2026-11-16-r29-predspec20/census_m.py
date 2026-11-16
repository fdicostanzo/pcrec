import json,re,sys
S=json.load(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/census/work/spans.json'))
mark=sys.argv[1]
def strip_rx(t):
    return re.sub(r'(?<![\w)\]])/(?:\\.|[^/])+/','<RX>',t)
for ln,k,t in S:
    s=strip_rx(t)
    if k=='B': s=s.split('#')[0]
    if re.search(mark,s): print(ln,k,t)
