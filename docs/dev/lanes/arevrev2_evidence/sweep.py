import itertools, subprocess, sys
sys.path.insert(0, sys.argv[1]); import model
probe = sys.argv[2]
ATOMS = ["a{1,2}", "a{0,2}", "(a{1,2})", "(?>ab|a)b{1,2}", "b", "(b)", "ab", "a?b",
         "\\ba{1,2}", "a{1,2}\\b", "(?:ab|a){1,2}", "(?=a)a{1,2}", "(a)a?", "a{1,2}?",
         "(a|b){1,2}", "a{1,2}+b?", "(?<=b)a{1,2}", "a{1,2}(?!b)", "(?:a|ab)b?"]
FOLLOWS = ["x", "b", "b\\1", "x\\1", "\\1", "", "b\\2", "\\2x"]
SUBJ = ["".join(t) for n in range(0, 4) for t in itertools.product("abx", repeat=n)] + ["aaba","aabx","abax","baax","abxb","aabb","aaax","abab","bab","aabaa"]
cells = []
for nb in (1, 2, 3):
    for brs in itertools.product(ATOMS, repeat=nb):
        if nb == 3 and len(set(brs)) < 3: continue
        body = "|".join(brs)
        if nb == 3 and sum(map(ord, body)) % 13: continue
        P = model.Parser(body); P.alt(); ng = P.ng
        for fol in FOLLOWS:
            if any(int(d) > ng for d in fol if d.isdigit()): continue
            for form in ("(?<=", "(?<!", "(?<*"):
                pat = form + body + ")" + fol
                for s in SUBJ:
                    cells.append((pat, s))
sys.stderr.write("%d cells\n" % len(cells))
text = "".join("%s\t%s\n" % c for c in cells)
pc = subprocess.run([probe, "m"], input=text, capture_output=True, text=True).stdout.splitlines()
assert len(pc) == len(cells), (len(pc), len(cells))
nd = nc = 0
with open(sys.argv[3], "w") as f:
    for (pat, s), line in zip(cells, pc):
        ref = line.split("\t")[2]
        try:
            rv = model.run("revdfa", pat, s); cu = model.run("cursor", pat, s)
        except Exception as e:
            rv = cu = "ERR %s" % e
        if cu != ref: nc += 1; f.write("CURSORDIFF\t%s\t%s\t%s\t%s\t%s\n" % (pat, s, ref, cu, rv))
        if rv != ref: nd += 1; f.write("REVDFADIFF\t%s\t%s\t%s\t%s\t%s\n" % (pat, s, ref, cu, rv))
print("cells %d; revdfa differs %d; cursor (control) differs %d" % (len(cells), nd, nc))
