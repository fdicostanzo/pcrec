# lane tt6fix sibling census: shell call sites that run, with stderr captured or merged,
# a tree script that (transitively) sources an advisory-notice helper.
import os, re, subprocess, sys
root = sys.argv[1]
HELPERS = ("tests/lib/timeout_bin.sh", "tests/lib/cc_resolve.sh", "tests/lib/resolve_pcre2.sh")
files = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True).stdout.split()
sh = [f for f in files if not f.endswith(".md") and (f.endswith((".sh", ".test", ".bash")) or f.startswith("scripts/") and "." not in os.path.basename(f) or f == "Makefile" or f.endswith("Makefile"))]
src = {}
for f in sh:
    try: src[f] = open(os.path.join(root, f), errors="replace").read()
    except OSError: pass
SRC_RE = re.compile(r'(?:^|[;&|]\s*|\bthen\s+)(?:\.|source)\s+"?[^"\s]*?((?:tests|scripts|memfn)/[A-Za-z0-9_./-]+\.sh)"?', re.M)
direct = {f for f, s in src.items() if any(re.search(r'(?:\.|source)\s+"?[^"\n]*' + re.escape(os.path.basename(h)), s) for h in HELPERS)}
# transitive: sources a file that is a sourcer
sourcer = set(direct) | set(HELPERS)
changed = True
while changed:
    changed = False
    for f, s in src.items():
        if f in sourcer: continue
        for m in SRC_RE.finditer(s):
            tgt = m.group(1)
            if any(tgt.endswith(x) for x in sourcer):
                sourcer.add(f); changed = True; break
# quiet sourcers: every helper source line redirects 2>/dev/null
CALL = re.compile(r'(?:bash|sh)\s+"?\$[{]?[A-Za-z_]+[}]?/([A-Za-z0-9_./-]+)"?|(?:bash|sh)\s+"?((?:tests|scripts|memfn)/[A-Za-z0-9_./-]+)"?')
hits = []
for f, s in src.items():
    for i, line in enumerate(s.split("\n"), 1):
        if line.lstrip().startswith("#"): continue
        if not re.search(r'2>&1|2>\s*"?\$|2>\s*[A-Za-z/]', line) or re.search(r'2>\s*/dev/null', line) and '2>&1' not in line: continue
        for m in CALL.finditer(line):
            tgt = os.path.normpath((m.group(1) or m.group(2)))
            cand = [x for x in sourcer if x.endswith(tgt)]
            if cand:
                hits.append((f, i, cand[0], line.strip()[:150]))
print("sourcers (direct+transitive):", len(sourcer))
print("capture sites of a sourcer's stderr:", len(hits))
for h in sorted(hits):
    print("%s:%d -> %s | %s" % h)
