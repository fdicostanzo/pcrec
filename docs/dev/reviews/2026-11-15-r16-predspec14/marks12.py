import re
F='/var/tmp/pcrec-pcrec/scratch/crit-predspec14/subject/predicates_draft_rev14.md'
L=open(F).read().split('\n')
cases={};cur=None
for i,l in enumerate(L,1):
    m=re.match(r'### 12\.\d+ (E-[A-Z0-9]+)',l)
    if m: cur=m.group(1); cases[cur]=[]; continue
    if l.startswith('## 13'): cur=None
    if cur and l.startswith('    '): cases[cur].append(l)
def strip_rx(s):
    # remove /.../ literals crudely and comments
    s=re.sub(r'#.*','',s)
    return s
for c,ls in cases.items():
    code='\n'.join(ls); nocom='\n'.join(re.sub(r'\s#.*$','',x) for x in ls)
    marks={'&':'&' in nocom,'|':bool(re.search(r'(?<![\\/\[])\|',re.sub(r'/(?:\\.|[^/\n])*/','',nocom))),
      ',':',' in re.sub(r'/(?:\\.|[^/\n])*/','',nocom),'/../':bool(re.search(r'/(?:\\.|[^/\n])+/',nocom)),
      '#':bool(re.search(r'(^|\s)#',code)),'"':'"' in nocom,'${':'${' in nocom,'$':bool(re.search(r'\$[a-z]',nocom)),
      '@':'@' in nocom,':=':':=' in nocom,'=':bool(re.search(r'[a-z_] ?= ?[^=]',re.sub(r':=|==|<=|>=','',nocom))),
      '!':'!' in nocom, '.':bool(re.search(r'[a-z]\.[a-z]',re.sub(r'/(?:\\.|[^/\n])*/','',nocom)))}
    print(c,len(ls),' '.join(k for k,v in marks.items() if v))
