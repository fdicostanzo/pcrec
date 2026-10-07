#!/usr/bin/env python3
"""Oracle-only equivalence check: for each (greedy pattern, possessive
spelling) pair, run libpcre2 (pcre2test) on both over a subject sweep and
report cells where span/captures differ.  Input: TSV lines
  id <TAB> mods <TAB> greedy <TAB> possessive <TAB> claim <TAB> alphabet(py-escaped list)
Output: per-id diff count + first witness."""
import sys, subprocess, itertools, random, ast, os
PCRE2TEST = os.environ.get("PCRE2TEST", "pcre2test")
random.seed(7)

def subjects(alpha, maxlen=int(os.environ.get("ML","2")), nrand=int(os.environ.get("NR","150")), rmax=7):
    out = [""]
    for L in range(1, maxlen + 1):
        out += ["".join(t) for t in itertools.product(alpha, repeat=L)]
    for _ in range(nrand):
        L = random.randint(maxlen + 1, rmax)
        out.append("".join(random.choice(alpha) for _ in range(L)))
    return out

def enc(s, utf):
    r = []
    for ch in s:
        o = ord(ch)
        r.append("\\x{%x}" % o)
    return "".join(r)

def run(cases):
    # one pcre2test run for all cases; delimit results with a marker pattern
    lines = []
    for c in cases:
        for which in ("g", "p"):
            pat = c[which]
            mods = "aftertext" + ("," + c["mods"] if c["mods"] else "")
            lines.append('"%s"%s' % (pat, mods))
            for s in c["subj"]:
                lines.append(enc(s, "utf" in c["mods"]) if s else "\\=")
            lines.append("")
    inp = "\n".join(lines) + "\n"
    r = subprocess.run([PCRE2TEST, "-q"], input=inp.encode("latin-1", "backslashreplace"),
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.stdout.decode("latin-1")

def parse(out):
    # returns list of per-pattern result lists
    res = []; cur = None; cursubj = None
    for ln in out.split("\n"):
        if ln.startswith('"'):
            cur = []; res.append(cur); continue
        if cur is None: continue
        if ln == "": continue
        if ln.startswith("Failed") or ln.startswith("**"):
            cur.append("ERR:" + ln); continue
        if ln.startswith(" ") or ln.startswith("No match") or ln.startswith("\\"):
            pass
        if ln.startswith("\\x") or ln == "\\=":
            cur.append([]); continue
        if cur and isinstance(cur[-1], list):
            cur[-1].append(ln.strip())
    return res

def main():
    cases = []
    for ln in open(sys.argv[1]):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("#"): continue
        f = ln.split("\t")
        alpha = ast.literal_eval(f[5])
        cases.append(dict(id=f[0], mods=f[1], g=f[2], p=f[3], claim=f[4],
                          subj=subjects(alpha)))
    CH = 40
    allres = []
    for i in range(0, len(cases), CH):
        chunk = cases[i:i + CH]
        allres += parse(run(chunk))
    assert len(allres) == 2 * len(cases), (len(allres), len(cases))
    tot = {}
    for k, c in enumerate(cases):
        rg, rp = allres[2 * k], allres[2 * k + 1]
        errs = [x for x in rg + rp if isinstance(x, str)]
        if errs:
            print("%s\tERROR\t%s\t%s" % (c["id"], c["g"], errs[0])); continue
        nd = 0; wit = ""
        for s, a, b in zip(c["subj"], rg, rp):
            if a != b:
                nd += 1
                if not wit: wit = "%r g=%s p=%s" % (s, a, b)
        key = (c["claim"], nd > 0)
        tot[key] = tot.get(key, 0) + 1
        print("%s\t%s\t%s\tdiff=%d/%d\t%s\t%s" % (c["id"], c["claim"], c["g"], nd, len(c["subj"]), c["mods"], wit))
    print("#SUMMARY", sorted(tot.items()), file=sys.stderr)
main()
