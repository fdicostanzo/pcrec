#!/usr/bin/env python3
"""[START-SET] edge lane: THE MUTATION RUN.  Do the draft edge cells SEE each
wrong variant of the two hats at ANSWER level?

    mut.py OUT_TSV [ID_SUBSTRING ...]
Env: PCREC, FSP (built fsp.c), W (scratch), ORACLE (built oracle.c; for the
give-up allowance), SWEEP=0 to skip the exhaustive arm, JOBS (default 4).

For every block of the drafts (`*.rxt` + `utfcheck_cells.tsv`, read back by
rxtcells.py, i.e. the cells AS WRITTEN), it compiles the base artifact
(today's emitter = the -fno-start-set arm), reads S (fsp) and the machine's
E / per-seed escape sets / Tdfa (hat.py), and builds the CORRECT hat twin
(D0 / V0) and every MUTANT that applies to the block:

  DFA hat   D0 ok          T = S ∩ E*, admitted iff T ⊊ E, conditional re-seed
            D1 r3          T = S ∩ E, admitted iff S ∩ E ≠ ∅ and ⊊ E (the sound-F1 bug)
            D2 omit-seed-k E* built without seed state k (each k ≠ s0 in turn)
            D3 omit-s0     E* built without s0
            D4 no-reseed   D0's table, re-seed removed
            D5 uncond      D0's table, re-seed `pos ? seed[..] : s0` (pf_emit_ofs_reseed's form)
            D6 pre-utf     a no-candidate early return hoisted above the -futf-check refusal
            D7 from-sf     the scan started at search_from instead of the K82 handoff's lo
            D9 drop-b      D0's T without member b (each b in turn)
            D0m / D10 / D11  |T| = 1: the first-memchr-bounded form, both landing paths re-seeded /
                           the hit path's re-seed deleted / the n-1 clamp path's deleted (S483/S484)
            DX Tdfa        T = Tdfa, the machine's own floor (rev 2 §4.1a calls it sound; tested, not assumed)
  VM hat    V0 ok          the entry + retry seek (../twin/vmtwin.py's shape)
            V1 late        every seek starts one byte late (S479's plant)
            V2 drop-b      S without member b (each b that begins a match in the cells, + one that does not)
            V3 nullable    the seek applied to a NULLABLE pattern (V's non-nullable conjunct removed)
            V4 retry-skip  the retry seek skips the next position (a valid later start)
            V5 pre-utf     the entry seek's no-candidate return above rx_valid_upto
            (V6 from-sf: no VM-hat artifact has a handoff — see startset.md §6.4)

A variant whose admission declines the block is the base program and is
reported `declined`.  Each built twin runs every case; DETECTED = some case's
answer differs from the cell's expectation.  The base artifact runs the same
cases (it must agree with every cell — the oracle check of the cells against
pcrec itself).  The SWEEP arm runs twin vs base over every subject on the
block's own subject alphabet (<= 5 bytes, length <= 6, every startpos) to say
whether an undetected mutant is OBSERVABLE at all on that machine.
"""
import itertools, json, os, re, subprocess, sys, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hat, rxtcells

W = os.environ["W"]; SWEEP = os.environ.get("SWEEP", "1") != "0"; JOBS = int(os.environ.get("JOBS", "4"))

DRV = r'''
#include <stdio.h>
#include <string.h>
#include <stddef.h>
%(inc)s
int main(void) { char line[1 << 16]; static unsigned char s[1 << 15];
  while (fgets(line, sizeof line, stdin)) {
    char *sp = strchr(line, ' '); *sp = 0; size_t f = strtoul(sp + 1, NULL, 10);
    size_t n = strlen(line) / 2; for (size_t i = 0; i < n; i++) { unsigned v; sscanf(line + 2 * i, "%%2x", &v); s[i] = (unsigned char)v; }
%(calls)s
    putchar('\n'); } return 0; }
'''
CALL = r'''    { ptrdiff_t c[RX_NCAPS][2]; memset(c, 0xff, sizeof c); int r = %(p)s_search(n ? s : (const unsigned char *)"", n, f, c);
      printf("%%s%%d", %(first)s ? "" : "|", r); if (r == 1) for (int g = 0; g < RX_NCAPS; g++) printf(" %%td %%td", c[g][0], c[g][1]); }
'''


