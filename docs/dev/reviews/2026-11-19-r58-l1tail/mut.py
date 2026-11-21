import subprocess,os,re,sys
D='/var/tmp/pcrec-pcrec/scratch/crit-l1tail/scope'; T='/home/pcrec/projects/pcrec/worktrees/crit-l1tail'
src=open(T+'/tests/memfn/arch_blind_check.py').read()
M=[]
for kw in ['pattern','pattern-esc','m','n','ms','ns','mc','mg','gu','var','under']:
    M.append(('del kw '+kw, "RXT_DATA_KW = frozenset((", None, ('kw',kw)))
muts=[]
def sub(name,old,new,count=1):
    assert src.count(old)>=1,(name,old)
    muts.append((name,src.replace(old,new,count)))
for kw in ['pattern','pattern-esc','m','n','ms','ns','mc','mg','gu','var','under']:
    s=src
    blk=re.search(r"RXT_DATA_KW = frozenset\(\((.*?)\)\)",s,re.S)
    items=[x.strip() for x in blk.group(1).replace('\n',' ').split(',') if x.strip()]
    items2=[x for x in items if x!="'%s'"%kw]
    assert len(items2)==len(items)-1,kw
    muts.append(('delkw '+kw, s[:blk.start(1)]+', '.join(items2)+s[blk.end(1):]))
sub('region never opens',"if kw in ('pattern', 'pattern-esc') and body.rstrip().endswith('|'):","if False:")
sub('region open only pattern (drop pattern-esc)',"if kw in ('pattern', 'pattern-esc') and body.rstrip().endswith('|'):","if kw == 'pattern' and body.rstrip().endswith('|'):")
sub('region open w/o endswith |',"and body.rstrip().endswith('|'):",":")
sub('region body mask off',"                out.append('')\n                continue\n            region = None","                region = None")
sub('region indent > -> >=',"indent > region","indent >= region")
sub('region indent > -> always',"indent > region","True")
sub('region ends not on blank',"if line.strip() and not line.startswith('#') and indent > region","if not line.startswith('#') and indent > region")
sub('region ends not on #',"if line.strip() and not line.startswith('#') and indent > region","if line.strip() and indent > region")
sub('comment test off',"if not line or line.startswith('#'):\n            out.append(line)\n            continue","if not line:\n            out.append(line)\n            continue")
sub('lstrip off (indented dirs unmasked)',"body = line.lstrip(' ')","body = line")
sub('mask whole line not just rest',"out.append(line[:len(line) - len(body)] + kw)","out.append('')")
sub('rxt mask noop',"        return mask_rxt(text)","        return text")
sub('tsv mask noop',"        return mask_tsv(text)","        return text")
sub('tests guard rxt -> any scope',"if scope == 'tests' and rel.endswith('.rxt')","if rel.endswith('.rxt')")
sub('tests guard tsv -> any scope',"if scope == 'tests' and rel.endswith('.tsv')","if rel.endswith('.tsv')")
sub('rxt guard -> code scope too: rxt guard dropped scope',"if scope == 'tests' and rel.endswith('.rxt')","if scope == 'tests'")
sub('mask_data call removed',"    text = mask_data(scope, rel, text)\n","")
sub('tsv: pattern col not masked',"if h.strip().lower() == 'pattern' or 'subject' in h.lower()","if 'subject' in h.lower()")
sub('tsv: subject col not masked',"if h.strip().lower() == 'pattern' or 'subject' in h.lower()","if h.strip().lower() == 'pattern'")
sub('tsv: header masked too',"out = [lines[0]]","out = ['']")
sub('tsv: all cols masked',"if i in cols else v","if True else v")
sub('tsv: no cols masked',"if i in cols else v","if False else v")
sub('tsv: pattern match substring',"h.strip().lower() == 'pattern'","'pattern' in h.lower()")
res=[]
for i,(n,t) in enumerate(muts):
    p='%s/mut/m%02d.py'%(D,i); os.makedirs(D+'/mut',exist_ok=True); open(p,'w').write(t)
    tmp='%s/tmp/m%02d'%(D,i); os.makedirs(tmp,exist_ok=True)
    r=subprocess.run(['python3','-I',p,T,T+'/tests/memfn/c4_allowlist.tsv','0'],capture_output=True,text=True,env=dict(os.environ,TMPDIR=tmp),timeout=120)
    fl=[l for l in r.stdout.split('\n') if l.startswith('FAIL')]
    sc=[l for l in fl if 'data-scope' in l]
    res.append((n,r.returncode,len(fl),len(sc),[l[:90] for l in fl[:2]]))
    print('%-45s rc=%d fails=%d scopectl=%d'%(n,r.returncode,len(fl),len(sc)),flush=True)
