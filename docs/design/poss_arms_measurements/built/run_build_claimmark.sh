#!/usr/bin/env bash
# CLAIM-vs-MARK against the BUILT compiler (lane possbuild-cm).  Run from
# anywhere inside the worktree; scratch goes in <worktree>/build/cm.
# Verifies the frozen sha1s first, then generates the three row files,
# then runs claimmark_build.py (base = -fno-poss-ctx-follow
# -fno-poss-bref-first, armed = default).  ~50 s with JOBS=8.
set -eu
export LC_ALL=C
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$HERE/../../../.." && pwd)
R=$HERE/../rev21
S=$ROOT/build/cm; mkdir -p "$S/bin" "$S/tmp"; export TMPDIR=$S/tmp
want="2fec0c2439e3e323a174cc33c915a38622b2ed57 gen_a21.py
5bb09dfbcc3a612360c4bbe90d07d132a9a0c765 gen_a021.py
9f9e7d92aa32f657c6f7a0ce3bf6b816a844eef8 gen_b21.py
d2288d1a9c6bcd0c674417b7d4f7809c5fe8fbf6 r21_claimmark.py"
got=$(cd "$R" && sha1sum gen_a21.py gen_a021.py gen_b21.py r21_claimmark.py | sed 's/  / /')
[ "$got" = "$want" ] || { echo "FROZEN SHA1 MISMATCH"; echo "$got"; exit 9; }
gcc -O2 -o "$S/bin/pcre2test" "$HERE/pcre2test_shim.c" -lpcre2-8
export PATH=$S/bin:$PATH
for g in gen_a21 gen_a021 gen_b21; do python3 -B "$R/$g.py" > "$S/$g.tsv" 2>/dev/null; done
PROTO=$ROOT/build/pcrec JOBS=${JOBS:-8} UCP_PIN=4502 python3 -B "$HERE/claimmark_build.py" \
    "$S/gen_a21.tsv" "$S/gen_a021.tsv" "$S/gen_b21.tsv" > "$S/claimmark_build.out" 2> "$S/claimmark_build.err"
echo "rc=$?"; grep '^#' "$S/claimmark_build.out"
