#!/usr/bin/env python3
"""The checks critic's mutant harness (review r80, checks.md; mut.py/mut2.py/mut3.py in orig/), RE-AIMED at lane bsu6fix's
cards.py: every one of the 62 mutants is re-stated on the fixed code (same clause, the new text where the fix moved it), plus
new mutants on the fixes' own controls. Each mutant: a copy of cards.py with ONE edit; KILLED if `c6selftest` fails; else the
critic's DRY chain (prepare + `time --dry` on C6 c6_dig32, then the two deadline DRYs +63.5 / +65), KILLED if any exit code or
normalized output differs from the unmutated tip's. Usage: mutb.py SRC_CARDS_PY [IDS..] (sequential; run under boxlock)."""
import os, re, subprocess, sys

S = "/var/tmp/pcrec-pcrec/scratch/bsu6fix"
W = "/home/pcrec/projects/pcrec/worktrees/bsu6fix"
SRCF = sys.argv[1]
SRC = open(SRCF).read()
HERE = os.path.dirname(os.path.abspath(SRCF))
M = []


def m(i, clause, old, new):
    M.append((i, clause, old, new))


# ---- c6_read (the reader)
m("R1", "c6_read header refusal", '    if why:\n        raise SystemExit2("cards: c6decide: %s: REFUSED: %s" % (path, why))', '    if False:\n        raise SystemExit2("x")')
m("R2", "c6_read no #end refusal", 'if C6_END not in [x.split("\\t")[0] for x in ln if x]:', 'if False:')
m("R3", "c6_read unknown line refusal", '        elif not f[0].startswith("#"):\n            raise SystemExit2("cards: c6decide: %s: REFUSED: an unknown line', '        elif False:\n            raise SystemExit2("cards: c6decide: %s: REFUSED: an unknown line')
m("R4", "c6_read LAUNCHES refusal", 'if int(info["run"].get("launches", -1)) != LAUNCHES:', 'if False:')
m("R5", "c6_read missing first-pass row refusal", 'if any(r is None for r in first.values()):', 'if False:')
m("R6", "c6_read owed vs have mismatch", 'if bool(have) != owed or (have and len(have) != 3):', 'if (have and len(have) != 3):')
m("R7", "c6_read len(have)==3", 'if bool(have) != owed or (have and len(have) != 3):', 'if bool(have) != owed:')
m("R8", "c6_read stray rows refusal", '    if stray:', '    if False:')
m("R9", "c6_read first gatefail collect", '            info["gatefail"] += ["%s %s: %s" % ("/".join(ck), a, r["note"]) for a, r in first.items() if r["status"] == "gatefail"]', '            pass')
m("R10", "c6_read retime gatefail collect", '                info["gatefail"] += ["%s %s (re-time): %s" % ("/".join(ck), a, r["note"])\n                                     for a, r in again.items() if r["status"] == "gatefail"]', '                pass')
m("R11", "c6_read c.run from notrun", 'c["run"] = not any(r["status"] == "notrun" for r in first.values())', 'c["run"] = True')
m("R12", "c6_read retime_notrun detect", 'if any(r["status"] == "notrun" for r in have):\n                    info["retime_notrun"]', 'if False:\n                    info["retime_notrun"]')
m("R13", "c6_read owed requires c.run", 'owed = c["run"] and c6_owes(c["arms"])', 'owed = c6_owes(c["arms"])')
m("R14", "c6_read approx skip", '        if regime in APPROX:\n            info["approx"] += 1\n            continue', '        if False:\n            continue')
# ---- c6_owes (now over c6_pass, RULE-1)
m("O1", "c6_owes V vs H64 only", 'return any(x in ("WIN", "LOSS") for x in c6_pass(arms))', 'return c6_pass(arms)[0] in ("WIN", "LOSS")')
m("O2", "c6_owes A/A only", 'return any(x in ("WIN", "LOSS") for x in c6_pass(arms))', 'return c6_pass(arms)[1] in ("WIN", "LOSS")')
m("O3", "c6_owes LOSS only (WIN not owed)", 'return any(x in ("WIN", "LOSS") for x in c6_pass(arms))', 'return c6_pass(arms)[0] == "LOSS" or c6_pass(arms)[1] in ("WIN", "LOSS")')
m("O4", "c6_owes always False", 'return any(x in ("WIN", "LOSS") for x in c6_pass(arms))', 'return False')
# ---- arm_pool
m("P1", "arm_pool no redraw (return first draw)", '        if not any((pre, tuple(fl)) in first for _v, pre, fl in pool):\n            return pool', '        return pool')
m("P2", "arm_pool first set only unsalted", 'for a in ("V",) + tuple(POOL_SALT)', 'for a in ("V",)')
m("P3", "arm_pool retime ignored", '    if not retime:\n        return pool_variants(key, aligns, pool_salt(arm), pool_shift(arm))', '    if True:\n        return pool_variants(key, aligns, pool_salt(arm), pool_shift(arm))')
m("P4", "arm_pool redraw salt constant", '("|redraw%d" % t if t else "")', '("")')
# ---- void_reason
m("V1", "void cpu test", 'if busy7 > self.qc["cpu7_max"]:', 'if False:')
m("V2", "void nivcsw test", 'if nivcsw > lim:', 'if False:')
m("V3", "void nivcsw no scaling", 'lim = self.qc["nivcsw_max"] * max(1.0, secs / self.qc["t_cal"])', 'lim = self.qc["nivcsw_max"] * 1.0')
m("V4", "void cpu >= to inverted", 'if busy7 > self.qc["cpu7_max"]:', 'if busy7 < self.qc["cpu7_max"]:')
m("V5", "void nivcsw scaling floor removed", 'max(1.0, secs / self.qc["t_cal"])', '(secs / self.qc["t_cal"])')
m("V6", "void nivcsw >=", 'if nivcsw > lim:', 'if nivcsw >= lim:')
# ---- QuietControl.launch
m("L1", "launch no retime", 'for attempt in range(1 + QC_RETIMES):', 'for attempt in range(1):')
m("L2", "launch one extra retime", 'for attempt in range(1 + QC_RETIMES):', 'for attempt in range(2 + QC_RETIMES):')
m("L3", "launch voids not counted", '            self.voids += 1\n', '            pass\n')
m("L4", "launch returns void ns", '                self.pass_, "\\t".join(cell), attempt, busy7, niv, secs, why, ns))\n        return None', '                self.pass_, "\\t".join(cell), attempt, busy7, niv, secs, why, ns))\n        return ns')
# ---- dry_guard (the effective-environment form, CHECKS-5)
m("D1", "guard taskset test", '(isinstance(argv, (list, tuple)) and argv[:1] == ["taskset"]) or "CARD_TIME" in env', '"CARD_TIME" in env')
m("D2", "guard CARD_TIME test", '(isinstance(argv, (list, tuple)) and argv[:1] == ["taskset"]) or "CARD_TIME" in env', '(isinstance(argv, (list, tuple)) and argv[:1] == ["taskset"])')
m("D3", "guard timed_launch not swapped", 'globals()["timed_launch"], subprocess.run = no_clock, guarded', 'subprocess.run = guarded')
m("D4", "guard ClockCalled an Exception", 'class ClockCalled(BaseException):', 'class ClockCalled(Exception):')
# ---- time_cells
m("T1", "time_cells stop ignored", '            if stop is not None and stop():', '            if False:')
m("T2", "time_cells void on no launch", '                if c not in out and not launches[c]:\n                    out[c] =', '                if False:\n                    out[c] =')
m("T3", "time_cells launch None appended", '                        if x is not None:\n                            launches[c].append(x)', '                        if True:\n                            launches[c].append(x)')
m("T4", "time_cells launch param ignored", '    launch = launch or timed_launch\n', '    launch = timed_launch\n')
m("T5", "time_cells prefix dropped", 'f.write(prefix + (out[c] if c in out else', 'f.write((out[c] if c in out else')
m("T6", "time_cells notrun prefix dropped", 'f.write(prefix + row_line(c, "notrun"', 'f.write(row_line(c, "notrun"')
m("T7", "time_cells retime ignored in prepare", 'prepare_cell(rundir, c, SUBJECT_N, retime)', 'prepare_cell(rundir, c, SUBJECT_N, 0)')
# ---- the timer (_time / c6_prepare)
m("X1", "reach control refusal removed (call site)", '    if why:\n        raise SystemExit2("cards: time: " + why)', '    if False:\n        raise SystemExit2("cards: time: " + why)')
m("X2", "pool-proof refusal removed (call site)", '    if bad:\n        for w in bad:\n            print("FAIL", w)\n        raise SystemExit2("cards: time: a pool was refused', '    if False:\n        for w in bad:\n            print("FAIL", w)\n        raise SystemExit2("cards: time: a pool was refused')
m("X3", "proofs only first pass", '    texts = sorted({(c[1], c[2], c[4], rt) for c in timed for rt in (0, 1)})', '    texts = sorted({(c[1], c[2], c[4], rt) for c in timed for rt in (0,)})')
m("X4", "owed always all", 'and c6_owes(\n                {a: (r["launches"] or None) if r["status"] == "ok" else None for a, r in rs.items()}):', 'and True:')
m("X5", "owed never", 'and c6_owes(\n                {a: (r["launches"] or None) if r["status"] == "ok" else None for a, r in rs.items()}):', 'and False:')
m("X6", "owed needs all non-notrun", 'if all(r and r["status"] != "notrun" for r in rs.values()) and', 'if all(r for r in rs.values()) and')
m("X7", "retime launch not via the control", '               launch=launch, stop=stop, prefix="retime\\t", salt="retime", c6=True)', '               launch=None, stop=stop, prefix="retime\\t", salt="retime", c6=True)')
m("X8", "retime stop dropped", '               launch=launch, stop=stop, prefix="retime\\t", salt="retime", c6=True)', '               launch=launch, stop=None, prefix="retime\\t", salt="retime", c6=True)')
m("X9", "retime same pool", 'with_approx=False, retime=1,', 'with_approx=False, retime=0,')
m("X10", "pass_ retime label", '    q.pass_ = "retime"\n', '    q.pass_ = "first"\n')
m("X11", "#end status truncated", '"truncated" if nr["first"] or nr["retime"] else "complete"', '"complete"')
m("X12", "reach control scope narrowed", 'k[2] == "hit-dense" and calls[k] == 0', 'k[2] == "hit-dense" and calls[k] == -1')
m("X13", "rc not returned", '    print("cards: time: DONE rc=%d" % rc)\n    return rc', '    print("cards: time: DONE rc=%d" % rc)\n    return 0')
m("X14", "rule_710 sha check", '    if rule_sha(C6_RULE_710_FILE) != C6_RULE_710_RECORDED:\n        raise SystemExit2("cards: time:', '    if False:\n        raise SystemExit2("cards: time:')
# ---- cmd_c6decide exit codes
m("E1", "c6decide gatefail exit 1", '    if info["gatefail"]:\n        return 1', '    if info["gatefail"]:\n        return 0')
m("E2", "c6decide truncated exit 4", 'return 4 if any(d["notrun"] for d in dec.values()) or info["retime_notrun"] else 0', 'return 0')
m("E3", "c6decide retime_notrun not 4", 'return 4 if any(d["notrun"] for d in dec.values()) or info["retime_notrun"] else 0', 'return 4 if any(d["notrun"] for d in dec.values()) else 0')
# ---- NEW: the fixes' own controls (bsu6fix)
m("N1", "RULE-1 reverted: a short arm NOISEs only its own comparison", '    if any(x is None for x in a.values()):\n        return "NOISE", "NOISE"\n', '')
m("N2", "RULE-4 reverted: a re-time NOT-RUN is not prefixed", 'if cause["NOT-RUN"] or any(c.get("retime_notrun") for c in cs):', 'if cause["NOT-RUN"]:')
m("N3", "A/A WIN on a noisy re-time falls to TIE again", '        if first == "LOSS" or aa:', '        if first == "LOSS":')
m("N4", "RULE-2: the single-pass list dropped", '            "%s %s" % ("/".join(key[1:3]), n) for key, n in d["notes"] if SINGLE in n) or "none"))', '            "%s %s" % ("/".join(key[1:3]), n) for key, n in d["notes"] if False) or "none"))')
m("N5", "FIDELITY-1: H64.b's own shift dropped", '    own = arm in POOL_SALT and "pool-overlap" not in PLANT', '    own = False')
m("N6", "FIDELITY-1: the re-time shift dropped", '2 * (int(own) + int(bool(retime))) % 4', '2 * int(own) % 4')
m("N7", "FIDELITY-1: the built disjointness check dropped", '        why = pool_disjoint_refusal(lay)\n', '        why = None\n')
m("N8", "FIDELITY-2: the wiring control dropped", '        if pool_of.get(argv[3]) != want:', '        if False:')
m("N9", "FIDELITY-2: the reader's re-time/first exe intersection dropped", '    if used.get(0, set()) & used.get(1, set()):', '    if False:')
m("N10", "FIDELITY-2: the reader's pool membership dropped", '                            any(x not in pool for x in r["exes"]):', '                            False:')
m("N11", "FIDELITY-2: DryProbe keyed on the cell label again", '        f = self.model.get(cell[3], {}).get((pass_, arm), 1.0)', '        f = self.model.get(cell[3], {}).get((({"first": "first", "retime": "retime"}.get(q.pass_, "cal") if q else "cal"), cell[2]), 1.0)')
m("N12", "FIDELITY-4: a timed-launch GateFail read as void again", '                        out[c] = row_line(c, "gatefail" if c6 else "void", note=str(e))', '                        out[c] = row_line(c, "void", note=str(e))')
m("N13", "FIDELITY-5: time compiles again", '    if not COMPILE_OK:\n        raise SystemExit2("cards: time refuses to compile', '    if False:\n        raise SystemExit2("cards: time refuses to compile')
m("N14", "CHECKS-5: untimed execs inherit CARD_TIME again", '    return {k: v for k, v in os.environ.items() if k != "CARD_TIME"}', '    return dict(os.environ)')
m("N15", "CHECKS-5: the guard reads only an explicit env again", '        env = os.environ if env is None else env', '        env = {} if env is None else env')
m("N16", "RULE-3: a timing without its window runs", '        raise SystemExit2("cards: time: a timing needs its WINDOW', '        return None, "none"\n        raise SystemExit2("cards: time: a timing needs its WINDOW')
m("N17", "RULE-3: --deadline +S anchored at nothing (+0)", '        return (t_start + float(dl[1:]) if dl.startswith("+") else float(dl)), "--deadline %s" % dl', '        return (t_start + 0 if dl.startswith("+") else float(dl)), "--deadline %s" % dl')
m("N18", "CHECKS-9: the redraw bound dropped (refusal never raised)", '    raise SystemExit2("cards: the re-time pool of %s %s %s repeats a first-pass exe after %d redraws: REFUSED" % (', '    return pool\n    raise SystemExit2("cards: the re-time pool of %s %s %s repeats a first-pass exe after %d redraws: REFUSED" % (')
m("N19", "CHECKS-10: the #end cross-check dropped", '    if info.get("end", {}).get("status") != want:', '    if False:')
m("N20", "FIDELITY-3: the harness field dropped from the header keys", 'C6_HEADER_KEYS = ("rule", "rule710", "harness", "form", "binary", "widths", "run")', 'C6_HEADER_KEYS = ("rule", "rule710", "form", "binary", "widths", "run")')

