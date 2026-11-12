#!/usr/bin/env python3
"""population.py -- the census's captures-only class (docs/design/dfa_captures/
capture_forced.tsv, engine_nc == dfa: 815 rows) through the spike.

Per row: admission into the spike's subset (or the reason it is out), then
the differential over (a) the corpus's own subjects for that pattern (every
m/n/ms/ns/mc/mg/gu case line of every block with these bytes, startpos
ignored: the question is the unanchored search from 0) and (b) exhaustive
subjects over one representative byte per byte class of the pattern, length
chosen so the set stays <= ~2,000; then cost rows for the unanchored TDFA
(Stage 4 shape: start tag in the machine) and the ANCHORED TDFA (Stage 1
shape: run inside the hybrid window), each against its untagged DFA.

Usage: python3 population.py OUT.tsv [MISMATCH.txt]
Env: BENCH (pcrec-bench/bench, read-only), LIMIT (rows), NOVM=1 (skip pcrec VM)."""
import csv
import itertools
import signal
import os
import subprocess
import sys
import time

import oracle
import tdfa

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
TSV = os.path.join(ROOT, "docs", "design", "dfa_captures", "capture_forced.tsv")
TESTS = os.path.join(ROOT, "tests")
BENCH = os.environ.get("BENCH", "/home/pcrec/projects/pcrec-bench/bench")
PCREC = oracle.PCREC
MAXSUB = int(os.environ.get("MAXSUB", "2000"))

PATCOLS = ("kind line name value pattern flags features features_only encoding engine budget_steps "
           "budget_frames with from pcrec export tags oracle esc tune").split()
CASECOLS = ("line block_line block_name kind under startpos subject_form subject subject_id sha256 "
            "start end count giveup slot route").split()
CASEKINDS = {"m", "n", "ms", "ns", "mc", "mg", "gu"}


def dec(b):
    """The .rxt subject-escape vocabulary (\\t \\n \\r \\\\ \\xNN, \\" in quotes)."""
    out = bytearray()
    i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i + 1]
            m = {0x5c: 0x5c, 0x74: 9, 0x6e: 10, 0x72: 13, 0x22: 0x22}
            if n in m:
                out.append(m[n]); i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try:
                    out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError:
                    pass
        out.append(c); i += 1
    return bytes(out)


def list_source(path):
    r = subprocess.run([PCREC, "--list-source", path], capture_output=True, timeout=120)
    blocks = {}
    order = []
    section = None
    for l in r.stdout.split(b"\n"):
        if l.startswith(b"#section"):
            section = l.split(b" ", 1)[1].strip().decode()
            continue
        if l.startswith(b"#") or not l.strip():
            continue
        f = l.split(b"\t")
        if section is None:
            if len(f) < len(PATCOLS):
                continue
            d = dict(zip(PATCOLS, f))
            if d["kind"] not in (b"pattern", b"pattern-esc"):
                continue
            ln = d["line"].decode()
            blocks[ln] = [dec(d["pattern"]), d["flags"].decode(), d["encoding"].decode(), []]
            order.append(ln)
        elif section == "cases":
            d = dict(zip(CASECOLS, f))
            if d.get("kind", b"").decode() not in CASEKINDS or d.get("subject_form") != b"inline":
                continue
            s = d["subject"]
            if s.startswith(b'"') and s.endswith(b'"'):
                s = s[1:-1]
            b = blocks.get(d["block_line"].decode())
            if b is not None:
                b[3].append(dec(s))
    return [blocks[k] for k in order]


def corpus_index():
    idx = {}

    def add(pat, fl, enc, subs, src):
        e = idx.setdefault(pat, {"flags": fl, "enc": enc, "subs": [], "src": src})
        e["subs"].extend(subs)
    for root, _, files in os.walk(TESTS):
        for fn in sorted(files):
            if fn.endswith(".rxt"):
                for pat, fl, enc, subs in list_source(os.path.join(root, fn)):
                    add(pat, fl, enc, subs, "corpus")
    if os.path.isdir(BENCH):
        for sb in sorted(os.listdir(BENCH)):
            rxt = os.path.join(BENCH, sb, "patterns.rxt")
            if os.path.isfile(rxt):
                for pat, fl, enc, subs in list_source(rxt):
                    add(pat, fl, enc, subs, "bench:" + sb)
    return idx


