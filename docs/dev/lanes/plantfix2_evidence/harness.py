#!/usr/bin/env python3
"""EVIDENCE, NOT A CHECK (lane plantfix2, 2026-11-24): review r94's acceptance gate.

Adapted from the r94 check-adequacy critic's harness
($PCREC_TMPDIR/scratch/crit-memfn-plantcheck/checkadequacy/h/harness.py, 35 mutants
Q1-Q20 on the applier, P1-P15 on the pass). The critic's FAULTS F1-F14 now live in the
pass's own `--selftest` (scripts/m6read_check_sab_anchors.py's CASES), so this file keeps
only the MUTANTS, each re-spelled onto the fixed code's site for the same clause (where
CA-6 merged check and apply into one loop, several originals land on ONE site: said per
row), plus N* mutants on the clauses the fix added.

A mutant is KILLED iff, applied to a copy of the tree, the LIVE run
(`python3 -I scripts/m6read_check_sab_anchors.py`, both halves, what [SABANCHOR] runs) or
the SELF-TEST (`... --selftest`) exits non-zero. EQUIVALENT rows are argued in the
lane report, not here.

Usage: python3 -I harness.py TREE OUT [ID,ID..]   (TREE: the lane worktree; OUT: scratch)
Prints one row per mutant, then the tally. The unmutated control must be green first.
"""
import os, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

P, S = "tests/lib/plants.py", "scripts/m6read_check_sab_anchors.py"

