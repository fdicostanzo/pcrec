import os, shutil, subprocess, sys, json
L="/var/tmp/pcrec-pcrec/scratch/crit-predlint/checks"
BASE=L+"/base"
env=dict(os.environ, PCREC_TMPDIR=L)
src=open(BASE+"/scripts/pred_doc_lint.py").read()
M=[]
def m(name, old, new, count=1): M.append((name, old, new, count))

m("RT title: rstrip('.') removed", 'full = " ".join(full.split()).rstrip(".")', 'full = " ".join(full.split())')
m("RT title: split ' (' removed", 'titles.add(full.split(" (")[0])', "pass")
m("RT title: ** opener removed", 'm = re.match(r"^\*\*(.+?)\*\*", ln)', 'm = None')
m("RT title: ### form removed", 'if ln.startswith("### "):\n            full = ln[4:]', 'if False:\n            full = ln[4:]')
m("PB fence skip in parse_base heads removed", "        if infence:\n            continue\n        if ln.startswith(\"### \"):", "        if ln.startswith(\"### \"):")
m("PD fence guard on details heading removed", 'if not infence and ln.startswith("## "):', 'if ln.startswith("## "):')
m("PD fence guard on FIELD_RE removed", 'mm = FIELD_RE.match(ln) if not infence else None', 'mm = FIELD_RE.match(ln)')
m("needs split: whitespace only (no comma)", 'p[mm.group(1)] += [x for x in re.split(r"[\s,]+", mm.group(2)) if x]', 'p[mm.group(1)] += [x for x in re.split(r"\s+", mm.group(2)) if x]')
m("needs: only first tag kept", 'p[mm.group(1)] += [x for x in re.split(r"[\s,]+", mm.group(2)) if x]', 'p[mm.group(1)] += [x for x in re.split(r"[\s,]+", mm.group(2)) if x][:1]')
m("rulings item marker '-' not required", 'items = [(ln, t) for ln, t in e["fields"].get("rulings", []) if t.strip().startswith("-")]', 'items = [(ln, t) for ln, t in e["fields"].get("rulings", [])]')
m("rulings item loop: skip L4 item check", 'rep.ok("L4")\n                m = re.search', 'rep.ok("L4")\n                continue\n                m = re.search')
m("statement = first non-meta line -> first line", 'if p["statement_line"] is None and not re.match(r"^(needs|by|was|modes):", t):', 'if p["statement_line"] is None:')
m("was: parse off", 'mm = re.match(r"^was:\s*(\S+)", t)', 'mm = None')
m("L7 piece end trims blanks off", 'while body_end > i + 1 and not lines[body_end - 1].strip():\n            body_end -= 1', 'pass')
m("L1 uniqueness per file not whole run", "seen_tags = {}\n    for word, P in pairs.items():\n        b, bp", "for word, P in pairs.items():\n        seen_tags = {}\n        b, bp")
m("L9 owners reset per file", "owners = {}\n    for P in pairs.values():\n        if not P[\"dp\"]:\n            continue", "owners = {}\n    for P in pairs.values():\n        owners = {}\n        if not P[\"dp\"]:\n            continue")
m("L9 same-tag twice counts", "tags = {t for t, _ in os_}", "tags = [t for t, _ in os_]")
m("L6 checks only first 30 lines", 'for i, ln in enumerate(bp["lines"]):', 'for i, ln in enumerate(bp["lines"][:30]):')
m("L6 skips last 2 lines", 'for i, ln in enumerate(bp["lines"]):', 'for i, ln in enumerate(bp["lines"][:-2]):')
m("L8 only first body line scanned", "body = p[\"text\"][1:]", "body = p[\"text\"][1:2]")
m("L5 ordinal always 0", "index[tag] = (word, len(index))", "index[tag] = (word, 0)")
m("RD ambiguity rc 2 off", "return (2 if len(hit) > 1", "return (0 if len(hit) > 1")
m("RD list status uses full status", '(p["status"] or "").split(" ")[0] != status', '(p["status"] or "") != status')
m("RD show level 2 omits details", "if level >= 2:", "if level >= 3:")
m("CLI exit code on fails -> 0", "return 1 if rep.fails else 0", "return 0")
m("report: fails not printed", "    for rule, where, msg in rep.fails:\n        out(", "    for rule, where, msg in []:\n        out(")
m("no-date accepted (DATE_RE off)", 'dm = DATE_RE.match(m.group("rest"))', 'dm = None')
M=[x for x in M if x]
only=sys.argv[1:]
res=[]
for i,(name,old,new,cnt) in enumerate(M):
    if only and str(i) not in only: continue
    if old not in src and old!="":
        print("%3d NOMATCH %s"%(i,name)); continue
    s=src.replace(old,new) if old.count else src
    d=L+"/mut/m%d"%i
    shutil.rmtree(d,ignore_errors=True); shutil.copytree(BASE,d)
    open(d+"/scripts/pred_doc_lint.py","w").write(s)
    def run(args):
        try:
            r=subprocess.run(["python3","-I",d+"/scripts/pred_doc_lint.py"]+args,env=env,capture_output=True,text=True,timeout=60)
            return r.returncode, r.stdout+r.stderr
        except Exception as e: return -9,str(e)
    a,ao=run(["--selftest"])
    b,bo=run(["--root",d+"/scripts/tests/pred_doc/root","--require-all"])
    n=src.count(old)
    print("%3d st=%s sample=%s %s%s"%(i,"GREEN" if a==0 else "red%d"%a,"GREEN" if b==0 else "red%d"%b,name,"" if n==1 else " (matches %d)"%n))
    shutil.rmtree(d,ignore_errors=True)
