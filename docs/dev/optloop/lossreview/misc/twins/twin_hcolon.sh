#!/bin/bash
# lossreview/misc twin T3: is rlhbuild's hcolon ENTRY-only +13% (open item 4) the
# handoff's DATA DEPENDENCY (the forward scan's first table load now waits on
# memchr's return through `scan_position = handoff_position`) or its extra
# arithmetic (pointer->index, two compares, the clamp)?
#   twin_hcolon.sh MAIN_PCREC RLH_PCREC WORKDIR SUBJECT_DIR
# MAIN_PCREC = a compiler at main; RLH_PCREC = a compiler built from lane/rlhbuild
# (git archive + make); SUBJECT_DIR = rlhbuild's gen_hostile.py output.
# Arms (hcolon `[a-y]\d{0,150}:`): ra = main; rb = lane (entry handoff on); rc = rb with
# the dependency cut:  `size_t scan_position = search_from; asm volatile("" :: "r"(handoff_position));`
# (the arithmetic and the early return stay).  Identity: rb and rc against ra.  NOTHING IS TIMED.
set -e
HH=$(cd "$(dirname "$0")" && pwd); MISC=$(dirname "$HH")
M=$(realpath "$1"); L=$(realpath "$2"); mkdir -p "$3"; W=$(realpath "$3"); S=$(realpath "$4")
P='[a-y]\d{0,150}:'; cd "$W"
"$M" --features all -p ra -o ra.c --pattern "$P"
"$L" --features all -p rb -o rb.c --pattern "$P"
python3 - <<'PY'
s = open('rb.c').read().replace('rb_', 'rc_').replace('RB_', 'RC_').replace('"rb.h"', '"rc.h"')
old = "    size_t scan_position = handoff_position;\n"
assert old in s
s = s.replace(old, "    size_t scan_position = search_from; __asm__ volatile(\"\" : : \"r\"(handoff_position));\n", 1)
open('rc.c', 'w').write(s)
PY
sed 's/rb_/rc_/g; s/RB_/RC_/g' rb.h > rc.h
for B in rb rc; do
  gcc -O2 -w -I. -DAP=ra -DBP=$B "$MISC/ident.c" ra.c $B.c -o ident_$B
  echo "== $B vs ra (MUST be 0 differences):"; ./ident_$B "$S"/*.bin | tail -2
done
cat <<'EOF'
TIMING (QUIET SLOT): build ra/rb/rc each as prefix rx in its own dir (re-run the three compiles with -p rx and the rc edit),
  gcc -O2 -I DIR studies/walk_survey/fatime.c DIR/rx.c -o DIR/fa ; per colon-dense subject: taskset -c 3 DIR/fa SUBJ findall 21
  interleaved over 8 pad layouts. READING: rc ~ ra  => the dependency is the cost (a fix keeps the gate off the scan's critical path);
  rc ~ rb => the arithmetic is the cost (a fix prices the entry form into the admission).
EOF
