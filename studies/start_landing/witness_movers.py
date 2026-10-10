#!/usr/bin/env python3
"""[START-LANDING] rev 2 (lane landrev, SL-C2/SL-C4): WHICH IN-TREE WITNESSES
MOVE, derived, never hand-listed (STUDY; read-only on the tree).

    witness_movers.py PROTO_PCREC ROOT FILE... > movers.tsv

For every FILE (a sabotage row, a tests/ gate script, or a witness manifest
the reader census `readers.sh` found), extract every pattern it compiles that
can be read statically:
  - shell text: each `--pattern "..."` / `--pattern '...'` argument, with the
    pcrec flags on the same command (`-e utf8`, `-i`, `--no-captures`,
    `--engine=X`, `-fno-X`, `-fX`);
  - `cand_oracle_witnesses.tsv`: ROW <tab> FLAGS <tab> PATTERN;
  - a `tests/codegen/manifests/*.txt` list: one pattern per non-comment line.
compile it with the fact probe (proto.patch rev 2) and apply the design's
first-match RECOVER rows (census.py's `row_of`, the empty arm included). One
line per (file, pattern, flags): today's RECOVER row, the rev-2 row, and
MOVES when they differ. A pattern built at run time (a loop variable, a
heredoc) is not extracted: the summary counts the files where the grep for
`--pattern` found more occurrences than were extracted (`unparsed`), so the
gap is visible rather than silent.
"""
import os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PC, ROOT, FILES = sys.argv[1], sys.argv[2], sys.argv[3:]
TMP = tempfile.mkdtemp(prefix="wm.", dir=os.environ.get("TMPDIR", "."))
FLAG = re.compile(r"(?<!\S)(-e utf8|-e byte|-i|--no-captures|--engine=\w+|-f(?:no-)?[a-z][a-z0-9-]*(?:=\S+)?)(?=\s|$)")


def sh_unquote(q, s):
    if q == "'":
        return s
    return re.sub(r'\\([\\"$`])', r"\1", s)


def extract(path):
    txt = open(path, encoding="utf8", errors="replace").read()
    out, total = [], 0
    base = os.path.basename(path)
    if base == "cand_oracle_witnesses.tsv":
        for ln in txt.split("\n"):
            if not ln or ln.startswith("#"): continue
            f = ln.split("\t")
            if len(f) >= 3:
                total += 1
                out.append((f[2], [] if f[1] == "-" else f[1].split()))
        return out, total
    if path.endswith(".txt") and "/manifests/" in path:
        for ln in txt.split("\n"):
            if ln.strip() and not ln.startswith("#"):
                total += 1
                out.append((ln.split("\t")[0], []))
        return out, total
    for m in re.finditer(r"--pattern\b", txt):
        total += 1
    # one logical command per line (a backslash-newline joins)
    for line in txt.replace("\\\n", " ").split("\n"):
        for m in re.finditer(r"--pattern\s+(\"((?:[^\"\\]|\\.)*)\"|'([^']*)')", line):
            q = m.group(1)[0]
            pat = sh_unquote(q, m.group(2) if q == '"' else m.group(3))
            if "$" in pat and re.search(r"\$(\{|[A-Za-z_0-9])", pat):
                continue                      # a shell variable: built at run time
            flags = [f for f in FLAG.findall(line[:m.start()]) + FLAG.findall(line[m.end():])]
            out.append((pat, flags))
    return out, total


def probe(pat, flags):
    out = os.path.join(TMP, "w.c")
    args = [PC, "--features", "all", "-p", "rx", "-o", out] + [x for f in flags for x in f.split()] + ["--pattern", pat]
    try:
        r = subprocess.run(args, capture_output=True, timeout=120, env=dict(os.environ, PCREC_LANDPROBE="1"))
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "-", "-"
    if r.returncode != 0:
        return "REFUSED", "-", "-"
    err = r.stderr.decode("utf8", "replace").split("\n")
    art = open(out, encoding="latin-1").read()
    m = re.search(r'_DFA_START "([^"]*)"', art)
    today = m.group(1) if m else "none"
    if 'DFA_SCAN "empty"' in art:
        e = [l for l in err if l.startswith("LANDEMPTY")]
        w = dict(kv.split("=", 1) for kv in e[-1].split("\t")[1:])["fixedw"] if e else "?"
        return today, "empty(W=%s)" % w, today
    lines = [l for l in err if l.startswith("LANDPROBE")]
    if not lines or today == "none":
        return today, "-", today
    f = dict(kv.split("=", 1) for kv in lines[-1].split("\t")[1:])
    if f.get("route") != "dfa": new = today
    elif f["recover"] == "pinned": new = "pinned"
    elif int(f["fixedw"]) >= 0: new = "end-minus-width"
    elif f["land"] == "OK" and f["seeded"] == "0" and f["next"] != "none": new = "landing"
    else: new = "reverse-pass"
    return today, "W=%s land=%s" % (f["fixedw"], f["land"]), new


print("file\tpattern\tflags\ttoday\tfacts\trev2\tmoves")
nf = nm = 0; unparsed = []
for path in FILES:
    rel = os.path.relpath(path, ROOT)
    pats, total = extract(path)
    seen = set()
    for pat, flags in pats:
        k = (pat, tuple(flags))
        if k in seen: continue
        seen.add(k)
        today, facts, new = probe(pat, flags)
        mv = "MOVES" if new not in (today, "-") and today not in ("REFUSED", "TIMEOUT", "none") else ""
        nm += bool(mv)
        print("\t".join([rel, pat, " ".join(flags) or "-", today, facts, new, mv]), flush=True)
    nf += 1
    if total > len(pats):
        unparsed.append("%s:%d/%d" % (rel, total - len(pats), total))
print("FILES %d MOVERS %d UNPARSED %d %s" % (nf, nm, len(unparsed), " ".join(unparsed)), file=sys.stderr)
