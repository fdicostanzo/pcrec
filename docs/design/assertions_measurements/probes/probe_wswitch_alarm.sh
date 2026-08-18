#!/bin/sh
# [M6.1]/R30 M8 — does adding an AKind ENUMERATOR actually raise an alarm?
#
# assertions_design.md S8.3 decides the flag-vs-node-kind spelling on this
# measurement, so the measurement has to be repeatable by a read-only critic
# rather than a transcript to trust. The first version of this number was
# produced by a hand edit and reverted by hand, which is unverifiable — R30
# M8. This is that experiment as an instrument.
#
# WHAT IT DOES: appends one probe enumerator to `AKind` in src/core/internal.h,
# runs `gcc -fsyntax-only` over every .c file that switches on a node kind,
# counts the -Wswitch diagnostics, and RESTORES the header. It compiles
# nothing into build/ and leaves no artifact.
#
# The complementary arm needs no experiment and is stated rather than run:
# adding a FIELD to `struct Ast` produces zero diagnostics anywhere, by
# construction — nothing in C warns that a struct member is unread.
#
# SAFETY: the header is copied first and restored by an EXIT trap, so an
# interrupted run cannot leave the tree edited. The script verifies the
# restore and says so; if it cannot restore it says THAT loudly rather than
# exiting quietly.
#
# Usage: probe_wswitch_alarm.sh REPO_ROOT
set -e
ROOT=$1
HDR="$ROOT/src/core/internal.h"
BAK=$(mktemp)
cp "$HDR" "$BAK"

restore() {
    cp "$BAK" "$HDR"
    if cmp -s "$BAK" "$HDR"; then
        echo
        echo "header RESTORED (byte-identical to the pre-run copy)"
    else
        echo "*** RESTORE FAILED -- $HDR differs from $BAK ***" >&2
    fi
    rm -f "$BAK"
}
trap restore EXIT

echo "repo         : $ROOT"
echo "gcc          : $(gcc -dumpversion)"
echo "header sha   : $(sha1sum "$HDR" | cut -c1-12)  (before edit)"
echo

python3 - "$HDR" <<'EOF'
import sys
p = sys.argv[1]; s = open(p).read()
old = "    A_CAP\n} AKind;"
new = ("    A_CAP,\n"
       "    A_PROBE_ONLY_M6_1   /* added by probe_wswitch_alarm.sh; reverted */\n"
       "} AKind;")
assert old in s, "AKind's tail is not the shape this probe patches"
open(p, "w").write(s.replace(old, new, 1))
print("probe enumerator A_PROBE_ONLY_M6_1 appended to AKind")
EOF

echo
echo "=== gcc -fsyntax-only -Wall -Wextra, every .c that switches on a node kind ==="
LOG=$(mktemp)
RAW=$(mktemp)
for f in src/opt/possessify.c src/ir/nfa.c src/gen/emit_vm.c \
         src/opt/mrl.c src/opt/revdet.c src/opt/altcls.c; do
    gcc -fsyntax-only -Wall -Wextra -std=gnu11 \
        -I"$ROOT/lib" -I"$ROOT/src" "$ROOT/$f" >>"$RAW" 2>&1 || true
done
grep "A_PROBE_ONLY_M6_1.*not handled in switch" "$RAW" > "$LOG" || true

# A BROKEN gcc INVOCATION MUST NOT READ AS "no warnings" -- that is this
# probe's own version of the failure mode the design keeps finding elsewhere
# (a control that stops controlling and says nothing). A run that produced no
# -Wswitch lines AND no output at all never compiled anything.
if [ ! -s "$LOG" ] && ! grep -q "warning:\|error:" "$RAW"; then
    echo "*** THIS RUN COMPILED NOTHING -- gcc produced no diagnostics at all." >&2
    echo "*** Treat the counts below as INVALID, not as zero. First lines:" >&2
    head -5 "$RAW" >&2
fi

sed "s|$ROOT/||" "$LOG"
echo
echo "total -Wswitch diagnostics : $(wc -l < "$LOG")"
echo "distinct files             : $(sed 's/:.*//' "$LOG" | sort -u | wc -l)"
echo
echo "by file:"
sed "s|$ROOT/||;s/:.*//" "$LOG" | sort | uniq -c | sed 's/^/  /'
rm -f "$LOG" "$RAW"

echo
echo "Under \`make strict\` (-Werror) each of these is a BUILD FAILURE."
echo "The complementary arm is zero by construction: adding a struct FIELD"
echo "warns nowhere, which is why a flag's failure mode is silent."