# id: (file, old text (exactly once), new text, what it breaks)
MUTANTS = {
    # --- the applier (the critic's Q1-Q20) ---
    "Q1": (P, ".replace('\\\\n', '\\n').replace('\\\\&', '&')\n\n\ndef un_pres", ".replace('\\\\n', '\\n')\n\n\ndef un_pres", "un_win drops the \\& rule"),
    "Q2": (P, "return s.replace('\\\\n', '\\n').replace('\\\\&', '&')\n\n\ndef un_pres", "return s.replace('\\\\&', '&')\n\n\ndef un_pres", "un_win drops the \\n rule"),
    "Q3": (P, "s.replace('\\\\\\\\n', '\\x00').replace('\\\\n', '\\n').replace('\\x00', '\\\\n')", "s.replace('\\\\n', '\\n')", "un_pres drops the \\\\\\\\n protection"),
    "Q4": (P, ".replace('\\x00', '\\\\n').replace('\\\\&', '&')", ".replace('\\x00', '\\\\n')", "un_pres drops the \\& rule"),
    "Q5": (P, "        if len(parts) != 3:\n            raise Undecodable('%d fields, not 3 (FILE@@FROM@@TO)' % len(parts))\n        f, a, b = parts\n", "        f, a, b = parts[0], parts[1], '@@'.join(parts[2:])\n", "wreply's exactly-3-fields rule dropped"),
    "Q6": (P, "    j = rest.find('@@')", "    j = rest.rfind('@@')", "shell_split takes the LAST @@"),
    "Q7": (P, "        if c != 1:\n            yield k, p, 'STALE'", "        if c == 0:\n            yield k, p, 'STALE'", "OK if count >= 1 (one loop: also Q14 apply refuses only on 0, Q20 ambiguous not bad)"),
    "Q8": (P, "            nbad += st != 'OK'", "            nbad += st not in ('OK', 'STALE')", "STALE not counted bad"),
    "Q9": (P, "        store.write(p, s.replace(a, b))\n", "        pass\n", "the loop never writes (check not cumulative; apply never writes)"),
    "Q9b": (P, "    def write(self, p, s):\n        self.mem[os.path.realpath(p)] = s\n", "    def write(self, p, s):\n        pass\n", "check's store not cumulative"),
    "Q10": (P, "            print('%s\\t0/0\\tNO SPEC\\t0\\t%s' % (pid, rel(runner)))\n            nbad += 1\n", "            print('%s\\t0/0\\tNO SPEC\\t0\\t%s' % (pid, rel(runner)))\n", "NO SPEC not counted bad"),
    "Q11": (P, "    for lab in case_labels(open(opt['labels']).read()):\n", "    for lab in []:\n", "the ORPHAN/BAD LABEL loop removed"),
    "Q12": (P, "            nbad += st != 'OK'", "            nbad += st not in ('OK', 'MISSING FILE')", "MISSING FILE not counted bad"),
    "Q13": (P, "    print('plant-check: %d plants, %d edits, %d bad' % (len(plants), nedit, nbad))\n    return 1 if nbad else 0\n", "    print('plant-check: %d plants, %d edits, %d bad' % (len(plants), nedit, nbad))\n    return 0\n", "check always exits 0"),
    "Q14": (P, "        if st != 'OK':\n            sys.exit(why)", "        if st == 'STALE':\n            sys.exit(why)", "apply-side: exits 0 on an AMBIGUOUS (or missing) edit, unapplied"),
    "Q15": (P, "    def write(self, p, s):\n        open(p, 'w').write(s)\n", "    def write(self, p, s):\n        pass\n", "apply never writes the file"),
    "Q16": (P, "def cmd_apply(dialect, base, c0, edits):\n", "def cmd_apply(dialect, base, c0, edits):\n    return 0\n", "apply returns at once"),
    "Q17": (P, "(c0 + '/' + f[len('@c0/'):]) if f.startswith('@c0/') else base + '/' + f", "base + '/' + f", "pres @c0/ resolved under BASE"),
    "Q18": (P, "    return [x[1:-1] if len(x) > 1", "    return [] and [x[1:-1] if len(x) > 1", "case labels never read"),
    "Q19": (P, "            nbad += st != 'OK'", "            nbad += st not in ('OK', 'UNDECODABLE')", "UNDECODABLE not counted bad"),
    "Q20": (P, "            nbad += st != 'OK'", "            nbad += st not in ('OK', 'AMBIGUOUS')", "AMBIGUOUS not counted bad"),
    # --- the pass (the critic's P1-P15) ---
    "P1": (S, "    p_fail = bool(p_unreadable or p_bad or pins)", "    p_fail = bool(p_unreadable or p_bad)", "the population (pins) ignored: the floor-0 analogue"),
    "P1b": (S, "        elif counts[rel] != PLANT_PINS[rel]:", "        elif False:", "a runner off its pin not red"),
    "P1c": (S, "        elif rel not in counts:\n", "        elif False:\n", "a pinned runner not read is not red"),
    "P1d": (S, "        if rel not in PLANT_PINS:\n            pins.append", "        if False:\n            pins.append", "an unpinned runner not red"),
    "P2": (S, "        if f.endswith(\".md\") or f in (me, APPLIER):", "        if f.endswith(\".md\") or f in (me, APPLIER) or f.startswith(\"memfn/\"):", "discovery drops memfn/"),
    "P3": (S, "            p_unreadable.append((rel, \"DEFINES plant_spec BUT HAS NO --plant-check MODE\"))\n", "", "a no-mode runner skipped silently"),
    "P4": (S, "            if err.strip() or rc not in (0, 1) or len(summ) != 1", "            if rc not in (0, 1) or len(summ) != 1", "check's stderr ignored"),
    "P4b": (S, "                if err.strip() or rc != 0 or any(len(r) != 6 for r in rows):", "                if rc != 0 or any(len(r) != 6 for r in rows):", "dump's stderr ignored"),
    "P5": (S, "            if err.strip() or rc not in (0, 1) or len(summ) != 1", "            if err.strip() or len(summ) != 1", "check's returncode ignored"),
    "P6": (S, " or len(summ) != 1 \\\n", " or not summ \\\n", "summary-count rule dropped"),
    "P7": (S, "                    or any(len(r) != 5 for r in rows):", "                    or False:", "row-width rule dropped"),
    "P8": (S, "            if len(ids) != P or len(bad) != Bn or (rc == 0) != (Bn == 0):", "            if False:", "the INCONSISTENT rule dropped"),
    "P9": (S, "            bad = [r for r in rows if r[2] != \"OK\"]", "            bad = [r for r in rows if r[2] == \"STALE\"]", "only STALE is bad"),
    "P10": (S, "    p_fail = bool(p_unreadable or p_bad or pins)", "    p_fail = bool(p_unreadable or pins)", "p_fail ignores bad plants"),
    "P11": (S, "    p_fail = bool(p_unreadable or p_bad or pins)", "    p_fail = bool(p_bad or pins)", "p_fail ignores unreadable runners"),
    "P12": (S, "    sys.exit(1 if (mech_fail or p_fail) else 0)", "    sys.exit(1 if mech_fail else 0)", "the exit ignores the plant half"),
    "P13": (S, "            if rc is None:\n                p_unreadable.append((rel, out + (\"\" if mode == \"check\" else \" (dump)\")))\n", "            if rc is None:\n", "a timeout not recorded"),
    "P14": (S, "                p_unreadable.append((rel, \"--plant-check SUMMARY UNREADABLE: \" + summ[0][:60]))\n", "", "a summary-parse failure not recorded"),
    "P15": (S, "        nplants += P\n", "        nplants += len(ids)\n", "nplants from the rows, not the summary"),
    # --- clauses the fix added ---
    "N1": (P, "        k = os.path.realpath(p)\n", "        k = p\n", "check's store keyed by the raw path (CA-1 alias)"),
    "N2": (P, "                return k not in sets or os.path.relpath(p, r) in sets[k]", "                return True", "check ignores the copy's file set (CA-1)"),
    "N3": (P, "    sets = {k: read_set(v) for k, v in opt.get('files', {}).items()}", "    sets = {}", "--files never read"),
    "N4": (P, "            out += [x.strip() for x in ln.strip()[:-1].split(' | ')]", "            out += [ln.strip()[:-1]]", "alternation labels not split (CA-2)"),
    "N5": (P, "    return [x[1:-1] if len(x) > 1 and x[0] == x[-1] and x[0] in '\\'\"' else x for x in out]", "    return out", "quoted labels not unquoted (CA-2)"),
    "N6": (P, "        if not re.fullmatch(r'S[0-9]+', lab):\n            print", "        if False:\n            print", "BAD LABEL never reported"),
    "N7": (P, "        tw = 'twin' if pid in twins else '-'", "        tw = '-'", "dump never declares a twin"),
    "N8": (S, "DEFINES = re.compile(rb\"^[ \\t]*(function[ \\t]+plant_spec\\b|plant_spec[ \\t]*\\([ \\t]*\\))\", re.M)", "DEFINES = re.compile(rb\"^plant_spec\\(\\) \\{\", re.M)", "definers by one spelling again (CA-3)"),
    "N9": (S, "        if f not in callers or f in definers:", "        if False:", "a vacuous NOT_RUNNERS entry not red"),
    "N10": (S, "        if f not in NOT_RUNNERS:\n            bad.append", "        if False:\n            bad.append", "a caller that defines no plant_spec not red"),
    "N11": (S, "        bad.append((f, \"DEFINES plant_spec BUT NEVER NAMES %s\" % APPLIER))\n", "        pass\n", "a definer that never names the applier not red"),
    "N12": (S, "                os.killpg(pr.pid, signal.SIGKILL)\n", "                pass\n", "the timed-out runner's group never killed (PAR-3)"),
    "N13": (S, "text=True, env=env, start_new_session=True)", "text=True, env=env, start_new_session=False)", "the runner not in its own session (PAR-3)"),
    "N14": (S, "                pr.communicate(timeout=5)\n", "                pr.communicate()\n", "the second communicate unbounded (PAR-3)"),
    "N15": (S, "            out, err = pr.communicate(timeout=max(0.0, deadline - time.monotonic()))", "            out, err = pr.communicate(timeout=budget)", "a per-runner timeout, not the shared deadline (PAR-2)"),
    "N16": (S, "    return \" \".join(text.split())", "    return text", "twin normal form: raw text"),
    "N17": (S, "            elif norm(a, sf) != norm(sb, sf):", "            elif False:", "twin FROM not compared"),
    "N18": (S, "            elif norm(b, sf) != norm(sa, sf):", "            elif False:", "twin TO not compared"),
    "N19": (S, "        if pid not in twins:\n            p_bad.append", "        if False:\n            p_bad.append", "an undeclared shared id (collision) not red"),
    "N20": (S, "            if pid in twins:\n                p_bad.append", "            if False:\n                p_bad.append", "a declared twin with no row not red"),
    "N21": (S, "    for pid in notlisted:\n        p_bad.append", "    for pid in []:\n        p_bad.append", "a declared twin not in PLANTS not red"),
    "N22": (S, "            if pid in seen:\n                p_bad.append", "            if False:\n                p_bad.append", "one id in two runners not red"),
    "N23": (S, "        if dump_ids != check_ids:", "        if False:", "check and dump naming different plants not red"),
    "N24": (S, "            if os.path.normpath(r[3]) != os.path.normpath(sf):", "            if False:", "twin file not compared"),
    "N25": (S, "        if len(sites) != len(rows):", "        if False:", "twin edit count not compared"),
}


