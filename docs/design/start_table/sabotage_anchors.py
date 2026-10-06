#!/usr/bin/env python3
# docs/design/start_table/sabotage_anchors.py -- maps every sabotage row whose
# SAB_FILE is src/gen/emit_dfa.c or src/gen/emit_vm.c to the top-level function
# (or table) its SAB_BEFORE anchor sits in, at the current tree, and marks the
# rows inside the start family (argv[2], comma-separated names). The K35 count
# behind start_table.md §3.5. Usage: sabotage_anchors.py ROOT FAMILY_NAMES
# Read-only; prints TSV (row, file, owner, line, FAMILY?) and a total on stderr.
import os,re,sys,glob,subprocess
root=sys.argv[1]
fam=set(sys.argv[2].split(','))
files={}
def funcs(path):
    if path in files: return files[path]
    L=open(os.path.join(root,path),encoding='utf-8',errors='replace').read().split('\n')
    # map line -> enclosing top-level definition name
    owner=[None]*len(L); cur=None
    for i,l in enumerate(L):
        m=re.match(r'^(?:static\s+)?(?:const\s+)?[A-Za-z_][\w\s\*]*?\b([A-Za-z_]\w*)\s*(\(|\[\]\s*=)',l)
        if m and not l.startswith((' ','\t','#','/','*')): cur=m.group(1)
        owner[i]=cur
    files[path]=(L,owner); return files[path]
def shval(txt,key):
    # crude: run bash to source the file and echo the var
    r=subprocess.run(['bash','-c','set +u; source "$1" >/dev/null 2>&1; printf "%s" "${!2}"','_',txt,key],capture_output=True,text=True)
    return r.stdout
rows=[]
for f in sorted(glob.glob(os.path.join(root,'tests/mech/sabotages/*.sh'))):
    sf=shval(f,'SAB_FILE')
    if sf not in ('src/gen/emit_dfa.c','src/gen/emit_vm.c'): continue
    before=shval(f,'SAB_BEFORE')
    if not before: rows.append((os.path.basename(f),sf,'?NOBEFORE')); continue
    L,owner=funcs(sf)
    txt='\n'.join(L)
    idx=txt.find(before)
    if idx<0: rows.append((os.path.basename(f),sf,'?NOTFOUND')); continue
    line=txt[:idx].count('\n')
    rows.append((os.path.basename(f),sf,owner[line] or '?', line+1))
hit=[r for r in rows if r[2] in fam]
for r in rows:
    print('\t'.join(map(str,r)), 'FAMILY' if r[2] in fam else '')
print('TOTAL_GEN_ROWS',len(rows),'FAMILY_ROWS',len(hit),file=sys.stderr)
