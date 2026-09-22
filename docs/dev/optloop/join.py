import json,math,collections
SP="/tmp/claude-501/-Users-fdicostanzo-pcrec/c7ec5900-bab2-4d19-b2df-f72f9b26896b/scratchpad"
rows=json.load(open(SP+"/rank.json")); st=json.load(open(SP+"/stamps.json"))
pats=json.load(open(SP+"/patterns.json"))
VMAP={"auto-caps":"auto-caps","auto-nocaps":"auto-nocaps","vm-caps":"vm-caps","vm-in":"vm-caps"}
def stampof(pat,var,k):
    e=st.get(pat,{}).get(VMAP.get(var,var))
    if not e or e["rc"]!=0: return "REFUSED"
    return e["stamps"].get(k,"-")
lose=[r for r in rows if r["class"]=="ranked" and r["ratio"]>1.0]
lose.sort(key=lambda r:-r["score"])
print(f'{"score":>6} {"ratio":>11} {"pattern":34s} {"reg":3s} {"var":11s} {"eng":4s} {"sel":22s} {"scan":10s} {"dfapre":22s} {"vmpre":10s} {"lang":10s} algo')
for r in lose:
    p,v=r["pattern"],r["pcrec_best"]
    print(f'{r["score"]:6.3f} {r["ratio"]:11.1f} {p:34.34s} {r["regime"][:3]:3s} {v:11s} '
          f'{stampof(p,v,"RX_ENGINE"):4.4s} {stampof(p,v,"RX_ENGINE_SEL"):22.22s} '
          f'{stampof(p,v,"RX_DFA_SCAN"):10.10s} {stampof(p,v,"RX_DFA_PREFILTER"):22.22s} '
          f'{stampof(p,v,"RX_VM_PREFILTER"):10.10s} {stampof(p,v,"RX_VM_PREFILTER_LANG"):10.10s} {r["algo"]}/{r["algo_ns"]:.0f} pc={r["pcrec_ns"]:.0f}')
