#!/usr/bin/env bash
# docs/design/artsize_impl/probes/witness_figures.sh — [ART-SIZE] the note's
# WITNESS FIGURES, with their recipe archived beside them (r42 M2/M6).
#
# WHY THIS EXISTS. The note quoted witness figures (87,118 / 1,718,425 /
# 670,650 and friends) that could not be reproduced at delivery: the emitter
# moved during the lane, and the numbers had been recorded WITHOUT the command
# that produced them. Two independent re-measurements (this lane's and the r42
# critic's) disagreed with the note AND with each other, which is what an
# unarchived recipe buys. The classifier was never the problem — it is
# `probes/measure.py`'s `scan()`, i.e. `tests/lib/size_count.sh`'s comment
# rule, and it still agrees to the byte (witness 1's 7,467 labels reproduce
# exactly). Only the BYTES moved.
#
# The rule this file exists to enforce: a figure in the note is quoted WITH the
# recipe that produces it, and the recipe is a file, not a sentence.
#
# Usage: bash docs/design/artsize_impl/probes/witness_figures.sh
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
IMPL="$ROOT_DIR/docs/design/artsize_impl"
. "$ROOT_DIR/tests/lib/size_count.sh"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export ROOT_DIR
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT

# Caps raised out of the way wherever a figure is about an artifact the shipped
# caps REFUSE: the figure is the size that justifies the refusal, so it cannot
# be measured through the refusal.
RAISE="--max-emit-code-bytes=99999999 --max-emit-bytes=99999999"

row() { # label, flags..., pattern
    local label="$1"; shift
    local pat="${!#}"; set -- "${@:1:$#-1}"
    if pcrec_run "$PCREC" -p rx --features all "$@" -o "$W/a.c" -- "$pat" 2>/dev/null; then
        # THREE QUANTITIES, NOT ONE -- §4.3b's whole lesson. `non-prose` is
        # total minus comments (the size log's and the TOTAL cap's quantity);
        # `code` additionally excludes table initializers (the CODE cap's
        # quantity); `raw` is the file. Quoting one where the other is meant
        # is the mistake this row made three times.
        python3 - "$W/a.c" "$label" <<'PYEOF'
import importlib.util, sys, os, re
root = os.environ["ROOT_DIR"]
spec = importlib.util.spec_from_file_location(
    "m", os.path.join(root, "docs/design/artsize_impl/probes/measure.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
t = open(sys.argv[1]).read(); d = m.scan(t)
k = re.search(r"^#define RX_UNROLL_K (\d+)", t, re.M)
print("%-34s non-prose=%-10d code=%-10d raw=%-10d K=%-2s labels=%d" % (
    sys.argv[2], d["total"] - d["prose"],
    d["total"] - d["prose"] - d["tables"], d["total"],
    k.group(1) if k else "-", d["labels"]))
PYEOF
    else
        printf '%-34s REFUSED\n' "$label"
    fi
}

echo "== [ART-SIZE] witness figures at $(git -C "$ROOT_DIR" rev-parse --short HEAD) =="
echo "recipe: build/pcrec -p rx --features all [flags] -o FILE -- PATTERN"
echo "size:   tests/lib/size_count.sh's size_count_bytes (total minus comment bytes)"
echo
W1="$(cat "$IMPL/k41_w1.txt")"
W2="$(cat "$IMPL/k41_w2.txt")"
NEST8='((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}'

# shellcheck disable=SC2086
{
row "K41 witness 1, term's own K"        "$W1"
row "K41 witness 1, K=8 (term denied)"   -fno-size-term $RAISE "$W1"
row "K41 witness 2, term's own K"        $RAISE "$W2"
row "K41 witness 2, K=8 (term denied)"   -fno-size-term $RAISE "$W2"
row "nested N=8, term's own K"           "$NEST8"
row "nested N=8, K=8 (term denied)"      -fno-size-term "$NEST8"
}
