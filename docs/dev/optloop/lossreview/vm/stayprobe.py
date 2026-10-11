import re,sys,collections
# For a DFA artifact (forward machine), simulate on subjects and report the
# hottest states, their self-loop byte counts, and whether a stay table exists.
art=sys.argv[1]; subs=sys.argv[2:]
t=open(art).read()
def arr(name):
    m=re.search(r'%s\[\d+\] = \{(.*?)\};'%re.escape(name),t,re.S)
    return [int(x) for x in re.findall(r'-?\d+',m.group(1))] if m else None
pre=re.search(r'static const unsigned char (\w+?)_forward_byte_class\[256\]',t) or re.search(r'static const unsigned char (\w+?)_byte_class\[256\]',t)
base=pre.group(0).split()[4].split('[')[0]
fwd = base.replace('byte_class','')
bc=arr(fwd+'byte_class'); ns=arr(fwd+'next_state')
ncls=max(bc)+1
premul = len(ns)%ncls==0 and max(ns) >= ncls
stays=sorted(set(int(x) for x in re.findall(re.escape(fwd)+r'stay(\d+)\[',t)))
csz=collections.Counter(bc)
hist=collections.Counter(); total=0
for f in subs:
    s=open(f,'rb').read(); st=0
    for b in s:
        hist[st]+=1; total+=1
        i=st+bc[b] if premul else st*ncls+bc[b]
        nx=ns[i] if i<len(ns) else 0
        st=nx if nx>=0 else 0
print('machine',fwd,'classes',ncls,'premul',premul,'stay tables',stays)
for st,c in hist.most_common(5):
    row=[ns[st+k] if premul else ns[st*ncls+k] for k in range(ncls)]
    self_b=sum(csz[k] for k in range(ncls) if row[k]==st)
    print('  state %5d visits %8d (%.1f%%) self-loop bytes %3d  stay-table %s'%(st,c,100*c/total,self_b, 'yes' if st in stays or (premul and st//ncls in stays) else 'no'))
