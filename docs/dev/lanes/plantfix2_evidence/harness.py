#!/usr/bin/env python3
"""Critic harness (not the subject): faults F* planted into copy M, mutants applied to M's
plants.py / anchor script; each case restores M's touched files from REF afterwards."""
import os, shutil, subprocess, sys
L = '/var/tmp/pcrec-claude/scratch/crit-memfn-plantcheck/checkadequacy'
REF, M = L + '/ref', L + '/m'
ENV = dict(os.environ, TMPDIR=L + '/tmp')
touched, created, removed = set(), set(), set()

def rd(rel): return open(os.path.join(M, rel)).read()
def wr(rel, s):
    touched.add(rel); open(os.path.join(M, rel), 'w').write(s)
def sub(rel, a, b, n=1):
    s = rd(rel); c = s.count(a)
    if c < 1: raise SystemExit('HARNESS: %r not in %s' % (a[:60], rel))
    wr(rel, s.replace(a, b, n))
def new(rel, s):
    p = os.path.join(M, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    created.add(rel); open(p, 'w').write(s)
def mv(rel, rel2):
    removed.add(rel); created.add(rel2)
    os.makedirs(os.path.dirname(os.path.join(M, rel2)), exist_ok=True)
    shutil.move(os.path.join(M, rel), os.path.join(M, rel2))
def rm(rel):
    removed.add(rel); os.remove(os.path.join(M, rel))
def restore():
    for rel in created:
        p = os.path.join(M, rel)
        if os.path.exists(p): os.remove(p)
    for rel in touched | removed:
        shutil.copy2(os.path.join(REF, rel), os.path.join(M, rel))
    touched.clear(); created.clear(); removed.clear()

def fast():
    subprocess.run(['bash', L + '/h/mkfast.sh', M], check=True)
    r = subprocess.run(['python3', '-I', M + '/scripts/fastpass.py'], capture_output=True, text=True, env=ENV)
    tail = [l for l in r.stdout.splitlines() if l.strip()][-3:]
    return r.returncode, ' | '.join(t.strip()[:110] for t in tail)

WIN, PRES, PROOF, WREPLY = 'memfn/tests/run_g2_win.sh', 'memfn/tests/run_g2_pres.sh', 'tests/memfn/run_proof.sh', 'tests/memfn/run_wreply.sh'
NOMODE = 'plant_spec() {\n    case "$1" in\n    S9001) echo \'x.c@@a@@b\' ;;\n    *) return 1 ;;\n    esac\n}\nPLANTS="S9001"\n'

FAULTS = {
 'F1 stale FROM (win S1425)':      lambda: sub(WIN, "S1425) # code review r1 C13", "S1425) # code review r1 C13") or sub(WIN, "echo 'window.c@@", "echo 'window.c@@XYZZY", 1),
 'F2 ambiguous FROM (wreply S1414 FROM duplicated in src)': lambda: wr('src/gen/emit_dfa.c', rd('src/gen/emit_dfa.c') + '\n/*    [NK_RUN_PINNED] = { "run-pinned[-bounded]", WR_ANY, 1, 1, */\n'),
 'F3 missing file (proof S1221 file renamed in spec)': lambda: sub(PROOF, "S1221) # a form claiming", "S1221) # a form claiming") or sub(PROOF, "echo '", "echo 'X", 1),
 'F4 PLANTS id with no case (proof S9999)': lambda: sub(PROOF, 'PLANTS="S1221', 'PLANTS="S9999 S1221'),
 'F5 case not in PLANTS (proof S9998)': lambda: sub(PROOF, "    *) return 1 ;;", "    S9998) echo 'compose.c@@x@@y' ;;\n    *) return 1 ;;"),
 'F6 two-id case line S9997|S9996) not in PLANTS': lambda: sub(PROOF, "    *) return 1 ;;", "    S9997|S9996) echo 'compose.c@@x@@y' ;;\n    *) return 1 ;;"),
 'F6b listed case widened S1225|S9995)': lambda: sub(PROOF, "    S1225) #", "    S1225|S9995) #"),
 'F6c case with space before paren S9994 )': lambda: sub(PROOF, "    *) return 1 ;;", "    S9994 ) echo 'compose.c@@x@@y' ;;\n    *) return 1 ;;"),
 'F6d quoted case "S9993")': lambda: sub(PROOF, "    *) return 1 ;;", "    \"S9993\") echo 'compose.c@@x@@y' ;;\n    *) return 1 ;;"),
 'F7 dropped runner (wreply deleted)': lambda: rm(WREPLY),
 'F7b renamed runner (wreply -> .bash)': lambda: mv(WREPLY, 'tests/memfn/run_wreply.bash'),
 'F7c runner moved outside discovery (wreply -> scripts/)': lambda: mv(WREPLY, 'scripts/run_wreply.sh'),
 'F7d plant_spec respelled `plant_spec () {` (wreply)': lambda: sub(WREPLY, 'plant_spec() {', 'plant_spec () {'),
 'F7e PLANTS emptied (wreply)': lambda: sub(WREPLY, 'PLANTS="S1413 S1414"', 'PLANTS=""'),
 'F8 fifth runner, plant_spec, no --plant-check (tests/)': lambda: new('tests/zz/run_zz.sh', '#!/bin/bash\n' + NOMODE),
 'F8b fifth runner, `function plant_spec {` (tests/)': lambda: new('tests/zz/run_zz.sh', '#!/bin/bash\n' + NOMODE.replace('plant_spec() {', 'function plant_spec {')),
 'F8c fifth runner under scripts/': lambda: new('scripts/run_zz.sh', '#!/bin/bash\n' + NOMODE),
 'F8d fifth runner under examples/': lambda: new('examples/zz/run_zz.sh', '#!/bin/bash\n' + NOMODE),
 'F8e fifth runner, mode named in a comment only': lambda: new('tests/zz/run_zz.sh', '#!/bin/bash\n# "--plant-check" TODO\n' + NOMODE),
 'F9 --plant-check prints garbage (proof)': lambda: sub(PROOF, 'if [ "${1:-}" = "--plant-check" ]; then\n', 'if [ "${1:-}" = "--plant-check" ]; then\n    echo garbage\n'),
 'F9b --plant-check garbage with tabs, 5 fields': lambda: sub(PROOF, 'if [ "${1:-}" = "--plant-check" ]; then\n', 'if [ "${1:-}" = "--plant-check" ]; then\n    printf "a\\tb\\tOK\\td\\te\\n"\n'),
 'F10 --plant-check dies (exit 3)': lambda: sub(PROOF, 'if [ "${1:-}" = "--plant-check" ]; then\n', 'if [ "${1:-}" = "--plant-check" ]; then\n    exit 3\n'),
 'F10b --plant-check exits 0 silently': lambda: sub(PROOF, 'if [ "${1:-}" = "--plant-check" ]; then\n', 'if [ "${1:-}" = "--plant-check" ]; then\n    exit 0\n'),
 'F10c --plant-check hangs': lambda: sub(PROOF, 'if [ "${1:-}" = "--plant-check" ]; then\n', 'if [ "${1:-}" = "--plant-check" ]; then\n    sleep 200\n'),
 'F10d --plant-check checks only first id': lambda: sub(PROOF, '    for id in $PLANTS; do\n        if plant_edits', '    for id in ${PLANTS%% *}; do\n        if plant_edits'),
 'F11 floor-compensated drop: wreply out of discovery, +2 proof plants': lambda: (sub(WREPLY, 'plant_spec() {', 'plant_spec () {'), sub(PROOF, 'PLANTS="S1221', 'PLANTS="S9101 S9102 S1221'), sub(PROOF, "    *) return 1 ;;", "    S9101|S9102) plant_spec S1221 ;;\n    *) return 1 ;;")),
 'F12 stale FROM in pres multi-edit, edit 2 (S3064)': lambda: sub(PRES, "echo 'compose.c@@            return kit_fail(art, \"mf_define: the presence", "echo 'compose.c@@            return kit_fail(art, \"mf_define: THE presence"),
 'F13 stale @c0/ FROM (census0.py edited)': lambda: sub('docs/design/memfn/span_pick/census0.py', 'off, kind, val = t.split(":", 2)', 'off, kind, val = t.split(":", 2)  # moved'),
 'F14 stale PERTS (wreply, PERT 1 FROM)': lambda: sub(WREPLY, "    bool reseed = wk && wk->nwalk", "    bool reseed = wk && wk->nwalkX"),
}

def mutants():
    P, S = 'tests/lib/plants.py', 'scripts/m6read_check_sab_anchors.py'
    return {
     'Q1 un_win drops \\& rule': (P, ".replace('\\\\n', '\\n').replace('\\\\&', '&')\n", ".replace('\\\\n', '\\n')\n"),
     'Q2 un_win drops \\n rule': (P, "return s.replace('\\\\n', '\\n').replace('\\\\&', '&')\n\n\ndef un_pres", "return s.replace('\\\\&', '&')\n\n\ndef un_pres"),
     'Q3 un_pres drops \\\\\\\\n protection': (P, "s.replace('\\\\\\\\n', '\\x00').replace('\\\\n', '\\n').replace('\\x00', '\\\\n')", "s.replace('\\\\n', '\\n')"),
     'Q4 un_pres drops \\& rule': (P, ".replace('\\x00', '\\\\n').replace('\\\\&', '&')", ".replace('\\x00', '\\\\n')"),
     'Q5 wreply 3-field rule dropped': (P, "        if len(parts) != 3:\n            raise Undecodable('%d fields, not 3 (FILE@@FROM@@TO)' % len(parts))\n        f, a, b = parts\n", "        f, a, b = parts[0], parts[1], '@@'.join(parts[2:])\n"),
     'Q6 shell_split rfind': (P, "    j = rest.find('@@')", "    j = rest.rfind('@@')"),
     'Q7 check: OK if c>=1': (P, "st = 'OK' if c == 1 else", "st = 'OK' if c >= 1 else"),
     'Q8 check: STALE not counted bad': (P, "            else:\n                nbad += 1\n    for pid", "            elif c > 1:\n                nbad += 1\n    for pid"),
     'Q9 check: not cumulative': (P, "                cur[p] = cur[p].replace(a, b)   # cumulative, as the apply is\n", "                pass\n"),
     'Q10 NO SPEC not bad': (P, "            print('%s\\t0/0\\tNO SPEC\\t0\\t%s' % (pid, rel(runner)))\n            nbad += 1\n", "            print('%s\\t0/0\\tNO SPEC\\t0\\t%s' % (pid, rel(runner)))\n"),
     'Q11 ORPHAN loop removed': (P, "    for pid in case_ids(runner):\n", "    for pid in []:\n"),
     'Q12 MISSING FILE not bad': (P, "print('%s\\t%d/%d\\tMISSING FILE\\t0\\t%s' % (pid, k, n, rel(p)))\n                nbad += 1\n", "print('%s\\t%d/%d\\tMISSING FILE\\t0\\t%s' % (pid, k, n, rel(p)))\n"),
     'Q13 check always rc 0': (P, "    return 1 if nbad else 0\n", "    return 0\n"),
     'Q14 apply: count==0 only refuses': (P, "        if s.count(a) != 1:\n            sys.exit(refusal", "        if s.count(a) == 0:\n            sys.exit(refusal"),
     'Q15 apply: never writes': (P, "        open(p, 'w').write(s.replace(a, b))\n", "        pass\n"),
     'Q16 apply: returns at once': (P, "def cmd_apply(dialect, base, c0, edits):\n", "def cmd_apply(dialect, base, c0, edits):\n    return 0\n"),
     'Q17 pres @c0 -> base': (P, "(c0 + '/' + f[len('@c0/'):]) if f.startswith('@c0/') else base + '/' + f", "base + '/' + f"),
     'Q18 case_ids never matches': (P, "r'\\s*(S[0-9]+)\\)'", "r'\\s*(X[0-9]+)\\)'"),
     'Q19 UNDECODABLE not bad': (P, "print('%s\\t%d/%d\\tUNDECODABLE\\t0\\t%s' % (pid, k, n, e))\n                nbad += 1\n", "print('%s\\t%d/%d\\tUNDECODABLE\\t0\\t%s' % (pid, k, n, e))\n"),
     'Q20 AMBIGUOUS counted OK-ish (c>1 not bad)': (P, "            else:\n                nbad += 1\n    for pid", "            elif c == 0:\n                nbad += 1\n    for pid"),
     'P1 floor 0': (S, "PLANT_FLOOR = 81 ", "PLANT_FLOOR = 0 "),
     'P2 discovery drops memfn/tests': (S, 'PLANT_DIRS = ("tests", "memfn/tests")', 'PLANT_DIRS = ("tests",)'),
     'P3 no-mode runner skipped silently': (S, '        p_unreadable.append((rel, "DEFINES plant_spec BUT HAS NO --plant-check MODE"))\n', ''),
     'P4 stderr ignored': (S, "    if err.strip() or pr.returncode", "    if pr.returncode"),
     'P5 returncode ignored': (S, "pr.returncode not in (0, 1) or len(summ)", "len(summ)"),
     'P6 summary count rule dropped': (S, "or len(summ) != 1 \\\n", "or not summ \\\n"),
     'P7 row-width rule dropped': (S, "            or any(len(r) != 5 for r in rows):", "            or False:"),
     'P8 INCONSISTENT rule dropped': (S, "    if len(ids) != P or len(bad) != Bn or (pr.returncode == 0) != (Bn == 0):", "    if False:"),
     'P9 only STALE is bad': (S, 'bad = [r for r in rows if r[2] != "OK"]', 'bad = [r for r in rows if r[2] == "STALE"]'),
     'P10 p_fail ignores p_bad': (S, "p_fail = bool(p_unreadable or p_bad or nplants", "p_fail = bool(p_unreadable or nplants"),
     'P11 p_fail ignores unreadable': (S, "p_fail = bool(p_unreadable or p_bad", "p_fail = bool(p_bad"),
     'P12 exit ignores p_fail': (S, "sys.exit(1 if (unreadable or stale or p_fail) else 0)", "sys.exit(1 if (unreadable or stale) else 0)"),
     'P13 timeout not recorded': (S, '        p_unreadable.append((rel, "--plant-check TIMED OUT (120 s)"))\n', ''),
     'P14 summary-parse failure not recorded': (S, '        p_unreadable.append((rel, "--plant-check SUMMARY UNREADABLE: " + summ[0][:60]))\n', ''),
     'P15 nplants from rows not summary': (S, "    nplants += P\n", "    nplants += len(ids)\n"),
    }

if __name__ == '__main__':
    which = sys.argv[1]
    if which == 'faults':
        for name, f in FAULTS.items():
            if len(sys.argv) > 2 and not name.startswith(sys.argv[2] + ' '): continue
            try:
                f(); rc, t = fast()
            finally:
                restore()
            print('%-62s rc=%d  %s' % (name, rc, t), flush=True)
    elif which == 'mutants':
        ms = mutants(); fl = [k for k in FAULTS if not (len(sys.argv) > 2 and sys.argv[2] == 'noF10c' and k.startswith('F10c'))]
        if len(sys.argv) > 3: ms = {k: v for k, v in ms.items() if k.split()[0] in sys.argv[3].split(',')}
        for mn, (rel, a, b) in ms.items():
            res = []
            try:
                sub(rel, a, b)
            except SystemExit as e:
                print('%-40s HARNESS-ERROR %s' % (mn, e)); restore(); continue
            base = M + '/' + rel
            saved = open(base).read()
            rc0, t0 = fast()
            try:
                for fname in fl:
                    fn = FAULTS[fname]
                    try:
                        fn(); rc, t = fast()
                    finally:
                        restore(); sub(rel, a, b)
                    res.append(rc)
            finally:
                restore()
            caught = [fl[i].split()[0] for i, r in enumerate(res) if r != 0]
            missed = [fl[i].split()[0] for i, r in enumerate(res) if r == 0]
            print('%-42s clean rc=%d | faults red %d/%d | missed: %s' % (mn, rc0, len(caught), len(fl), ' '.join(missed)), flush=True)