def run(argv, env, tmo):
    try:
        r = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=tmo)
        return r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return 124, "HARNESS: timed out after %d s" % tmo


def main():
    tree, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    ref = os.path.join(out, "ref")
    if not os.path.isdir(ref):
        ls = subprocess.run(["git", "-C", tree, "ls-files", "-z"], capture_output=True, check=True).stdout
        for f in (x.decode() for x in ls.split(b"\0") if x):
            if os.path.isfile(os.path.join(tree, f)):
                os.makedirs(os.path.dirname(os.path.join(ref, f)), exist_ok=True)
                shutil.copy2(os.path.join(tree, f), os.path.join(ref, f))
        for argv in (["git", "init", "-q"], ["git", "add", "-A"]):
            subprocess.run(argv, cwd=ref, capture_output=True, check=True)

    def one(mid):
        w = os.path.join(out, "w_" + mid)
        shutil.rmtree(w, ignore_errors=True)
        subprocess.run(["cp", "-cR" if sys.platform == "darwin" else "-R", ref, w], check=True)
        tmp = os.path.join(w, ".tmp")
        os.makedirs(tmp)
        env = dict(os.environ, TMPDIR=tmp)
        if mid != "CONTROL":
            rel, a, b, _ = MUTANTS[mid]
            s = open(os.path.join(w, rel)).read()
            if s.count(a) != 1:
                shutil.rmtree(w, ignore_errors=True)
                return mid, "HARNESS-ERROR (site occurs %d times)" % s.count(a), "", ""
            os.remove(os.path.join(w, rel))       # never write through a clone's shared block
            open(os.path.join(w, rel), "w").write(s.replace(a, b))
        t0 = time.monotonic()
        lrc, lout = run(["python3", "-I", os.path.join(w, S)], env, 300)
        src, sout = run(["python3", "-I", os.path.join(w, S), "--selftest"], env, 900)
        fails = [l.split("  ")[0].replace("selftest ", "").strip()
                 for l in sout.splitlines() if l.startswith("selftest ") and " FAIL" in l]
        shutil.rmtree(w, ignore_errors=True)
        verdict = "KILLED" if (lrc != 0 or src != 0) else "SURVIVED"
        if mid == "CONTROL":
            verdict = "GREEN" if verdict == "SURVIVED" else "RED"
        why = []
        if lrc != 0:
            why.append("live rc %d: %s" % (lrc, " | ".join(l.strip() for l in lout.splitlines()
                                                         if l.strip() and not l.startswith("sabotages"))[:150]))
        if src != 0:
            why.append("selftest rc %d, %d failed: %s" % (src, len(fails), "; ".join(f[:50] for f in fails[:3])))
        return mid, verdict, "%.0f s" % (time.monotonic() - t0), " || ".join(why)

    rows = [one("CONTROL")]
    print("%-8s %-9s %-6s %s" % rows[0], flush=True)
    if rows[0][1] != "GREEN":
        sys.exit("HARNESS: the unmutated control is not green; nothing below would mean anything")
    ids = [m for m in MUTANTS if only is None or m in only]
    with ThreadPoolExecutor(max_workers=2) as ex:
        for r in ex.map(one, ids):
            print("%-8s %-9s %-6s %s  [%s]" % (r + (MUTANTS[r[0]][3],)), flush=True)
            rows.append(r)
    k = sum(r[1] == "KILLED" for r in rows)
    s = [r[0] for r in rows if r[1] == "SURVIVED"]
    e = [r[0] for r in rows if r[1].startswith("HARNESS")]
    print("mutants: %d, killed %d, survived %d %s, harness errors %d %s" % (len(ids), k, len(s), s, len(e), e))


if __name__ == "__main__":
    main()
