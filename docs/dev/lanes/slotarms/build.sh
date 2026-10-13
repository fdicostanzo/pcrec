#!/bin/bash
# slotarms/build.sh -- kit harness contract: OUT=<dir> bash build.sh. Produces
#   $OUT/bin/<cell>/<arm>/run SUBJFILE first|all     (the timed binary; slot25c drv.c method)
#   $OUT/bin/<cell>/<arm>/cnt SUBJFILE list first|all (counting twin: calls= matches= bytes= on stderr)
#   $OUT/subj/pc_*                                   (via gen_subj.py)
# One artifact per (pattern, engine arm) is built once and shared by that arm's cells (-first and -all).
# Needs pcrec: PCREC=/path/to/build/pcrec (default: first of ./build/pcrec, `command -v pcrec`).
# Compiles pinned to CPUS (default 12-13), -j2. Self-contained: spec and driver are embedded below.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${OUT:?set OUT}
PCREC=${PCREC:-$(ls ./build/pcrec 2>/dev/null || command -v pcrec)}
[ -x "$PCREC" ] || { echo "FATAL: set PCREC=/path/to/pcrec"; exit 1; }
CPUS=${CPUS:-12-13}; JOBS=${JOBS:-2}; CC=${CC:-gcc}
mkdir -p "$OUT/bin" "$OUT/subj" "$OUT/tmp/slotarms"; W=$OUT/tmp/slotarms; TMPDIR=$W; export TMPDIR
python3 -I "$HERE"/gen_subj.py "$OUT" || exit 1
cat > "$W/drv.c" <<'DRV_EOF'
/* slotarms driver: the kit harness's vdrv.c (= slot25c's drv.c) without the KEEP
 * branch, plus a `check` mode (no clock). Interface: drv SUBJECT_FILE [first|all] [check].
 * Timed: one line "matches=N hash=H ns/pass=X" (X = median of 7 rounds, each calibrated to >= 50 ms).
 * check: "matches=N hash=H first=S:E" (first = the span of the match from offset 0, or -1:-1). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>
#include <time.h>
extern int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
extern size_t rx_next_pos(const unsigned char *s, size_t n, size_t pos);
static uint64_t now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return (uint64_t)t.tv_sec*1000000000ull+t.tv_nsec;}
static int cmp(const void*a,const void*b){double x=*(double*)a,y=*(double*)b;return x<y?-1:x>y;}
static ptrdiff_t cp[64][2];
#ifdef CNT
static long ncalls;
static int rx_search_c(const unsigned char *s, size_t n, size_t f, ptrdiff_t (*c)[2]) { ncalls++; return rx_search(s, n, f, c); }
#define rx_search rx_search_c
#endif
/* one pass: `first` = one call from 0; `all` = match_api.md §3.1.3's find-all loop */
static long pass(const unsigned char *b, size_t n, int all, unsigned long *h)
{
    if (!all) { int r = rx_search(b, n, 0, cp); *h ^= r == 1 ? (unsigned long)cp[0][0] * 31u + cp[0][1] : 7u; return r == 1; }
    size_t p = 0; long k = 0;
    while (p <= n && rx_search(b, n, p, cp) == 1) {
        k++; *h = *h * 131u + (unsigned long)cp[0][0] * 31u + (unsigned long)cp[0][1];
        p = cp[0][1] > cp[0][0] ? rx_next_pos(b, n, (size_t)cp[0][1] - 1) : rx_next_pos(b, n, (size_t)cp[0][1]);
        if (cp[0][1] == cp[0][0] && (size_t)cp[0][1] >= n) break;
    }
    return k;
}
int main(int c, char **v)
{
#ifdef CNT   /* cnt SUBJECT list first|all: one counted pass, key=value line on stderr */
    if (c > 3 && !strcmp(v[2], "list")) {
        FILE *g = fopen(v[1], "rb"); if (!g) return 2;
        fseek(g, 0, 2); long gn = ftell(g); fseek(g, 0, 0); unsigned char *gb = malloc(gn + 1);
        if (fread(gb, 1, gn, g) != (size_t)gn) return 2;
        unsigned long gh = 0; long gm = pass(gb, gn, !strcmp(v[3], "all"), &gh);
        fprintf(stderr, "calls=%ld matches=%ld bytes=%ld\n", ncalls, gm, gn); return 0;
    }
#endif
    FILE *f = fopen(v[1], "rb"); int all = c > 2 && !strcmp(v[2], "all");
    if (!f) return 2;
    fseek(f, 0, 2); long n = ftell(f); fseek(f, 0, 0); unsigned char *b = malloc(n + 1);
    if (fread(b, 1, n, f) != (size_t)n) return 2;
    unsigned long h = 0; long m = pass(b, n, all, &h), it = 1; uint64_t t0;
    if (c > 3 && !strcmp(v[3], "check")) {
        ptrdiff_t s = -1, e = -1; if (rx_search(b, n, 0, cp) == 1) { s = cp[0][0]; e = cp[0][1]; }
        printf("matches=%ld hash=%lx first=%td:%td\n", m, h, s, e); return 0;
    }
    do { it *= 2; t0 = now(); unsigned long g = 0; for (long i = 0; i < it; i++) pass(b, n, all, &g); } while (now() - t0 < 50000000);
    double t[7];
    for (int k = 0; k < 7; k++) { unsigned long g = 0; t0 = now(); for (long i = 0; i < it; i++) pass(b, n, all, &g); t[k] = (double)(now() - t0) / it; }
    qsort(t, 7, sizeof t[0], cmp);
    printf("matches=%ld hash=%lx ns/pass=%.2f\n", m, h, t[3]);
    return 0;
}
DRV_EOF
cat > "$W/arms.spec" <<'SPEC_EOF'
# arm build spec, read by build.sh: cell-prefix<TAB>arm<TAB>family<TAB>pattern<TAB>pcrec flags ('-' = none)<TAB>want_engine<TAB>want_vm_prefilter ('-' = any)
p1	dfa	w2	[0-9][a-z]	-	dfa	-
p1	vm	w2	[0-9][a-z]	--engine=vm	vm	none
p2	hyb	w2	([0-9])[a-z]	-	vm	hybrid
p2	dfa	w2	([0-9])[a-z]	--engine=dfa --no-captures	dfa	-
p2	vm	w2	([0-9])[a-z]	--engine=vm	vm	none
p3	dfa	w5	[0-9]+[a-z]	-	dfa	-
p3	vm	w5	[0-9]+[a-z]	--engine=vm	vm	none
SPEC_EOF
: > "$W/jobs"
while IFS=$'\t' read -r p arm fam pat flags eng vmp; do
  case "$p" in '#'*|'') continue ;; esac
  d=$W/$p-$arm; mkdir -p "$d"; [ "$flags" = - ] && flags=
  # shellcheck disable=SC2086
  "$PCREC" $flags -p rx -o "$d/art.c" --pattern "$pat" || { echo "PCREC FAILED $p $arm"; exit 1; }
  echo "$CC -O2 -I$d -c $d/art.c -o $d/art.o && $CC -O2 -I$d -c $W/drv.c -o $d/drv.o && $CC -o $d/run $d/drv.o $d/art.o && $CC -O2 -DCNT -I$d -o $d/cnt $W/drv.c $d/art.c" >> "$W/jobs"
done < "$W/arms.spec"
tr '\n' '\0' < "$W/jobs" | taskset -c "$CPUS" xargs -0 -P "$JOBS" -I{} bash -c '{} 2>&1' || { echo "BUILD FAILED"; exit 1; }
# place the shared binaries under every cell that uses the arm
while IFS=$'\t' read -r cell arm role subj modes; do
  case "$cell" in '#'*|'') continue ;; esac
  mkdir -p "$OUT/bin/$cell/$arm"
  for f in run cnt art.c art.h; do cp "$W/${cell%-*}-$arm/$f" "$OUT/bin/$cell/$arm/$f"; done
done < "$HERE/arms.tsv"
echo "slotarms: built $(grep -vc '^#' "$W/arms.spec") artifacts under $OUT/bin"
