import json,re,sys
S=json.load(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/census/work/spans.json'))
mark=sys.argv[1]
def strip_rx(t):
    # remove /.../ rx literals (rough): slash-delimited not preceded by word char
    return re.sub(r'(?<![\w)\]])/(?:\\.|[^/])+/','<RX>',t)
for ln,k,t in S:
    s=strip_rx(t)
    if mark in s: print(ln,k,t)
