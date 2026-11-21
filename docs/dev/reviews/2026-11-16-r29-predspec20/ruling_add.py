import sys
F='/var/tmp/pcrec-pcrec/scratch/crit-predspec20/ruling/findings.md'
txt=open(F).read(); new=open(sys.argv[1]).read().rstrip('\n')+'\n\n'
k=txt.index('## PROBED-AND-HELD')
open(F,'w').write(txt[:k]+new+txt[k:])
