import sys, collections
sys.path.insert(0, sys.argv[1]); import candidates as C
R=[(lo,hi) for lo in range(3) for hi in range(lo+1,5)]
d=collections.Counter(); worst={}
for s in C.subjects():
    for P in range(len(s)+1):
        for lo,hi in R:
            a,wa=C.counter(s,P,lo,hi); b,wb=C.cursor(s,P,lo,hi)
            x=wb-wa; d[x]+=1
            if x>0 and x not in worst: worst[x]=(s.hex(),P,lo,hi,wa,wb,len(b))
print("cursor work minus counter work: distribution", sorted(d.items()))
for k,v in sorted(worst.items()): print("first +%d: subject=%s POS=%d lo=%d hi=%d counter=%d cursor=%d candidates=%d"%((k,)+v))
