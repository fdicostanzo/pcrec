# tests/lib/unit_cc.sh — [REVW.U L5-R0] THE ONE WAY AN INTERNAL-PROPERTY
# CHECK IS BUILT.
#
# WHY THIS EXISTS. `docs/dev/reviews/lens_reports/lens5_unit_seams.md` found
# that this repo already has a unit tier — ten C programs in six directories
# that `#include "core/internal.h"`, link `libpcrec.a` and assert a property
# of an internal helper directly, below any answer — and that it has **four
# divergent flag policies** across its ten build sites, two of them absent
# from `san_scripts.txt` (fixed separately, [REVW.FIX] L5-R0.2). The tier's
# missing shared build is a live coverage hole, not a tidiness complaint:
# `tests/codegen/cpset_model_check.c`, the tree's best unit check, had never
# been built under a sanitizer, because its own build site named no
# `$SANFLAGS` at all and nothing forced the two to agree.
#
# ONE FUNCTION. Every unit-tier build site becomes one call:
#
#   unit_build <outbin> <src.c> [extra compiler args/sources...]
#
# It resolves a real GNU `$CC` (sources tests/lib/cc_resolve.sh if the
# caller has not already), applies `-Ilib -Isrc`, threads `$SANFLAGS` (the
# SAN-1 override every san target sets) and links `$LIBPCREC` (default
# `<root>/build/libpcrec.a`, the SAME override name `cwmax_check.c`'s own
# build site already reads — this file does not invent a second spelling).
# Anything passed after `<src.c>` is appended to the compiler invocation
# VERBATIM, after the library — extra libs (`-ldl`), an extra include dir
# for a per-test scratch directory, or an extra generated source to link
# alongside the check.
#
# THE WARNING POLICY IS `-Werror` UNCONDITIONALLY, and it is the real
# decision this file makes (R0.1's own recommendation, argued against
# R5-Q1 rather than in ignorance of it). `docs/testing.md`'s K28 entry:
# `-Werror` on a compile path found a maybe-uninitialized read no answer
# check could see, and it stops at the FIRST report — which is why K28's
# entry "named ONE site and there were THREE." R5-Q1 keeps `-Werror` out of
# `make`'s own default so a stranger's newer gcc cannot fail their PLAIN
# BUILD; these are TEST compiles, already gated behind a suite whose
# failure the stranger is expected to read, exactly the distinction
# `GENCFLAGS`'s own `-O1 -Werror` already draws for generated code.
#
# WHAT THIS FILE DOES NOT COVER, ON PURPOSE. The two `fold_agreement_
# check.c` sites (tests/backrefs/run_backref_diff.sh) and
# `startbnd_backend_check.c` (tests/utf8/run_startbnd_diff.sh) compile a
# check ALONGSIDE a GENERATED matcher artifact (`gen.c`) through
# `$GENCFLAGS`/`gen_cc` — the tree's established, deliberate flag regime
# for compiling GENERATED code (D45's budgets), which predates this file
# and is orthogonal to it: those sites are not part of R0's "four divergent
# policies" defect (GENCFLAGS is itself one uniform, already-`-Werror`-
# capable policy under `make san`), and folding a check that also compiles
# a generated artifact into a helper whose whole contract is "one compiler,
# one flag set, link libpcrec.a" would either strip GENCFLAGS off the
# artifact half or bolt a second compiler invocation onto a shape this
# file's own R0.4 cost budget (one gcc invocation per SUBJECT) argues
# against. `docs/dev/lanes/waveu_report.md` records this as a scoping
# decision, not an oversight.
#
# THE COST BUDGET IS A SHAPE (R0.4), stated here because this file is where
# it is enforced by construction: ONE gcc invocation and ONE process spawn
# per SUBJECT. A check that needs to invoke `pcrec` or `gcc` PER CASE is a
# differential driver and belongs in the suite that owns that feature,
# under D45's gen-timeout budgets, never here — `unit_build` builds exactly
# one binary per call and nothing in this file spawns a second compiler.
#
# Usage (source once, per script):
#   . "$ROOT_DIR/tests/lib/unit_cc.sh"
#   unit_build "$WORKDIR/mycheck" "$SCRIPT_DIR/mycheck.c" -ldl
#
# Env: CC (resolved via cc_resolve.sh if unset), SANFLAGS (SAN-1, default
#      empty), LIBPCREC (default <root>/build/libpcrec.a).

UNIT_CC_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
. "$UNIT_CC_LIB_DIR/tests/lib/cc_resolve.sh"   # [MACPORT] a real GNU gcc

SANFLAGS="${SANFLAGS:-}"
LIBPCREC="${LIBPCREC:-$UNIT_CC_LIB_DIR/build/libpcrec.a}"

# unit_build <outbin> <src.c> [extra args...]
#
# Returns the compiler's own exit status. On failure the caller's own `bad`
# reports it; this function prints nothing on success (matching every
# existing build site's own `if ! "$CC" ...; then bad ...; fi` shape) so a
# caller's OWN error message — which names the check by file, not this
# helper by name — is what a reader sees.
unit_build() {
    local outbin="$1" src="$2"
    shift 2
    if [ ! -f "$LIBPCREC" ]; then
        echo "unit_build: $LIBPCREC not built — run 'make' first" >&2
        return 1
    fi
    "$CC" -O1 -g -std=gnu11 -Wall -Wextra -Werror \
        -I"$UNIT_CC_LIB_DIR/lib" -I"$UNIT_CC_LIB_DIR/src" $SANFLAGS \
        -o "$outbin" "$src" "$@" "$LIBPCREC"
}
