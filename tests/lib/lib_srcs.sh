# tests/lib/lib_srcs.sh — sourced, never run. THE ONE LIST of libpcrec's C
# sources for a test script that builds a compiler from source rather than
# linking build/libpcrec.a (a reference build, a TSan library, a scratch
# witness).
#
#   pcrec_lib_srcs ROOT    prints every .c under ROOT/src and, when ROOT has
#                          one, ROOT/memfn/src (the pcrec-memory-functions
#                          kit libpcrec links since [MEMFN] R4a), LC_ALL=C
#                          sorted, one per line. Returns 1, naming ROOT, when
#                          ROOT/src holds no source.
#
# WHY A HELPER. Each of these scripts used to spell `find "$ROOT/src" -name
# '*.c'` itself, and that line is a claim about the tree's SHAPE: the tree
# changed shape under it twice ([M5-SEAM]'s src/gen/enc/, [REVW.3]'s src/enc/
# and src/dump/; tests/thread/run_thread_tests.sh's header) and a third time
# at R4a, when the library's sources stopped being only src/. The Makefile's
# LIBSRCS + KITSRCS is the build's list; this is the scripts' — one function,
# so the next shape change is one edit.
#
# "When ROOT has one": a tree archived from a commit before R4a has no
# memfn/, and its src/ does not reference the kit. A tree that HAS the kit's
# caller (src/dump/axes_dump.c includes memfn.h) but was copied without
# memfn/ fails to LINK, loudly, on the missing pcrec_mf_* symbols — the
# [M5-SEAM] failure shape, never a silent build from a different source set.
#
# The kit's sources include their header by relative path, so a from-source
# build needs no -I beyond the -Ilib -Isrc it already passes.

pcrec_lib_srcs() {
    local root="$1" dirs list
    dirs=("$root/src")
    [ -d "$root/memfn/src" ] && dirs+=("$root/memfn/src")
    list="$(find "${dirs[@]}" -name '*.c' 2>/dev/null | LC_ALL=C sort)"
    if ! printf '%s\n' "$list" | grep -q "^$root/src/"; then
        echo "lib_srcs: no library sources under $root/src" >&2
        return 1
    fi
    printf '%s\n' "$list"
}
