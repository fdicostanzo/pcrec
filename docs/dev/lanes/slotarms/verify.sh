#!/bin/bash
# slotarms/verify.sh -- OUT=<dir> bash verify.sh (after build.sh). Not a timing run; exit 0 = green.
# (1) stamps per arm: the engine/vm-prefilter arms.spec (embedded in build.sh) says, and no kit form
#     (RX_MEMFN_FORMS / RX_MEMFN_LIBC both "none"); (2) every (cell, arm, subject, mode) vs python3 `re`.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:?set OUT}
SPEC=$(mktemp -p "$OUT/tmp")
sed -n "/^cat > \"\$W\/arms.spec\" <<'SPEC_EOF'/,/^SPEC_EOF/p" "$HERE/build.sh" | sed '1d;$d' > "$SPEC"
bad=0
while IFS=$'\t' read -r p arm fam pat flags eng vmp; do
  case "$p" in '#'*|'') continue ;; esac
  c=$OUT/bin/$p-first/$arm/art.c
  st() { sed -n "s/^#define RX_$1 \"\(.*\)\"/\1/p" "$c" "${c%.c}.h" | head -1; }
  got=$(st ENGINE); vp=$(st VM_PREFILTER); forms=$(st MEMFN_FORMS); libc=$(st MEMFN_LIBC)
  ok=1; [ "$got" = "$eng" ] || ok=0; [ "$vmp" = - ] || [ "$vp" = "$vmp" ] || ok=0
  [ "$forms" = none ] && [ "$libc" = none ] || ok=0
  printf '%-3s %-4s engine=%s vm_prefilter=%s memfn_forms=%s memfn_libc=%s %s\n' "$p" "$arm" "$got" "${vp:--}" "$forms" "$libc" "$([ $ok = 1 ] && echo ok || echo MISMATCH)"
  [ $ok = 1 ] || bad=1
done < "$SPEC"
python3 -I - "$OUT" "$SPEC" "$HERE/arms.tsv" <<'PY' || bad=1
import re, subprocess, sys, os
out, spec, tsv = sys.argv[1:4]
pats = {}
for ln in open(spec):
    if ln.startswith("#") or not ln.strip(): continue
    f = ln.rstrip("\n").split("\t"); pats[f[0]] = f[3]
rows = fails = 0
for ln in open(tsv):
    if ln.startswith("#") or not ln.strip(): continue
    cell, arm, role, subjects, modes = ln.rstrip("\n").split("\t")
    rx = re.compile(pats[cell.split("-")[0]].encode())
    for s in subjects.split(","):
        data = open(f"{out}/subj/{s}", "rb").read()
        ms = list(rx.finditer(data))
        for mode in modes.split(","):
            r = subprocess.run([f"{out}/bin/{cell}/{arm}/run", f"{out}/subj/{s}", mode, "check"], capture_output=True, text=True).stdout.split()
            got = dict(x.split("=", 1) for x in r)
            want_n = len(ms) if mode == "all" else (1 if ms else 0)
            f = ms[0].span() if ms else (-1, -1)
            ok = int(got.get("matches", -1)) == want_n and got.get("first") == "%d:%d" % f
            c = subprocess.run([f"{out}/bin/{cell}/{arm}/cnt", f"{out}/subj/{s}", "list", mode], capture_output=True, text=True).stderr.split()
            cd = dict(x.split("=", 1) for x in c)
            ok = ok and int(cd["matches"]) == want_n and int(cd["bytes"]) == len(data) and int(cd["calls"]) == (want_n + 1 if mode == "all" else 1)
            rows += 1
            if not ok: fails += 1; print("MISMATCH", cell, arm, s, mode, got, cd, "want", want_n, f)
print(f"answers: {rows} (cell,arm,subject,mode) checks vs python re (+ cnt twin), {fails} mismatches")
sys.exit(1 if fails else 0)
PY
rm -f "$SPEC"; [ $bad = 0 ] && echo "verify: GREEN" || echo "verify: RED"; exit $bad
