import re,sys,csv
SRC="/Users/fdicostanzo/pcrec/src/gen/emit_vm.c"
CEN="/Users/fdicostanzo/pcrec/worktrees/revtools/tools/review/out/function_census.tsv"
lines=open(SRC,encoding='utf-8',errors='replace').read().split('\n')
rows=[]
with open(CEN) as f:
    r=csv.reader(f,delimiter='\t')
    next(r)  # comment
    hdr=next(r)
    for x in r:
        d=dict(zip(hdr,x))
        if 'emit_vm.c' in d['file']:
            rows.append(d)
rows.sort(key=lambda d:int(d['start_line']))
print(f"{'start':>6} {'end':>6} {'span':>5} {'code':>5} {'dep':>3} {'name':<26} {'sb':>4} {'pf':>4} {'buf':>4} {'arena':>5}")
for d in rows:
    s,e=int(d['start_line']),int(d['end_line'])
    body='\n'.join(lines[s-1:e])
    # strip comments crudely
    body_nc=re.sub(r'/\*.*?\*/','',body,flags=re.S)
    sb=len(re.findall(r'\bsb_(?:printf|puts|putc|addf|add)\s*\(',body_nc))
    pf=len(re.findall(r'\bsnprintf\s*\(',body_nc))
    buf=len(re.findall(r'\bchar\s+\w+\s*\[\s*\d+\s*\]',body_nc))
    ar=len(re.findall(r'\barena_|pcrec_arena',body_nc))
    print(f"{s:6} {e:6} {d['span_lines']:>5} {d['code_lines']:>5} {d['max_depth']:>3} {d['name']:<26} {sb:4} {pf:4} {buf:4} {ar:5}")
