#!/usr/bin/env bash
# syncheck.sh OUT [CC] : window_split.md rev 2's compile evidence over an assemble.py tree.
# `CC -fsyntax-only` of EVERY .c in OUT/memfn/src (the 21 assembled files, the edited presence.c
# and every other kit file, which read the edited kit.h), each twice: as the build compiles it
# (KITFLAGS: -O2 -g -Wall -Wextra -std=gnu11) with `make strict`'s -Wshadow -Werror and W21's
# -Wmissing-prototypes, and the same with -DMF_TRACE (the trace build, mk_mftrace_lib.sh's
# define; strict never compiles those regions). Then the four test drivers that include kit.h
# (white-box: tests/memfn/{arm_fixtures,mass_check,proven_check,run_decide_check}.c) against the assembled kit.h. One line per (file, define):
# PASS/FAIL; FAIL prints the first diagnostics. Exit 1 iff any FAIL. CC defaults to gcc-16 (the
# Mac's GNU gcc, tests/lib/cc_resolve.sh; bare gcc there is Apple clang).
set -u
out=$1; cc=${2:-gcc-16}
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
flags="-O2 -g -Wall -Wextra -std=gnu11 -Wshadow -Werror -Wmissing-prototypes"
pass=0; fail=0
run() {   # label file extra-flags...
    local f=$1; shift
    local msg
    if msg=$("$cc" $flags "$@" -fsyntax-only "$f" 2>&1); then
        echo "PASS ${DEF:-plain} $(basename "$f")"; pass=$((pass+1))
    else
        echo "FAIL ${DEF:-plain} $(basename "$f")"; echo "$msg" | grep -E 'error|warning' | head -4 | sed 's/^/    /'
        fail=$((fail+1))
    fi
}
for DEF in plain MF_TRACE; do
    d=""; [ "$DEF" = MF_TRACE ] && d="-DMF_TRACE"
    for f in "$out"/memfn/src/*.c; do run "$f" $d; done
done
# the white-box drivers: their own include line names memfn/src/kit.h by a relative path, so
# they are compiled from a copy placed in the assembled tree's shape
for DEF in plain; do
    for t in tests/memfn/arm_fixtures.c tests/memfn/mass_check.c tests/memfn/proven_check.c \
             tests/memfn/run_decide_check.c; do
        mkdir -p "$out/$(dirname "$t")"; cp "$root/$t" "$out/$t"
        flags_save=$flags; flags="-O2 -g -Wall -Wextra -std=gnu11"
        run "$out/$t" -I"$out/memfn/src" -I"$out/memfn/include" -I"$root/lib" -I"$root/src"
        flags=$flags_save
    done
done
echo "syncheck: $pass PASS, $fail FAIL ($cc)"
[ "$fail" = 0 ]
