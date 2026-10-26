#!/usr/bin/env bash
# mkprobe.sh -- build the rwsurvey probe: a pcrec CLI whose compile driver is a
# COPY of src/core/compile.c with dump hooks injected by sed (src/ is not edited).
# Usage: studies/rwsurvey/mkprobe.sh   (run from anywhere; builds under build/probe/)
# Output: build/probe/pcrec_probe. Run it with PROBE_OUT=file to collect the dump.
set -eu
W=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
P=$W/build/probe
mkdir -p "$P"
SRC=$W/src/core/compile.c
OUT=$P/compile_probe.c

# hooks, one anchored sed per site; each must match exactly once (checked below)
sed \
 -e 's|^#include "core/internal.h"$|#include "core/internal.h"\n#include "probe_hooks.h"\n#define pcrec_scanedge_dfa(cx, d, ...) (probe_dfa((cx), (d), #d, __LINE__), (pcrec_scanedge_dfa)((cx), (d), __VA_ARGS__))|' \
 -e 's|^        Ast \*root = pcrec_parse(&cx);$|        Ast *root = pcrec_parse(\&cx); probe_begin(\&cx); probe_ast(\&cx, "1-parse", root);|' \
 -e 's|^        root = pcrec_altcls(&cx, root);$|        probe_ast(\&cx, "2-hooks", root); root = pcrec_altcls(\&cx, root); probe_ast(\&cx, "3-altcls", root);|' \
 -e 's|^        root = pcrec_discharge_atomic(&cx, root);$|        root = pcrec_discharge_atomic(\&cx, root); probe_ast(\&cx, "4-discharge", root);|' \
 -e 's|^        pcrec_select_engine(&cx, root);$|        pcrec_select_engine(\&cx, root); probe_ast(\&cx, "5-select", root);|' \
 -e 's|^        root = pcrec_lower_enc(&cx, root);$|        root = pcrec_lower_enc(\&cx, root); probe_ast(\&cx, "6-lower", root);|' \
 "$SRC" > "$OUT"
for pat in 'probe_hooks.h' '"1-parse"' '"3-altcls"' '"4-discharge"' '"5-select"' '"6-lower"'; do
    n=$(grep -c -F "$pat" "$OUT")
    [ "$n" -ge 1 ] || { echo "hook site not found: $pat" >&2; exit 1; }
done
FLAGS="-O2 -g -Wall -Wextra -std=gnu11 -I$W/lib -I$W/src -I$W/studies/rwsurvey"
gcc $FLAGS -c "$OUT" -o "$P/compile.o"
gcc $FLAGS -c "$W/studies/rwsurvey/probe_hooks.c" -o "$P/probe_hooks.o"
cp "$W/build/libpcrec.a" "$P/libpcrec_probe.a"
ar d "$P/libpcrec_probe.a" compile.o
ar r "$P/libpcrec_probe.a" "$P/compile.o" "$P/probe_hooks.o" 2>/dev/null
gcc $FLAGS -o "$P/pcrec_probe" "$W/cli/main.c" "$P/libpcrec_probe.a"
echo "built $P/pcrec_probe"
