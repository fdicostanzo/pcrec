import sys,subprocess,re,ast,glob,os,collections
sys.path.insert(0,'/home/pcrec/projects/pcrec/docs/dev/lanes/sae1_evidence')
from ident_check import decode_escape
pc='/var/tmp/pcrec-pcrec/scratch/l1ffix/bin/pcrec'
W='/home/pcrec/projects/pcrec/worktrees/l1ffix'; B='/var/tmp/pcrec-pcrec/scratch/l1feat/trees/base'
miss=[ast.literal_eval(l.split('FACTS STREAM ',1)[1].strip()) for l in open(sys.argv[1]) if 'NOT IN THE FACTS' in l]
print(len(miss))
def pats(tree):
    d=collections.defaultdict(set)
    for f in glob.glob(tree+'/tests/**/*.rxt',recursive=True)+glob.glob(tree+'/tests/**/*.rxtin',recursive=True):
        r=subprocess.run([pc,'--list-source',f],capture_output=True)
        for l in r.stdout.decode('utf8','surrogateescape').splitlines():
            y=l.split('\t')
            if not l.startswith('#') and len(y)>=5 and y[0] in('pattern','pattern-esc'):
                d[decode_escape(y[4])].add(os.path.relpath(f,tree))
    return d
nw=pats(W); bs=pats(B)
c=collections.Counter()
for m in miss:
    inb=m in bs; files=sorted(nw.get(m,[]))
    c[(inb,tuple(files))]+=1
    if inb or not files: print('EXCEPT',m,inb,files)
for k,v in c.items(): print(v,k)