def build(d, arts):
    """arts: [(prefix, src)] -> driver path.  Every artifact was compiled with its own -p."""
    for p, src in arts: open(os.path.join(d, p + ".c"), "w").write(src)
    inc = "#include <stdlib.h>\n" + "".join('#include "%s.h"\n' % p for p, _ in arts)
    calls = "".join(CALL % {"p": p, "first": "1" if i == 0 else "0"} for i, (p, _) in enumerate(arts))
    open(os.path.join(d, "drv.c"), "w").write(DRV % {"inc": inc, "calls": calls})
    exe = os.path.join(d, "drv")
    r = subprocess.run(["gcc-16", "-O1", "-w", "-I" + d, "-o", exe, os.path.join(d, "drv.c")] + [os.path.join(d, p + ".c") for p, _ in arts],
                       capture_output=True, text=True)
    if r.returncode: raise RuntimeError("cc: " + r.stderr[:2000])
    return exe


def run(exe, cases):
    inp = "".join("%s %d\n" % (s.hex(), p) for p, s in cases)
    out = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=600).stdout.splitlines()
    assert len(out) == len(cases), (len(out), len(cases))
    return [[tuple(int(x) for x in col.split()) for col in l.split("|")] for l in out]


def ok(res, exp, base, allow):
    if allow and res[0] == -3 and base[0] == -3: return True        # Q-R3: a give-up the deny arm also gives
    if exp[0] == "n": return res == (0,)
    if exp[0] == "utf": return res == (-9,)
    if exp[0] == "gu": return res[0] == {"frames": -3, "steps": -2, "work": -4}[exp[1]]
    if res[0] != 1: return False
    for g, sp in enumerate(exp[1]):
        got = (res[1 + 2 * g], res[2 + 2 * g])
        if sp is None and got != (-1, -1): return False
        if sp is not None and got != sp: return False
    return True


def starts(b, s):
    if b["enc"] != "utf8": return range(len(s) + 1)
    return [p for p in range(len(s) + 1) if p == 0 or p == len(s) or (s[p] & 0xC0) != 0x80]


