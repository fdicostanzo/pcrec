#!/usr/bin/env bash
# tests/core/ksrc_deps_check.sh ROOT [WORKDIR] — [KNOW-SRC] the knowledge
# module's DEPENDENCY RULE (docs/design/measure_sets.md rev 3 §9.2, sabotage
# S989): the kind-independent parts, src/core/ksrc.c and src/core/ksrc.h,
# include libc/POSIX headers and `core/ksrc.h` ONLY, so a tool that links
# them (`pcrec-measure`, §7.1) links nothing else of src/.
#
# Two independent halves, because each is blind where the other sees:
#   (a) the INCLUDE LINES, read as text: every `#include "..."` must be
#       "core/ksrc.h" (a `<...>` header is the platform's);
#   (b) the OBJECT: ksrc.c compiled ALONE with `-Isrc` and no `-Ilib`
#       (core/internal.h needs lib/pcrec.h, so a hidden include fails here
#       even if (a)'s text scan were fooled, e.g. by a macro include), and
#       its UNDEFINED symbols (`nm -u`) hold no `pcrec_` name — the parts
#       call nothing of the compiler, whatever header declared it.
# The `nm -u` half on the linked `pcrec-measure` binary joins at M3, when
# that binary exists.
#
# Control: (a) is re-run on a copy of ksrc.c with `#include
# "core/internal.h"` planted, which must FAIL. The population — include
# lines read, undefined symbols listed — is printed and must be non-zero.
set -u
export LC_ALL=C
ROOT="$1"
W="${2:-$(mktemp -d)}"
CC="${CC:-gcc}"
pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1"; fail=$((fail + 1)); }

# (a) the include lines of a file, as `file: include` rows for every quoted
# include other than core/ksrc.h; prints the population on stderr.
quoted_offenders() {
    local n
    n="$(grep -cE '^[[:space:]]*#[[:space:]]*include' "$@" | awk -F: '{s+=$NF} END {print s+0}')"
    echo "$n" > "$W/ninc"
    grep -HE '^[[:space:]]*#[[:space:]]*include[[:space:]]*"' "$@" |
        grep -vE '#[[:space:]]*include[[:space:]]*"core/ksrc\.h"'
}
off="$(quoted_offenders "$ROOT/src/core/ksrc.c" "$ROOT/src/core/ksrc.h")"
ninc="$(cat "$W/ninc")"
if [ "$ninc" -lt 3 ]; then
    bad "ksrc deps (a): only $ninc include line(s) read in ksrc.c/ksrc.h — the scan has stopped matching (K35)"
elif [ -n "$off" ]; then
    bad "ksrc deps (a): the parts include outside libc + core/ksrc.h: $(echo "$off" | tr '\n' ' ')"
else
    ok "ksrc deps (a): $ninc include lines in ksrc.c/ksrc.h, every quoted one core/ksrc.h"
fi
# the control
mkdir -p "$W/plant/core"
cp "$ROOT/src/core/ksrc.h" "$W/plant/core/"
sed 's|^#include "core/ksrc.h"|#include "core/internal.h"\n#include "core/ksrc.h"|' \
    "$ROOT/src/core/ksrc.c" > "$W/plant/core/ksrc.c"
if quoted_offenders "$W/plant/core/ksrc.c" | grep -q 'core/internal.h'; then
    ok "ksrc deps (a) control: a planted #include \"core/internal.h\" is reported"
else
    bad "ksrc deps (a) control: a planted #include \"core/internal.h\" was NOT reported — (a) cannot fail"
fi

# (b) the object, alone
if ! "$CC" -std=gnu11 -O2 -Wall -Wextra -Werror -I"$ROOT/src" -c \
        -o "$W/ksrc.o" "$ROOT/src/core/ksrc.c" 2> "$W/ksrc.cc"; then
    bad "ksrc deps (b): src/core/ksrc.c does not compile with -Isrc alone: $(head -3 "$W/ksrc.cc" | tr '\n' ' ')"
else
    und="$(nm -u "$W/ksrc.o" | awk '{print $NF}')"
    nund="$(printf '%s\n' "$und" | grep -c .)"
    bad_syms="$(printf '%s\n' "$und" | grep '^_\?pcrec_')"
    if [ "$nund" -lt 1 ]; then
        bad "ksrc deps (b): nm -u listed no undefined symbol at all — the listing is not being read (K35)"
    elif [ -n "$bad_syms" ]; then
        bad "ksrc deps (b): ksrc.o calls the compiler: $(echo "$bad_syms" | tr '\n' ' ')"
    else
        ok "ksrc deps (b): ksrc.c builds with -Isrc alone and its $nund undefined symbols are libc's ($(echo "$und" | tr '\n' ' '))"
    fi
fi
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
