import re,sys
# function start offsets in .text from a gas -aln listing; also loop-head labels (aligned) inside hot functions
for path in sys.argv[1:]:
    fn=None; out=[]; sect='text'; pend=None; loops=[]
    for line in open(path):
        m=re.match(r'^\s*\d+\s+(?:([0-9a-f]{4}) ([0-9A-F]+)\s+)?\t?(.*)$',line.rstrip('\n'))
        if not m: continue
        off,code,src=m.group(1),m.group(2),m.group(3).strip()
        if src.startswith('.section') or src=='.text': sect='text' if src=='.text' else src
        if re.match(r'^[a-z_]+:$',src) and sect=='text': pend=('F',src[:-1]); continue
        if re.match(r'^\.L\d+:$',src) and sect=='text': pend2=src[:-1]; 
        if off and not src.startswith('.cfi') and sect=='text':
            if pend: out.append((pend[1],int(off,16))); fn=pend[1]; pend=None
    print(path, ' '.join('%s@%d(m64=%d)'%(f.replace('rx_',''),o,o%64) for f,o in out))
