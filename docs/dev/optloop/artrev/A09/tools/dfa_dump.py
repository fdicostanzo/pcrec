import re,sys
src=open(sys.argv[1]).read()
def arr(name):
    m=re.search(r'%s\[\d+\] = \{(.*?)\};'%name,src,re.S)
    return [int(x) for x in re.findall(r'\d+',m.group(1))]
bc=arr('rx_forward_byte_class'); ns=arr('rx_forward_next_state'); acc=arr('rx_forward_is_accepting'); abc=arr('rx_forward_is_accepting_by_class')
NC=29
states=sorted(set(range(0,1276,NC)))
cls={}
for b in range(256): cls.setdefault(bc[b],[]).append(b)
def nm(c): 
    bs=cls[c]; return ''.join(chr(b) if 32<b<127 else '\\x%02x'%b for b in bs[:4])+('..' if len(bs)>4 else '')
for s in states:
    row=ns[s:s+NC]
    from collections import Counter
    com=Counter(row).most_common(1)[0][0]
    exc={nm(c):row[c] for c in range(NC) if row[c]!=com}
    a=[nm(c) for c in range(NC) if abc[s+c]]
    print(s//NC, s, 'default->',com, exc, 'acc' if acc[s] else '', 'accby',a)