def reps(dfa, utf8):
    out = []
    for cl in dfa.classes:
        pick = None
        for pref in (range(97, 123), range(48, 58), range(65, 91), range(32, 127), range(0, 128), range(128, 256)):
            for b in pref:
                if b in cl:
                    pick = b
                    break
            if pick is not None:
                break
        if utf8 and pick >= 0x80:
            continue
        out.append(pick)
    return out


def exhaustive(alpha):
    L = 0
    total = 1
    while L < 8:
        nxt = total + len(alpha) ** (L + 1)
        if nxt > MAXSUB:
            break
        total = nxt
        L += 1
    subs = []
    for n in range(L + 1):
        for t in itertools.product(alpha, repeat=n):
            subs.append(bytes(t))
    return subs, L


def costs(dfa, plain):
    st = dfa.stats()
    an = tdfa.analyze(dfa)
    return [st["states"], plain.stats()["states"], st["regs"], st["trans"], st["sets"], st["copies"],
            st["copy_trans"], st["tmp_trans"], st["maxops"], st["init_ops"],
            int(an["copyfree"]), an["conflicts"], int(an["copyfree_nf"]), an["conflicts_nf"],
            an["fixed"], an["classes"], int(an["allfixed"]), an["regs_after_fixed"]]


COSTCOLS = ["states", "ustates", "regs", "trans", "sets", "copies", "copy_trans", "tmp_trans", "maxops", "init_ops",
            "copyfree", "conflicts", "copyfree_nf", "conflicts_nf", "fixed", "classes", "allfixed", "regs_nf"]


class RowTimeout(Exception):
    pass


def _alarm(sig, frm):
    raise RowTimeout()


ROWSECS = int(os.environ.get("ROWSECS", "90"))
MAXNFA = int(os.environ.get("MAXNFA", "3000"))


