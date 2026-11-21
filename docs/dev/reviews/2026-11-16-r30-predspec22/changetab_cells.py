import re,sys
f=sys.argv[1]
L=open(f).read().split('\n')
# group consecutive table lines
i=0
while i<len(L):
    if L[i].startswith('|'):
        j=i
        while j<len(L) and L[j].startswith('|'): j+=1
        def n(s): return len(re.split(r'(?<!\\)\|',s.strip()))-2
        hdr=n(L[i])
        for k in range(i,j):
            if n(L[k])!=hdr: print(k+1,hdr,n(L[k]),L[k][:80])
        i=j
    else: i+=1
