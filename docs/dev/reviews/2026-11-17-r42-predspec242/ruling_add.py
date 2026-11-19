import sys
p,txt=sys.argv[1],open(sys.argv[2]).read().rstrip('\n')+'\n\n'
s=open(p).read(); i=s.index('## PROBED-AND-HELD'); open(p,'w').write(s[:i]+txt+s[i:])
