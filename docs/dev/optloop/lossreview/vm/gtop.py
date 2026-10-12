import sys,re
# print the hottest executed source lines of rx.c.gcov
rows=[]
for l in open(sys.argv[1]):
  m=re.match(r'\s*([0-9]+)\*?:\s*([0-9]+):(.*)',l)
  if m: rows.append((int(m.group(1)),int(m.group(2)),m.group(3)))
N=int(sys.argv[2]) if len(sys.argv)>2 else 40
for c,ln,t in sorted(rows,reverse=True)[:N]: print('%12d %6d %s'%(c,ln,t[:150]))