def variants(b, c, d):
    """-> list of (name, kind, src|None, note).  kind: dfa / vm."""
    out = []; S = c["S"]; m = c["m"]
    base = open(c["path"]).read()
    def twin(name, fn, note=""):
        pfx = "t%d" % len(out)
        path, err = hat.compile_block(b, d, pfx)
        src = fn(open(path).read(), pfx)
        out.append((name, pfx, src, note))
    if m and S is not None and not c["nullable"] and len(S) < 256 and len(re.findall(hat.SKIP_RE % "rx", base)) == 1:
        E, Es, esc, s0 = m["E"], m["Estar"], m["esc"], m["s0"]
        adm = lambda T: bool(T) and T < E
        T0 = S & Es
        def dfa(name, T, admitted, reseed="cond", note=""):
            if not admitted: out.append((name, None, None, "declined")); return
            if name != "D0-ok" and reseed == "cond" and T == T0 and adm(T0):
                out.append((name, None, None, "identical table (T = D0's)")); return
            twin(name, lambda src, p: hat.dfa_twin(src, p, T, reseed), note)
        dfa("D0-ok", T0, adm(T0))
        T1 = S & E; dfa("D1-r3-SnE", T1, bool(T1) and T1 < E, note="T=%d" % len(T1))
        Td = m["Tdfa"]; dfa("DX-Tdfa", Td, bool(Td) and Td < E, note="T=Tdfa (rev 2 §4.1a: 'would also be sound'), |T|=%d" % len(Td))
        for k in m["seeds"]:
            if k == s0: continue
            Ek = set().union(*[esc[s] for s in m["seeds"] if s != k]); T = S & Ek
            if T == T0 and adm(T) == adm(T0): out.append(("D2-omit-seed", None, None, "identical table (E* without seed %d is still %d bytes)" % (k, len(Ek))))
            else: dfa("D2-omit-seed", T, adm(T), note="seed %d: |E*_k|=%d |T|=%d" % (k, len(Ek), len(T)))
        Ek = set().union(*[esc[s] for s in m["seeds"] if s != s0]) if len(m["seeds"]) > 1 else set(); T = S & Ek
        if T == T0 and adm(T) == adm(T0): out.append(("D3-omit-s0", None, None, "identical table (|E*_s0|=%d)" % len(Ek)))
        else: dfa("D3-omit-s0", T, adm(T), note="|E* w/o s0|=%d |T|=%d" % (len(Ek), len(T)))
        if adm(T0):
            dfa("D4-no-reseed", T0, True, "none")
            dfa("D5-uncond-reseed", T0, True, "uncond")
            if "-futf-check" in b["xflags"]:
                twin("D6-seek-before-utfcheck", lambda src, p: hat.dfa_pre_seek_before_validation(hat.dfa_twin(src, p, T0), p, T0))
            if c["handoff"] not in ("", "none"):
                twin("D7-seek-from-startpos", lambda src, p: hat.dfa_twin(src, p, T0).replace(
                    "size_t scan_position = handoff_position;", "size_t scan_position = search_from;"))
            if len(T0) == 1 and c.get("skip_bounded"):
                twin("D0m-ok-memchr-bounded", lambda src, p: hat.dfa_twin_memchr_bounded(src, p, T0))
                twin("D10-memchr-found-path-no-reseed", lambda src, p: hat.dfa_twin_memchr_bounded(src, p, T0, found=False))
                twin("D11-memchr-clamp-path-no-reseed", lambda src, p: hat.dfa_twin_memchr_bounded(src, p, T0, clamp=False))
            if len(T0) > 1:
                for x in sorted(T0)[:8]: dfa("D9-drop-member", T0 - {x}, True, note="drop 0x%02x" % x)
    if c["hat"] in ("vm", "vm-nullable"):
        if c["hat"] == "vm":
            twin("V0-ok", lambda src, p: hat.vm_twin(src, p, S, "ok"))
            twin("V1-late", lambda src, p: hat.vm_twin(src, p, S, "late"))
            starts_seen = {s[e[1][0][0]] for _, s, e in b["cases"] if e[0] == "m" and e[1][0][1] > e[1][0][0]}
            drop = sorted(S & starts_seen) + sorted(S - starts_seen)[:1]
            for x in drop[:10]:
                role = "begins a match in the cells" if x in starts_seen else "begins no match in the cells"
                twin("V2-drop-member", lambda src, p, x=x: hat.vm_twin(src, p, S - {x}, "ok"), "drop 0x%02x (%s)" % (x, role))
            twin("V4-retry-skip", lambda src, p: hat.vm_twin(src, p, S, "retry-skip"))
            if "-futf-check" in b["xflags"]:
                twin("V5-seek-before-utfcheck", lambda src, p: hat.vm_twin(src, p, S, "before-valid"))
        else:
            twin("V3-nullable-as-nonnullable", lambda src, p: hat.vm_twin(src, p, S, "ok"))
    return out


def sweep_cases(b):
    alpha = []
    for _, s, _ in b["cases"]:
        for x in s:
            if x not in alpha: alpha.append(x)
    alpha = alpha[:5]
    L = 6 if len(alpha) <= 4 else 5
    subs = [bytes(t) for n in range(L + 1) for t in itertools.product(alpha, repeat=n)]
    return [(p, s) for s in subs for p in starts(b, s)]


