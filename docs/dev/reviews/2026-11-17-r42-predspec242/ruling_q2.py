import re,sys
C=re.sub(r'\s+',' ',open(sys.argv[1]).read())
F=re.sub(r'\s+',' ',open(sys.argv[2]).read())
qs=open(sys.argv[3]).read().split('\n')
for q in qs:
    if not q.strip(): continue
    q=re.sub(r'\s+',' ',q.strip())
    print('OK ' if (q in C or q in F) else 'MISS', q[:100], [m.start() for m in re.finditer(re.escape(q),C)][:2])
