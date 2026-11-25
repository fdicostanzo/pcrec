#!/usr/bin/env bash
# controls.sh TREE BASE_CHECKER SCRATCH (lane plantfix, 2026-11-24): the plant pass's controls,
# each on its OWN extracted copy of TREE's committed HEAD (git archive) under SCRATCH, never the
# live tree. Prints one "CONTROL <name>: rc=<rc> <verdict line(s)>" per control.
#   C0 positive        the copy as committed: 81 read, all apply, rc 0
#   C1 stale FROM      one runner's FROM corrupted (S1401 in run_g2_win.sh): rc 1, names S1401 STALE
#   C2 discovery       run_wreply.sh's plant_spec renamed out of discovery: rc 1, floor red (79 < 81)
#   C3 runner gone     run_proof.sh deleted: rc 1, floor red (75 < 81)
#   C4 no mode         a discovered runner without --plant-check: rc 1, UNREADABLE, never run
#   C5 orphan          a plant_spec case PLANTS does not list: rc 1, ORPHAN
#   C6 ambiguous       a FROM that occurs twice (S1423's bound line alone): rc 1, AMBIGUOUS
#   M  mech identity   the mech rows' output lines equal BASE_CHECKER's on the same copy
set -u
TREE=$1; BASE=$2; SCR=$3
mkdir -p "$SCR"
fresh() {   # fresh NAME: a new copy of HEAD; prints its path
    local d; d=$(mktemp -d "$SCR/ctl_$1.XXXXXX")
    git -C "$TREE" archive HEAD | tar -xf - -C "$d"
    echo "$d"
}
run() {   # run NAME DIR: the copy's own checker
    local out rc
    out=$(python3 -I "$2/scripts/m6read_check_sab_anchors.py" 2>&1); rc=$?
    echo "CONTROL $1: rc=$rc"
    printf '%s\n' "$out" | sed -n '/^runner plants checked/,$p' | sed 's/^/    /'
}
d=$(fresh c0); run C0-positive "$d"
d=$(fresh c1)
python3 -I - "$d/memfn/tests/run_g2_win.sh" <<'EOF'
import sys
p = sys.argv[1]; s = open(p).read()
o = "join = !p->one_pos \\&\\& !q->one_pos \\&\\&@@"
assert s.count(o) == 1
open(p, "w").write(s.replace(o, "join = !p->one_pos \\&\\& !q->one_pos \\&\\& XYZZY_STALE@@"))
EOF
run C1-stale-FROM "$d"
d=$(fresh c2); sed -i.bak 's/^plant_spec() {/plant_spec_hidden() {/' "$d/tests/memfn/run_wreply.sh"; rm -f "$d/tests/memfn/run_wreply.sh.bak"
run C2-runner-out-of-discovery "$d"
d=$(fresh c3); rm -f "$d/tests/memfn/run_proof.sh"; run C3-runner-deleted "$d"
d=$(fresh c4); printf '#!/usr/bin/env bash\necho THIS RUNNER WAS RUN > "%s/c4_ran"\nplant_spec() {\n    case "$1" in S9) echo x ;; esac\n}\nPLANTS="S9"\n' "$d" > "$d/tests/memfn/run_nomode.sh"
run C4-no-check-mode "$d"; [ -e "$d/c4_ran" ] && echo "    C4: THE RUNNER WAS RUN (wrong)" || echo "    C4: the runner was not run"
d=$(fresh c5)
python3 -I - "$d/tests/memfn/run_proof.sh" <<'EOF'
import sys
p = sys.argv[1]; s = open(p).read()
o = "    *) return 1 ;;\n    esac\n}\nPLANTS=\"S1221"
assert s.count(o) == 1
open(p, "w").write(s.replace(o, "    S9999) echo 'compose.c@@long d = (long)t->offset + j;@@long d = 0;' ;;\n" + o))
EOF
run C5-orphan-case "$d"
d=$(fresh c6)
python3 -I - "$d/memfn/tests/run_g2_win.sh" <<'EOF'
import sys
p = sys.argv[1]; s = open(p).read()
o = "echo 'window.c@@    int ih = w->hix;\\n    kb_printf(b, \"if (!(%s)) break; \", bound);@@"
assert s.count(o) == 1
open(p, "w").write(s.replace(o, "echo 'window.c@@    kb_printf(b, \"if (!(%s)) break; \", bound);@@"))
EOF
run C6-ambiguous-FROM "$d"
d=$(fresh m)
new=$(python3 -I "$d/scripts/m6read_check_sab_anchors.py" 2>&1 | sed '/^runner plants checked/,$d')
cp "$BASE" "$d/scripts/base_checker.py"
old=$(python3 -I "$d/scripts/base_checker.py" 2>&1)
if [ "$new" = "$old" ]; then echo "CONTROL M-mech-identity: SAME ($(printf '%s\n' "$old" | head -1))"
else echo "CONTROL M-mech-identity: DIFFERENT"; diff <(printf '%s\n' "$old") <(printf '%s\n' "$new"); fi