def main():
    signal.signal(signal.SIGALRM, _alarm)
    out = open(sys.argv[1], "w")
    mm = open(sys.argv[2] if len(sys.argv) > 2 else os.devnull, "w")
    limit = int(os.environ.get("LIMIT", "0"))
    novm = os.environ.get("NOVM") == "1"
    rows = [r for r in csv.DictReader(open(TSV), delimiter="\t") if r["engine_nc"] == "dfa"]
    if limit:
        rows = rows[:limit]
    t0 = time.time()
    idx = corpus_index()
    print("# index built %.0fs, %d patterns; rows %d" % (time.time() - t0, len(idx), len(rows)), file=sys.stderr)
    hdr = (["n", "src", "enc", "flags", "ncaps", "prefilter", "status", "why", "nsubs", "corpus_subs", "exh_len",
            "pcre2_err", "mism_tdfa", "mism_pike", "mism_anch", "mism_vm", "fixed_viol"]
           + ["u_" + c for c in COSTCOLS] + ["a_" + c for c in COSTCOLS] + ["pattern_esc"])
    out.write("\t".join(hdr) + "\n")
    for n, r in enumerate(rows):
        pat = dec(r["pattern_esc"].encode("utf8"))
        e = idx.get(pat)
        flags = e["flags"] if e else ""
        utf8 = r["enc"] in ("utf8", "utf-8") or "u" in flags
        base = [str(n), r["src"], r["enc"], flags, r["ncaps"], r["prefilter"]]
        rec = {"status": "", "why": "", "nsubs": 0, "corpus_subs": 0, "exh_len": "", "pcre2_err": 0,
               "mism_tdfa": "", "mism_pike": "", "mism_anch": "", "mism_vm": "", "fixed_viol": ""}
        ucost = acost = [""] * len(COSTCOLS)
        signal.alarm(ROWSECS)
        try:
            nfa = tdfa.compile_pattern(pat, flags, utf8)
            if len(nfa.n) > MAXNFA:
                raise tdfa.Unsupported("NFA over the spike's %d-node cap (%d)" % (MAXNFA, len(nfa.n)))
            anfa = tdfa.compile_pattern(pat, flags, utf8, anchored=True)
            try:
                dfa = tdfa.TDFA(nfa)
                plain = tdfa.TDFA(nfa, tagged=False)
                adfa = tdfa.TDFA(anfa)
                aplain = tdfa.TDFA(anfa, tagged=False)
            except tdfa.TooBig:
                raise tdfa.Unsupported("TDFA over the spike's 4000-state cap")
            ucost = costs(dfa, plain)
            acost = costs(adfa, aplain)
            ref = oracle.Pcre2(pat, flags, utf8, nfa.ncap)
            aref = oracle.Pcre2(pat, flags, utf8, nfa.ncap, anchored=True)
            csubs = list(dict.fromkeys(e["subs"])) if e else []
            xsubs, L = exhaustive(reps(dfa, utf8))
            subs = list(dict.fromkeys(csubs + xsubs))
            rec.update(nsubs=len(subs), corpus_subs=len(csubs), exh_len=L)
            vm = None
            if not novm:
                vm, why = oracle.pcrec_vm(pat, flags, utf8, subs, tag="pop%d" % n)
                if vm is None:
                    rec["mism_vm"] = "n/a"
            bad = {"tdfa": 0, "pike": 0, "anch": 0, "vm": 0}
            for k, s in enumerate(subs):
                want = ref.search(s)
                if isinstance(want, tuple) and want[0] == "ERR":
                    rec["pcre2_err"] += 1
                    continue
                for kind, got in (("tdfa", dfa.run(s)), ("pike", tdfa.pike(nfa, s)),
                                  ("anch", adfa.run(s))):
                    w = want if kind != "anch" else aref.search(s)
                    if got != w:
                        bad[kind] += 1
                        if bad[kind] <= 3:
                            mm.write("%d\t%s\t%r\t%r\tpcre2=%s\tgot=%s\n" % (n, kind, pat, s, w, got))
                for kind, m in (("fixu", dfa), ("fixa", adfa)):
                    nv = tdfa.verify_fixed(m, s)
                    if nv:
                        bad[kind] = bad.get(kind, 0) + 1
                        if bad[kind] <= 3:
                            mm.write("%d\t%s\t%r\t%r\tfixed-offset claim violated %d\n" % (n, kind, pat, s, nv))
                if vm is not None and vm[k] != want:
                    bad["vm"] += 1
                    if bad["vm"] <= 3:
                        mm.write("%d\tvm\t%r\t%r\tpcre2=%s\tgot=%s\n" % (n, pat, s, want, vm[k]))
            rec.update(mism_tdfa=bad["tdfa"], mism_pike=bad["pike"], mism_anch=bad["anch"],
                       fixed_viol=bad.get("fixu", 0) + bad.get("fixa", 0))
            if vm is not None:
                rec["mism_vm"] = bad["vm"]
            rec["status"] = "in"
        except tdfa.Unsupported as ex:
            rec["status"], rec["why"] = "out", str(ex)
        except oracle.p2.Pcre2Error as ex:
            rec["status"], rec["why"] = "out", "pcre2 compile: " + str(ex)[:60]
        except RowTimeout:
            rec["status"], rec["why"] = "timeout", "row over %ds (spike's Python budget)" % ROWSECS
        signal.alarm(0)
        out.write("\t".join(base + [str(rec[k]) for k in hdr[6:17]] + [str(x) for x in ucost]
                            + [str(x) for x in acost] + [r["pattern_esc"]]) + "\n")
        out.flush()
        mm.flush()
        if n % 50 == 0:
            print("# row %d  %.0fs" % (n, time.time() - t0), file=sys.stderr)
    print("# done %.0fs" % (time.time() - t0), file=sys.stderr)


if __name__ == "__main__":
    main()
