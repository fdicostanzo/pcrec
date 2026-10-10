#!/usr/bin/env bash
# studies/start_landing/agree_sl1.sh — SL1's CENSUS AGREEMENT CHECK (lane
# slbuild, start_landing.md §7.1 SL1 (a)): the BUILT facts `land_char` and
# `width` (src/facts/kset.c, through --emit-facts) against the design's
# PROTOTYPE PROBE (proto.patch's lp_land_fact / lp_width_interval /
# lp_fixed_width, an independent walk sharing no source with the build),
# on the same compile of every population pattern.
#
#   agree_sl1.sh SCRATCH POP.tsv... > agree.tsv   (summary on stderr)
#
# SCRATCH receives a `git archive HEAD` copy with the probe's functions
# inserted (re-anchored at this pin: the block before dfa_form_derive and the
# one call after its NEXT selection), built there; nothing is written here.
set -eu
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCR="$1"; shift
rm -rf "$SCR/tree"; mkdir -p "$SCR/tree"
git -C "$ROOT" archive HEAD | tar -x -C "$SCR/tree"
F="$SCR/tree/src/gen/emit_dfa.c"
awk '/^\+\/\* ==== \[START-LANDING\] PROTOTYPE PROBE/{on=1} on{e=($0 ~ /end PROTOTYPE PROBE/); sub(/^\+/,""); print; if (e) exit}' \
    "$ROOT/studies/start_landing/proto.patch" > "$SCR/probe.c"
grep -q '^static void lp_probe' "$SCR/probe.c"
python3 - "$F" "$SCR/probe.c" <<'PY'
import sys
f, pc = sys.argv[1], sys.argv[2]
s = open(f).read(); probe = open(pc).read()
a = "static void dfa_form_derive(Ctx *cx, const Dfa *d, const UnanchStart *us,"
b = "        f->pf  = cand_select(CAND_SLOT_NEXT, &s, flags);\n"
assert s.count(a) == 1 and s.count(b) == 1
s = s.replace(a, probe + "\n" + a).replace(b, b + "        lp_probe(cx, d, f->pf);\n")
open(f, "w").write(s)
PY
make -C "$SCR/tree" -j8 >/dev/null 2>&1
exec python3 "$ROOT/studies/start_landing/agree_sl1.py" "$SCR/tree/build/pcrec" "$@"
