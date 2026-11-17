import re,sys
S=open(sys.argv[1]).read().split('\n')
C=open(sys.argv[2]).read()
Cn=re.sub(r'\s+',' ',C)
txt=' '.join(S[449:1247])
txt=re.sub(r'\s+',' ',txt)
for m in re.finditer(r'"([^"]{12,}?)"',txt):
    q=m.group(1)
    ok = q in Cn
    if not ok:
        print('MISS:',q[:200])
