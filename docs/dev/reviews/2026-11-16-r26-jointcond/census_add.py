import sys
f=sys.argv[1]; new=open(sys.argv[2]).read().rstrip("\n")+"\n\n"
s=open(f).read(); k=s.index("## PROBED-AND-HELD")
open(f,"w").write(s[:k]+new+s[k:])
