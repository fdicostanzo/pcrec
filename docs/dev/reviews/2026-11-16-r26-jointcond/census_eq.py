import re,sys
L=open(sys.argv[1]).read().split("\n")
seen=set()
for i,ln in enumerate(L,1):
    for m in re.finditer(r"`([^`]+)`",ln):
        s=m.group(1)
        for e in re.finditer(r"(?<![=<>!:|])=(?!=)",s):
            ctx=s[max(0,e.start()-25):e.end()+12]
            if ctx not in seen:
                seen.add(ctx); print(i,"\t",ctx)