ONLY = sys.argv[2:]


def norm(s):
    s = re.sub(r"\d+ void launches", "N void launches", s)
    s = re.sub(r"DRY: \d+ synthetic", "DRY: N synthetic", s)
    s = re.sub(r"[0-9a-f]{16}", "H", s)
    s = re.sub(r"/var/tmp\S+", "P", s)
    s = re.sub(r"deadline \d+ \(", "deadline D (", s)
    return s


def env_of(cards):
    return dict(os.environ, TMPDIR=S + "/tmp", PCREC_TMPDIR=S, PCREC_TREE=W, JOBS="4", CARDS=cards)


def cards_run(cards, args, timeout=1500):
    p = subprocess.run(["nice", "gnutimeout", str(timeout), "python3", "-I", cards] + args, env=env_of(cards),
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def rundir(tag):
    d = os.path.join(S, "mutants", "rd_" + tag)
    os.makedirs(d, exist_ok=True)
    for x in ("art", "bin", "reach", "subj", "fx"):
        if not os.path.lexists(os.path.join(d, x)):
            os.symlink(os.path.join(S, "rd", x), os.path.join(d, x))
    return d


def dry_chain(cards, tag):
    """The critic's DRY chain re-aimed: prepare C6 c6_dig32, then `time --dry`, `--deadline +63.5`, `--deadline +65`."""
    d = rundir(tag)
    out = []
    rc, o = cards_run(cards, ["time", d, "--prepare", "--cards", "C6", "--patterns", "c6_dig32"])
    out.append((rc, o))
    for extra in ([], ["--deadline", "+63.5"], ["--deadline", "+65"]):
        out.append(cards_run(cards, ["time", d, "--dry"] + extra))
    return out


def main():
    base_cards = os.path.join(S, "mutants", "base", "cards.py")
    os.makedirs(os.path.dirname(base_cards), exist_ok=True)
    for f in ("c6_rule.md", "rule_710.md"):
        open(os.path.join(os.path.dirname(base_cards), f), "w").write(open(os.path.join(HERE, f)).read())
    open(base_cards, "w").write(SRC)
    rc, o = cards_run(base_cards, ["c6selftest", os.path.join(S, "rd")])
    print("BASE c6selftest rc %d (%s)" % (rc, (re.findall(r"c6selftest: \d+ rows, \d+ failed", o) or ["?"])[-1]), flush=True)
    if rc:
        print(o[-3000:])
        return 1
    base = dry_chain(base_cards, "base")
    print("BASE dry chain rcs %s" % [r for r, _o in base], flush=True)
    res = {}
    for i, cl, old, new in M:
        if ONLY and i not in ONLY:
            continue
        if SRC.count(old) != 1:
            print(i, cl, "-> PATTERN MATCHES %d (not applied)" % SRC.count(old), flush=True)
            res[i] = "NOT-APPLIED"
            continue
        d = os.path.join(S, "mutants", "m_" + i)
        os.makedirs(d, exist_ok=True)
        for f in ("c6_rule.md", "rule_710.md"):
            open(os.path.join(d, f), "w").write(open(os.path.join(HERE, f)).read())
        mc = os.path.join(d, "cards.py")
        open(mc, "w").write(SRC.replace(old, new))
        rc, o = cards_run(mc, ["c6selftest", os.path.join(S, "rd")])
        open(os.path.join(d, "selftest.out"), "w").write(o)
        if rc != 0:
            fails = [x for x in o.splitlines() if x.startswith("FAIL")]
            k = "KILLED(selftest rc=%d: %s)" % (rc, fails[0][:110] if fails else o.strip().splitlines()[-1][:110])
        else:
            chain = dry_chain(mc, i)
            diff = [n for n, ((brc, bo), (mrc, mo)) in enumerate(zip(base, chain)) if brc != mrc or norm(bo) != norm(mo)]
            k = "KILLED(dry chain step %s)" % diff if diff else "SURVIVED"
        res[i] = k
        print(i, cl, "->", k, flush=True)
    print("TOTALS: %d mutants, %d KILLED, %d SURVIVED, %d NOT-APPLIED" % (
        len(res), sum(v.startswith("KILLED") for v in res.values()), sum(v == "SURVIVED" for v in res.values()),
        sum(v == "NOT-APPLIED" for v in res.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
