#!/bin/bash
# slotarms/verify.sh -- (1) the stamps: each cell's artifact runs the engine arms.tsv says, and no kit
# search form is on its path; (2) answers: every (cell, subject, mode) equals python3 `re`.
# Not a timing run. Exit 0 = all green.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
OUT=${OUT:-$ROOT/build/slotarms}
bad=0
while IFS=$'\t' read -r cell pat flags fam eng vmp note; do
  case "$cell" in '#'*|'') continue ;; esac
  c=$OUT/bin/$cell/V0/art.c
  st() { sed -n "s/^#define RX_$1 \"\(.*\)\"/\1/p" "$c" "${c%.c}.h" | head -1; }
  got=$(st ENGINE); vp=$(st VM_PREFILTER); forms=$(st MEMFN_FORMS); libc=$(st MEMFN_LIBC); dpf=$(st DFA_PREFILTER)
  ok=1
  [ "$got" = "$eng" ] || ok=0
  [ "$vmp" = - ] || [ "$vp" = "$vmp" ] || ok=0
  [ "$forms" = none ] || ok=0     # no memfn find form rendered anywhere in the artifact
  [ "$libc" = none ] || ok=0      # nor a libc memchr/memrchr skip
  printf '%-8s engine=%s vm_prefilter=%s dfa_prefilter=%s memfn_forms=%s memfn_libc=%s %s\n' "$cell" "$got" "${vp:--}" "${dpf:--}" "$forms" "$libc" "$([ $ok = 1 ] && echo ok || echo STAMP-MISMATCH)"
  [ $ok = 1 ] || bad=1
done < "$HERE/arms.tsv"
python3 -I - "$OUT" "$HERE/arms.tsv" <<'PY' || bad=1
import re, subprocess, sys, os
out, spec = sys.argv[1:3]
SUBJ = {"w2": ["e0", "nm8", "nm64", "nm1k", "nm64k", "mw2-L8", "mw2-L64", "mw2-L1k"],
        "w5": ["e0", "nm8", "nm64", "nm1k", "nm64k", "mw5-L8", "mw5-L64", "mw5-L1k"]}
rows = 0; fails = 0
for ln in open(spec):
    if ln.startswith("#") or not ln.strip(): continue
    cell, pat, flags, fam = ln.rstrip("\n").split("\t")[:4]
    rx = re.compile(pat.encode())
    for s in SUBJ[fam]:
        data = open(os.path.join(out, "subj", s), "rb").read()
        ms = [m for m in rx.finditer(data) if True]
        for mode in ("first", "all"):
            if mode == "all" and not s.startswith("m"): continue
            r = subprocess.run([f"{out}/bin/{cell}/V0/run", f"{out}/subj/{s}", mode, "check"], capture_output=True, text=True).stdout.split()
            got = dict(x.split("=", 1) for x in r)
            want_n = len(ms) if mode == "all" else (1 if ms else 0)
            f = ms[0].span() if ms else (-1, -1)
            ok = int(got.get("matches", -1)) == want_n and got.get("first") == "%d:%d" % f
            rows += 1
            if not ok:
                fails += 1; print("MISMATCH", cell, s, mode, got, "want", want_n, f)
print(f"answers: {rows} (cell,subject,mode) checks vs python re, {fails} mismatches")
sys.exit(1 if fails else 0)
PY
[ $bad = 0 ] && echo "verify: GREEN" || echo "verify: RED"
exit $bad
