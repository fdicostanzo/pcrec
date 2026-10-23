#!/usr/bin/env bash
# tests/findall/run_findall_tests.sh -- `make test-findall`, the find-all
# iterator's section ([FINDALL-NEXT] I1, findall_iter.md §6.7):
#   1. the answer differential (run_iter_diff.sh over cells.tsv): every group
#      on auto, --engine=vm and --engine=dfa, against libpcre2's global loop,
#      with the state-machine arms iter_drv.c runs on every subject;
#   2. the ASan cells (IC6): the retry shapes (a DFA notempty root, a VM
#      accept guard, \K, a compound shell) and a -futf-check utf8 group,
#      artifact and driver built with AddressSanitizer + UBSan, every region
#      the iterator reads or writes heap-backed by the driver.
#   3. (I4) run_one_body.sh: <p>__one's body is the pinned text (iteropt2).
# The `mg` corpus (global.rxt) rides test-corpus like every other .rxt file.
# env: as run_iter_diff.sh; ASAN=0 skips part 2 (a build without libasan).
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fail=0
# exit 77 = no libpcre2 oracle: the whole section SKIPS, loudly, with its own
# trailer (PC-3's shape), never a PASS with one check
bash "$SCRIPT_DIR/run_iter_diff.sh" "$SCRIPT_DIR/cells.tsv"
rc=$?
if [ "$rc" -eq 77 ]; then
    echo "SKIP: test-findall (no libpcre2 oracle; the iterator differential, the ASan cells and the one-body check did not run)"
    echo "checks passed: 0"; echo "checks failed: 0"; echo "checks skipped: 1"
    exit 0
fi
[ "$rc" -eq 0 ] || fail=1
bash "$SCRIPT_DIR/run_one_body.sh" || fail=1

if [ "${ASAN:-1}" = "1" ]; then
    WORK="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-findall-asan.XXXXXX")"
    trap 'rm -rf "$WORK"' EXIT
    awk -F'\t' '/^#/ {next}
        ($1 == "byte" && $2 == "" && ($3 == "x*|y" || $3 == "(a)|b*" || $3 == "a\\K|b" ||
                                       $3 == "^\\s*|\\s*$" || $3 == "(?:^|,)([^,]*)" ||
                                       $3 == "(a)(b)?(c)?" || $3 == "(a)(b)?(c)?(d)?(e)?(f)?(g)?(h)?(i)?(j)?")) ||
        ($1 == "utf8" && $2 == "-futf-check" && $3 == "x*|.")' \
        "$SCRIPT_DIR/cells.tsv" > "$WORK/asan.tsv"
    if ! printf 'int main(void){return 0;}\n' | "${CC:-cc}" -fsanitize=address -x c - -o "$WORK/probe" 2>/dev/null; then
        echo "SKIP: findall: the compiler cannot build -fsanitize=address; the ASan cells did not run" >&2
        asan_skipped=1
    else
        GENCFLAGS="-O1 -g -std=gnu11 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer" \
        ARMS="auto vm" MIN_GROUPS=10 MIN_RETRY=10 ASAN_OPTIONS=detect_leaks=1 \
        REACH_NEED="n3m4 split g2" \
            bash "$SCRIPT_DIR/run_iter_diff.sh" "$WORK/asan.tsv" || fail=1
    fi
fi
if [ "$fail" -ne 0 ]; then
    echo "FAIL: test-findall" >&2
    echo "checks passed: 0"; echo "checks failed: 1"
    exit 1
fi
if [ "${asan_skipped:-0}" = 1 ]; then
    echo "PASS (ASan half SKIPPED): test-findall"
    echo "checks passed: 1"; echo "checks failed: 0"; echo "checks skipped: 1"
    exit 0
fi
echo "PASS: test-findall"
echo "checks passed: 1"; echo "checks failed: 0"
