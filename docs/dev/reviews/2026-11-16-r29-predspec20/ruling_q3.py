import re
exec(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec20/ruling/work/q2.py').read().split('seen=set()')[0])
OQ=[q for q in qs]
ALL=' || '.join(OQ)
def words(x): return re.findall(r"[a-z0-9']+",x.lower())
grams=set()
for q in OQ:
    w=words(q)
    for i in range(len(w)-3): grams.add(tuple(w[i:i+4]))
# iterate quoted strings in rev20 normalized S with line map
for m in re.finditer(r'"([^"]{6,600}?)"',S):
    t=m.group(1)
    w=words(t)
    g=[tuple(w[i:i+4]) for i in range(len(w)-3)]
    if not g or not any(x in grams for x in g): continue
    # unescape markdown pipes
    t2=t.replace('\\|','|')
    if any(t2 in q for q in OQ):
        continue
    # allow '...' elisions
    parts=[p.strip() for p in re.split(r'\s*\.\.\.\s*',t2) if p.strip()]
    if all(any(p in q for q in OQ) for p in parts): 
        print('ELIDED-OK L%d: %s'%(m2[m.start()],t2[:100]));continue
    print('MISMATCH L%d: %s'%(m2[m.start()],t2[:300]))
