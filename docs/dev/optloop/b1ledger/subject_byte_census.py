import sys, hashlib
sys.path.insert(0,"/Users/fdicostanzo/pcrec-bench/bench/capability")
sys.path.insert(0,"/Users/fdicostanzo/pcrec-bench")
import captext as ct
SIZES=(("t-64k",64*1024,0xC0FFEE1),("t-256k",256*1024,0xC0FFEE2),("t-1m",1024*1024,0xC0FFEE3))
want={"t-64k":"d2e4f134473cc40a9a4e7df7a30e0efa11f566d96ee990c62cd663a2439c8524",
"t-256k":"3cf7b248873da164518b74e039cc2380f39e233b2899716c82c8eb4b7b49b5a7",
"t-1m":"ccbdf7eb97f15776a68b8bbb9d6387870cd01d4796207fb20032958caf9754ee"}
bytes_of_interest={47:"/ (nested-comment-rec)",92:"\\\\ (winpath-near-miss)",64:"@ (email-nested-plus)",114:"r (router-prefix-order)",126:"~ (floor-byte)",45:"- (uuid-near-miss)",46:". (ipv4-near-miss)"}
tot=0
for sid,n,seed in SIZES:
    b=ct.text(n,seed); h=hashlib.sha256(b).hexdigest(); tot+=len(b)
    print("%-8s len=%7d sha_ok=%s" % (sid,len(b),h==want[sid]))
    for bv,lab in sorted(bytes_of_interest.items()):
        i=b.find(bytes([bv])); c=b.count(bytes([bv]))
        print("   byte %3d %-26s first_at=%-8s count=%-7d" % (bv,lab,i,c))
print("total bytes across 3 subjects =",tot)