def one(job):
    i, b = job
    d = os.path.join(W, "m%d" % i); os.makedirs(d, exist_ok=True)
    c = hat.classify(b, d)
    row = {"id": b["id"], "pat": b["pat"], "edge": b["tags"].get("edge", ""), "status": c["status"], "cases": len(b["cases"])}
    if c["status"] != "ok": row["err"] = c.get("err"); return row, []
    row.update(hat=c["hat"], route="hybrid" if c["vmpf"] == "hybrid" else c["engine"], dfapf=c["dfapf"],
               S=len(c["S"]) if c["S"] is not None else -1, nullable=int(bool(c["nullable"])))
    if c["m"]: row.update(E=len(c["m"]["E"]), Estar=len(c["m"]["Estar"]), Tdfa=len(c["m"]["Tdfa"]), nseeds=len(c["m"]["seeds"]))
    vs = variants(b, c, d)
    built = [(n, p, s, note) for n, p, s, note in vs if s is not None]
    exe = build(d, [("rx", open(c["path"]).read())] + [(p, s) for _, p, s, _ in built])
    cases = [(p, s) for p, s, _ in b["cases"]]
    res = run(exe, cases)
    allow = "giveup_allowance" in b["tags"]
    base_bad = [(p, s) for (p, s, e), r in zip(b["cases"], res) if not ok(r[0], e, r[0], allow)]
    row["base_disagrees"] = len(base_bad)
    row["base_first"] = "" if not base_bad else "%d %r" % base_bad[0]
    sres = None
    if SWEEP and built:
        sc = sweep_cases(b); sres = (sc, run(exe, sc))
    out = []
    for n, p, s, note in vs:
        r = {"id": b["id"], "pat": b["pat"], "hat": c["hat"], "variant": n, "note": note}
        if s is None: r.update(status="declined" if note == "declined" else "identical"); out.append(r); continue
        k = 1 + [x[1] for x in built].index(p)
        det = [j for j, ((cp, cs, e), rr) in enumerate(zip(b["cases"], res)) if not ok(rr[k], e, rr[0], allow)]
        r["status"] = "built"; r["cells_detecting"] = len(det)
        if det:
            cp, cs, e = b["cases"][det[0]]
            r["first_cell"] = 'p=%d "%s" expect %s got %s' % (cp, cs.decode("latin-1").encode("unicode_escape").decode(), e, res[det[0]][k])
        if sres:
            sc, sr = sres
            diff = [(sp, ss) for (sp, ss), rr in zip(sc, sr) if rr[k] != rr[0] and not (allow and rr[0][0] == -3 and rr[k][0] >= 0)]
            r["sweep_cases"] = len(sc); r["sweep_diffs"] = len(diff)
            r["sweep_witness"] = "" if not diff else '%d "%s"' % (diff[0][0], diff[0][1].decode("latin-1").encode("unicode_escape").decode())
        out.append(r)
    return row, out


def main():
    outp = sys.argv[1]; filt = sys.argv[2:]
    blocks = [b for b in rxtcells.load(HERE) if b["cases"] and (not filt or any(f in b["id"] or f in b["pat"] for f in filt))]
    with cf.ThreadPoolExecutor(JOBS) as ex: res = list(ex.map(one, enumerate(blocks)))
    rows = [r for r, _ in res]; muts = [m for _, ms in res for m in ms]
    def dump(path, recs):
        keys = []
        for r in recs:
            for k in r:
                if k not in keys: keys.append(k)
        with open(path, "w") as f:
            f.write("\t".join(keys) + "\n")
            for r in recs: f.write("\t".join(str(r.get(k, "")) for k in keys) + "\n")
    dump(outp + ".blocks.tsv", rows); dump(outp + ".variants.tsv", muts)
    print("blocks %d (hat: %s), base disagreements %d" % (len(rows), {h: sum(r.get("hat") == h for r in rows) for h in ("dfa", "vm", "vm-nullable", "none")},
                                                       sum(r.get("base_disagrees", 0) for r in rows)))
    for r in rows:
        if r.get("base_disagrees"): print("  BASE DISAGREES", r["id"], r["pat"], r["base_first"])
        if r["status"] != "ok": print("  REFUSED", r["id"], r["pat"], r.get("err"))


if __name__ == "__main__": main()
