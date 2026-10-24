import sys, unicodedata as U, collections, re
D='/home/pcrec/projects/pcrec/third_party/ucd-16.0.0/'
dec={}; names={}
for l in open(D+'UnicodeData.txt',encoding='utf-8'):
    f=l.split(';'); cp=int(f[0],16); names[cp]=f[1]
    if f[5].startswith('<'):
        t,_,r=f[5].partition('> '); dec[cp]=(t[1:],[int(x,16) for x in r.split()])
print("compat-mapped code points (vendored):",len(dec))
print("tag counts:",dict(collections.Counter(t for t,_ in dec.values()).most_common()))
# cross-check vs unicodedata
bad=sum(1 for c in dec if not U.decomposition(chr(c)).startswith('<'))
print("vendored vs unicodedata tag mismatches:",bad, " unicodedata compat count:",sum(1 for c in range(0x110000) if U.decomposition(chr(c)).startswith('<')))
N=lambda c:U.normalize('NFKC',chr(c))
# Q1
tgt=collections.defaultdict(list)
for c in dec:
    n=N(c)
    if n!=chr(c): tgt[n].append(c)
print("\nQ1")
tot=collections.Counter(); per={}
for ch in [chr(x) for x in list(range(65,91))+list(range(97,123))+list(range(48,58))]:
    cnt=collections.Counter(dec[c][0] for c in tgt[ch]); per[ch]=cnt; tot+=cnt
    print(ch,sum(cnt.values()),dict(cnt))
print("TOTAL",sum(tot.values()),dict(tot))
for grp,rng in [('upper',range(65,91)),('lower',range(97,123)),('digit',range(48,58))]:
    print(grp,sum(sum(per[chr(x)].values()) for x in rng))
# Q2
print("\nQ2")
multi=[(c,N(c)) for c in dec if len(N(c))>1 and all(ord(x)<128 for x in N(c))]
cat=collections.defaultdict(list)
for c,n in multi:
    k=dec[c][0]; cat[k].append((c,n))
print("total ASCII-multi:",len(multi))
for k,v in cat.items(): print(k,len(v),[(chr(c),n) for c,n in v[:6]])
single_nonascii=[(c,N(c)) for c in dec if len(N(c))==1 and ord(N(c))>=128 and N(c)!=chr(c)]
# Q3
print("\nQ3")
print("single->single ASCII:",sum(len(v) for k,v in tgt.items() if len(k)==1 and ord(k)<128))
print("single non-ASCII targets: sources",len(single_nonascii),"distinct targets",len({n for _,n in single_nonascii}))
scr=collections.Counter()
for _,n in single_nonascii: scr[U.name(n).split()[0]]+=1
print("target by first name word:",scr.most_common(12))
other=[(c,N(c)) for c in dec if len(N(c))>1 and not all(ord(x)<128 for x in N(c))]
print("multi-char non-ASCII-involving results:",len(other),[(chr(c),N(c)) for c,_ in other[:5]])
print("canonical-identical (NFKC==char) among compat-mapped:",sum(1 for c in dec if N(c)==chr(c)))
# Q4
print("\nQ4")
def cf(s): return s.casefold()
def nfkccf(s):
    return U.normalize('NFKC',cf(U.normalize('NFKC',cf(U.normalize('NFD',s)))))
cfmap=collections.defaultdict(list)
for c in range(0x110000):
    if 0xD800<=c<0xE000: continue
    s=nfkccf(chr(c))
    if len(s)==1 and s!=chr(c) or len(s)==1: cfmap[s].append(c)
for grp in ['abcdefghijklmnopqrstuvwxyz','0123456789']:
    print({ch:len(cfmap[ch]) for ch in grp})
print("letter total",sum(len(cfmap[ch]) for ch in 'abcdefghijklmnopqrstuvwxyz'))
for ch in 'fks': print(ch,[f"U+{c:04X}" for c in cfmap[ch] if c>127][:40])
print("(?i)f extra beyond plain-ASCII-pair: non-ASCII count",sum(1 for c in cfmap['f'] if c>127), "(Kelvin sign U+212A in k:",0x212A in cfmap['k'],"; U+017F in s:",0x17F in cfmap['s'],")")
# Q5
print("\nQ5")
chain=[c for c in dec if any(t in dec for t in dec[c][1])]
print("sources whose one-step mapping contains a compat-mapped char (chains):",len(chain),[(f"U+{c:04X}",[f"U+{t:04X}" for t in dec[c][1]]) for c in chain[:5]])
unstab=[(c,N(c)) for c in dec if N(c)!=chr(c) and U.normalize('NFKC',N(c))!=N(c)]
print("NFKC not idempotent:",len(unstab))
nonstab_targets=[t for t in tgt if U.normalize('NFKC',t)!=t]
print("NFKC targets not NFKC-stable:",len(nonstab_targets))
# does mapping contain any compat tags after one step (single step target not final)
one_step_nonfinal=[c for c in dec if len(dec[c][1])>=1 and any(U.normalize('NFKC',chr(t))!=chr(t) for t in dec[c][1])]
print("one-step targets that are NFKC-unstable:",len(one_step_nonfinal))
# Q6
print("\nQ6")
def split(lo,hi):
    # utf8 range sequences, standard algorithm
    out=[]
    def rec(lo,hi):
        for n,m in [(0x7F,1),(0x7FF,2),(0xFFFF,3)]:
            pass
        for b in (0x7F,0x7FF,0xFFFF):
            if lo<=b<hi: rec(lo,b); rec(b+1,hi); return
        if hi<0x80: out.append(((lo,hi),)); return
        for i in range(1,4):
            m=(1<<(6*i))-1
            if (lo&~m)!=(hi&~m):
                if (lo&m)!=0: rec(lo,lo|m); rec((lo|m)+1,hi); return
                if (hi&m)!=m: rec(lo,(hi&~m)-1); rec(hi&~m,hi); return
        a=chr(lo).encode(); b=chr(hi).encode()
        out.append(tuple(zip(a,b)))
    rec(lo,hi); return out
def cost(cps):
    cps=sorted(cps); rs=[]
    for c in cps:
        if rs and rs[-1][1]==c-1: rs[-1][1]=c
        else: rs.append([c,c])
    seqs=[s for a,b in rs for s in split(a,b)]
    leads={s[0] for s in seqs}
    leadbytes=set()
    for a,b in rs:
        for c in (a,b): pass
    # distinct lead bytes by actual encoding
    lb={chr(c).encode()[0] for c in cps}
    return len(cps),len(rs),len(seqs),len(lb)
print("columns: codepoints, ranges, utf8 byte-range sequences, distinct lead bytes")
for ch in 'afkexAZ0159':
    sset=sorted(set(tgt[ch])|{ord(ch)})
    print(ch,"compat-only set+self:",cost(sset))
for ch in 'fks':
    print(ch,"(?i) NFKC_CF set:",cost(cfmap[ch]))
allset=sorted({c for ch in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in tgt[ch]})
print("all letters union, compat only:",cost(allset))
