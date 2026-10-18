#!/usr/bin/env python3
"""kvcensus --selftest: every instrument against witnesses whose answer is known
from the pattern text, and in the FAILING direction against a PLANT (a machine
or a set edited so the instrument must change its answer). Each line is
PASS/FAIL; the transcript is committed as selftest.txt.

    PCREC=build/pcrec PROBE=build/kv/pcrec-kv python3 docs/dev/kvcensus/selftest.py
"""
import copy, os, random, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kvdfa, kvvm, kvctx, kvpcre  # noqa: E402

PCREC = os.environ.get("PCREC", "build/pcrec")
PROBE = os.environ.get("PROBE", "build/kv/pcrec-kv")
fails = 0


def ck(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print("%s  %-58s got=%r%s" % ("PASS" if ok else "FAIL", name, got, "" if ok else " want=%r" % (want,)))


def C(p, *ex):
    return subprocess.run([PCREC, "-p", "rx", "--features", "all", "-fno-scan-edge", "-o", "-", *ex,
                           "--pattern", p], capture_output=True).stdout.decode("latin-1")


def LF(p, *ex):
    c = C(p, "--engine=dfa", "--no-captures", *ex)
    A = kvdfa.Machine(c, "anchored")
    return A, kvdfa.lang(A, A.starts())


# ---- 1. exactness (the language machine) -----------------------------------
A, L = LF("abc\\d{3,7}")
ck("exact abc\\d{3,7} = span = 6", (L["exact"], L["span"]), (6, 6))
A, L = LF("ab|cd")
ck("exact ab|cd = 1 (a product would admit ad)", L["exact"], 1)
ck("ab|cd counterexample pair", L["cex"] is not None, True)
A, L = LF("[ac][bd]")
ck("exact [ac][bd] = 2", L["exact"], 2)
def split(M, byte):
    """PLANT helper: give `byte` a class of its own (a copy of its column)."""
    k = M.ncl
    old = M.bc[byte]
    M.bc = list(M.bc); M.bc[byte] = k; M.ncl += 1
    for r in range(M.nrow):
        M.next[r].append(M.next[r][old])
    return k


A2 = copy.deepcopy(A)        # PLANT: 'c' enters a COPY of the shared row that has no 'd' edge
kc, kd = split(A2, ord("c")), split(A2, ord("d"))
r1 = A2.next[0][kc]
A2.next.append(list(A2.next[r1])); A2.acc.append(A2.acc[r1]); A2.acc_any.append(A2.acc_any[r1])
A2.next[-1][kd] = None
A2.nrow += 1
A2.next[0][kc] = A2.nrow - 1
A2.live.add(A2.nrow - 1)
ck("PLANT [ac][bd] minus c->d: exact drops to 1", kvdfa.lang(A2, A2.starts())["exact"], 1)
A, L = LF("abc[α-ω]x", "-e", "utf8")
ck("utf8 abc[alpha-omega]x: exact 4 of span 6 (mixed)", (L["exact"], L["span"]), (4, 6))

# ---- 2. delta_uniform / consumable (the forward machine) -------------------
F = kvdfa.Machine(C("abc\\d{3,7}"), "forward")
A, L = LF("abc\\d{3,7}")
u = kvdfa.uniform(F, L["S"], L["exact"])
ck("uniform abc\\d{3,7}: true at all six", (u[0], u[1], u[2]), (6, 6, [True] * 6))
F2 = copy.deepcopy(F)        # PLANT: byte '5' leads somewhere else at offset 3
r3 = F2.step(F2.step(F2.step(0, ord("a")), ord("b")), ord("c"))
other = next(t for t in range(F2.nrow) if t not in (None, F2.step(r3, ord("0"))) and t in F2.live and t != 0)
F2.bc = list(F2.bc); F2.bc[ord("5")] = F2.ncl
for r in range(F2.nrow):
    F2.next[r].append(other if r == r3 else F2.next[r][F.bc[ord("0")]])
u2 = kvdfa.uniform(F2, L["S"], L["exact"])
ck("PLANT a non-uniform digit at offset 3: contig 3, flag[3] 0", (u2[0], u2[2][3]), (3, False))
F = kvdfa.Machine(C("ac\\d|bc"), "forward")
A, L = LF("ac\\d|bc")
ck("uniform ac\\d|bc: false at 0", kvdfa.uniform(F, L["S"], L["exact"])[2][0], False)
F = kvdfa.Machine(C("\\bfoobar\\b"), "forward")
ck("\\bfoobar\\b forward machine is seeded", F.seeded, True)
nonw = frozenset(range(256)) - kvdfa.W
ck("\\bfoobar\\b under (?<!\\w)+absent: one entry row", len(F.starts(nonw, True)), 1)
ck("\\bfoobar\\b under every context: two entry rows", len(F.starts()), 2)

F = kvdfa.Machine(C("xx"), "forward")
ck("forward_path xx from {x}: one row through both", kvdfa.forward_path(F, {ord("x")})[:2], (2, 2))
F2 = copy.deepcopy(F)        # PLANT: after x, 'q' engages a different live row
r1 = F2.step(0, ord("x"))
kq = split(F2, ord("q"))
F2.next[r1][kq] = r1         # a live row other than x's target
ck("PLANT xx with q engaging elsewhere: forward_path best 1", kvdfa.forward_path(F2, {ord("x")})[0], 1)
F = kvdfa.Machine(C("x[ab]c"), "forward")
ck("forward_path x[ab]c: the restart byte x forks offset 1 (best 1)", kvdfa.forward_path(F, {ord("x")})[0], 1)
F = kvdfa.Machine(C("(?:a||b)c"), "forward")
A, L = LF("(?:a||b)c")
ck("(?:a||b)c: S_0 is {a,b,c} but the scan restarts on {c} only", (kvdfa.setstr(L["S"][0]), sorted(
   b for b in range(256) if F.step(0, b) not in (0, None))), ("61-63", [ord("c")]))

# ---- 3. whole-cover ---------------------------------------------------------
for p, k in (("abc", 3), ("(?i)abc", 3), ("foo|foobar", 3), ("abcd?", 0), ("\\babc", 0), ("a[0-9]{2}", 3)):
    A, L = LF(p)
    ck("whole(%s) = %d" % (p, k), kvdfa.whole(A, L, A.starts()), k)
A, L = LF("abc")
A2 = copy.deepcopy(A)        # PLANT: an extra live edge out of the final row
fin = next(iter(next(iter(L["Qk"]))))
A2.next[fin][A2.bc[ord("z")]] = fin
A2.live.add(fin)
ck("PLANT abc with a live edge after the end: whole 0", kvdfa.whole(A2, kvdfa.lang(A2, {0}), {0}), 0)

# ---- 4. the VM literal prefix ------------------------------------------------
def IR(p):
    return subprocess.run([PCREC, "--features", "all", "--emit-ir", "--pattern", p],
                          capture_output=True).stdout.decode("latin-1")
ck("vm ab(?=c)(x)\\1: strict lit 2 (stops at the assert)", kvvm.vm_prefix(IR("ab(?=c)(x)\\1"))[:2], (2, 2))
ck("vm (a)bc\\1: strict 0, relaxed 3", (kvvm.vm_prefix(IR("(a)bc\\1"))[0], kvvm.vm_prefix(IR("(a)bc\\1"))[2]), (0, 3))
ck("vm (?:ab|cd)(x)\\1: 0 (dispatch)", kvvm.vm_prefix(IR("(?:ab|cd)(x)\\1"))[1], 0)
ck("vm (?i)(foo)\\1: relaxed cls 3, lit 0", kvvm.vm_prefix(IR("(?i)(foo)\\1"))[2:], (0, 3))

# ---- 5. context shapes -------------------------------------------------------
W = kvdfa.W
ck("ctx \\bfoo: leading \\b, body foo", kvctx.parse(b"\\bfoo")["body"], b"foo")
ck("ctx \\bfoo|bar: top-level alternation declines", kvctx.parse(b"\\bfoo|bar")["why"], "toplevel-alt")
ck("expressible \\b before a word set: (?<!\\w), absent ok",
   kvctx.expressible(("b", None), frozenset(b"f"), False, W)[:2], (True, True))
ck("expressible \\b before a non-word set: (?<=\\w), absent fails",
   kvctx.expressible(("b", None), frozenset(b" "), False, W)[:2], (True, False))
ck("PLANT \\b before a straddling set [a ]: not expressible",
   kvctx.expressible(("b", None), frozenset(b"a "), False, W)[0], False)
ck("expressible (?<=ab): positive width 2", kvctx.expressible(("lb+", b"ab"), None, False, W)[0], True)
ck("expressible (?<!ab): a disjunction, not expressible", kvctx.expressible(("lb-", b"ab"), None, False, W)[0], False)
ck("expressible (?<!x): width 1, absent satisfies", kvctx.expressible(("lb-", b"x"), None, False, W)[:2], (True, True))
ck("expressible (?<=a|b): not a product", kvctx.expressible(("lb+", b"a|b"), None, False, W)[0], False)

ck("anchors ^\\d{5}(-\\d{4})?$ -> ^, $, body", kvctx.strip_anchors(b"^\\d{5}(-\\d{4})?$"), ("^", "$", b"\\d{5}(-\\d{4})?"))
ck("anchors ^a|b: top-level alternation declines", kvctx.strip_anchors(b"^a|b"), None)
Fz = kvdfa.Machine(C("[a-z]{0,16}", "--engine=dfa", "--no-captures"), "forward")
ck("nullable [a-z]{0,16}: the forward start row accepts", bool(Fz.ok and Fz.acc_any[0]), True)
Fz = kvdfa.Machine(C("[a-z]{1,16}", "--engine=dfa", "--no-captures"), "forward")
ck("PLANT non-nullable [a-z]{1,16}: the start row does not", bool(Fz.ok and Fz.acc_any[0]), False)

# ---- 6. the PCRE2 control, both directions -----------------------------------
P = kvpcre.Pat(b"abc\\d{3,7}")
ck("pcre abc123 is a prefix", P.is_prefix(b"abc123"), True)
ck("pcre abd is not a prefix", P.is_prefix(b"abd"), False)
A, L = LF("ab|cd")
ok, bad = L["cex"]
P = kvpcre.Pat(b"ab|cd")
ck("pcre confirms the ab|cd counterexample pair", (P.is_prefix(ok), P.is_prefix(bad)), (True, False))
rnd = random.Random(1)
A, L = LF("abc\\d{3,7}")
Sbad = list(L["S"]); Sbad[4] = frozenset(range(256))   # PLANT: a superset claimed exact
P = kvpcre.Pat(b"abc\\d{3,7}")
miss = sum(not P.is_prefix(bytes(rnd.choice(sorted(s)) for s in Sbad[:5])) for _ in range(40))
ck("PLANT a superset position claimed exact: PCRE2 rejects some", miss > 0, True)
P = kvpcre.Pat("abc[α-ω]x".encode(), utf8=True)
ck("pcre utf8 truncated abc\\xce is a prefix", P.is_prefix(b"abc\xce"), True)
ck("pcre utf8 abc\\xcf\\xb1 is not", P.is_prefix(b"abc\xcf\xb1"), False)
P, Q = kvpcre.Pat(b"\\bfoo"), kvpcre.Pat(b"(?<!\\w)foo")
ck("pcre \\bfoo == (?<!\\w)foo on 5 contexts",
   [P.match_len(b"foo", c) == Q.match_len(b"foo", c) for c in (b"", b"a", b" ", b"_", b"-")], [True] * 5)
P, Q = kvpcre.Pat(b"\\b-x"), kvpcre.Pat(b"(?<!\\w)-x")
ck("PLANT the wrong rewrite of \\b-x differs somewhere",
   any(P.match_len(b"-x", c) != Q.match_len(b"-x", c) for c in (b"", b"a", b" ")), True)

# ---- 7. the site probe ---------------------------------------------------------
out = os.path.abspath("build/kv/selftest_sites.tsv")
if os.path.exists(out):
    os.unlink(out)
subprocess.run([PROBE, "-p", "rx", "--features", "all", "-o", "/dev/null", "--pattern", "x[a-z]+@y"],
               env=dict(os.environ, KV_OUT=out), capture_output=True)
rows = [l.rstrip("\n").split("\t") for l in open(out)] if os.path.exists(out) else []
pf = [r for r in rows if r[3] == "PF"]
ck("probe x[a-z]+@y: one PF site, DFA_SCAN", [(r[3], r[7]) for r in pf], [("PF", "DFA_SCAN")])
ck("probe x[a-z]+@y: proven0 = {x}", sorted(kvdfa.hexset(pf[0][22])) if pf else None, [ord("x")])
ck("probe x[a-z]+@y: PRE site present, proven nothing", [len(kvdfa.hexset(r[22])) for r in rows if r[3] == "PRE"], [256])

print("== selftest %s: %d failed" % ("PASS" if not fails else "FAIL", fails))
sys.exit(1 if fails else 0)
