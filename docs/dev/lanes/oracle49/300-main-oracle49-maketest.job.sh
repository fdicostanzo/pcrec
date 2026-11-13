#!/usr/bin/env bash
# 300-main-oracle49-maketest: make + make test on worktrees/oracle49 (main 0c56b73cf) with every libpcre2
# differential pointed at the PCRE2 10.49 oracle build ([ORACLE-UPGRADE]); fails loudly if 10.49 is not what resolves.
set -u
TREE=/home/pcrec/projects/pcrec/worktrees/oracle49
D=/var/tmp/pcrec-pcrec/oracle/pcre2-10.49
OUT=/var/tmp/pcrec-pcrec/scratch/oracle49
export PKG_CONFIG_PATH=$D/install/lib/pkgconfig LD_LIBRARY_PATH=$D/install/lib
assert_1049() {
    v=$(bash -c ". '$TREE/tests/lib/resolve_pcre2.sh' 2>/dev/null; echo \"\${PCRE2_AVAILABLE:-0} \${PCRE2_VERSION:-} \${PCREC_PCRE2_PATH:-}\"")
    case "$v" in "1 10.49 $D/install/lib/"*) return 0 ;; esac
    echo "ORACLE49 ASSERT FAILED: resolver gave '$v', not 10.49 under $D" >&2; return 1
}
case "${1:-}" in
    --dry-run)
        [ -e "$TREE/.git" ] || { echo "no tree" >&2; exit 1; }
        assert_1049 || exit 1
        echo "would run in $TREE: make -j16; make -k -j16 -Otarget test (PKG_CONFIG_PATH/LD_LIBRARY_PATH -> $D/install)"
        echo "boxqueue: cap 5400"; echo "boxqueue: patience none"; echo "boxqueue: est 2400"
        echo "boxqueue: expect none reason=the job's rc is make test's rc (assert + make steps exit nonzero first)"
        exit 0 ;;
    --ready) exit 0 ;;
esac
mkdir -p "$OUT"
assert_1049 || exit 1
make -C "$TREE" -j16 >"$OUT/build.log" 2>&1 || { echo "build failed"; exit 1; }
make -C "$TREE" -k -j16 -Otarget test >"$OUT/test.make.log" 2>&1
rc=$?
echo "== oracle49 make test rc=$rc"
grep -h 'libpcre2 resolved' "$OUT/test.make.log" | sort | uniq -c
if grep 'libpcre2 resolved' "$OUT/test.make.log" | grep -qv 'resolved: 10.49 '; then
    echo "ORACLE49: a non-10.49 libpcre2 resolved during the run; result WORTHLESS"; exit 1
fi
grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' "$OUT/test.make.log" | sed 's/^/test-red: /'
exit "$rc"
