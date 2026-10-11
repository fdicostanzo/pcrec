#!/bin/bash
# time_twins.sh — OWED (quiet slot only; NOT run by lane lrdfa). Interleaved
# best-of-R find-all timing of every lrdfa twin against its base on the
# bench's own throughput subjects (regenerated, sha-checked), pinned to one
# core, three interleaved repeats. Run check_twins.sh first (answers) and
# keep its log beside the timing. Every line carries walk_survey fatime.c's
# span checksum: a base/twin pair whose ck differs is void.
#   L=<scratch> REPO=<pcrec at main> CORE=12 R=7 time_twins.sh > times.txt
set -u
L=${L:?}; REPO=${REPO:?}; CORE=${CORE:-12}; R=${R:-7}
H=$(cd "$(dirname "$0")" && pwd); A=$L/art; T=$L/tw; B=$L/bench/bench
FT=$REPO/studies/walk_survey/fatime.c
bin() {  # bin LABEL SRC HDR [extra.c]
    local lab=$1 src=$2 hdr=$3; shift 3; local d=$T/time_$lab; mkdir -p $d
    cp "$hdr" $d/rx.h
    gcc -O2 -I$d -I$A -o $d/bin $FT "$src" "$@" || echo "BUILD-FAIL $lab" >&2; }
pairs=(
 "hex8.base|$A/capability__hex8-bounded.c|$A/capability__hex8-bounded.h|capability"
 "hex8.plain|$T/capability__hex8-bounded__plain.c|$A/capability__hex8-bounded.h|capability"
 "hex8.nostart|$T/capability__hex8-bounded__nostart.c|$T/capability__hex8-bounded__nostart.h|capability"
 "dbn.base|$A/capability__wild-waf-crs-942140-dbnames.c|$A/capability__wild-waf-crs-942140-dbnames.h|capability"
 "dbn.plain|$T/capability__wild-waf-crs-942140-dbnames__plain.c|$A/capability__wild-waf-crs-942140-dbnames.h|capability"
 "json.base|$A/capability__wild-codegrammar-json-constant.c|$A/capability__wild-codegrammar-json-constant.h|capability"
 "json.plain|$T/capability__wild-codegrammar-json-constant__plain.c|$A/capability__wild-codegrammar-json-constant.h|capability"
 "union.base|$A/capability__wild-waf-crs-942270-union-select.c|$A/capability__wild-waf-crs-942270-union-select.h|capability"
 "union.from_f|$T/capability__wild-waf-crs-942270-union-select__from_f.c|$T/capability__wild-waf-crs-942270-union-select__norun.h|capability"
 "union.from_m|$T/capability__wild-waf-crs-942270-union-select__from_m.c|$T/capability__wild-waf-crs-942270-union-select__norun.h|capability"
 "modi.base|$A/syntax__mod-i.c|$A/syntax__mod-i.h|syntax"
 "modi.k101|$T/syntax__mod-i__k101.c|$A/syntax__mod-i.h|syntax"
 "modi.nofold|$T/syntax__mod-i__nofold.c|$A/syntax__mod-i.h|syntax"
 "email.base|$A/capability__wild-validator-email-owasp.c|$A/capability__wild-validator-email-owasp.h|capability"
 "email.deferpre|$T/capability__wild-validator-email-owasp__deferpre.c|$A/capability__wild-validator-email-owasp.h|capability"
 "line80.base|$A/bounded__line-80.c|$A/bounded__line-80.h|bounded"
 "line80.land|$T/bounded__line-80__land.c|$A/bounded__line-80.h|bounded"
 "atl4096.base|$A/bounded__cls-atleast-4096.c|$A/bounded__cls-atleast-4096.h|bounded"
 "atl4096.land|$T/bounded__cls-atleast-4096__land.c|$A/bounded__cls-atleast-4096.h|bounded"
 "hbr.base|$A/capability__high-byte-run.c|$A/capability__high-byte-run.h|capability"
 "hbr.hiskip|$T/capability__high-byte-run__hiskip.c|$A/capability__high-byte-run.h|capability"
)
for p in "${pairs[@]}"; do IFS='|' read lab src hdr set <<<"$p"; bin $lab $src $hdr; done
bin concat.base $A/capability__wild-waf-crs-942360-concat-sqli.c $A/capability__wild-waf-crs-942360-concat-sqli.h
bin concat.split $H/split_rx.c $H/split_rx.h $T/split/su.c $T/split/sa.c
pairs+=("concat.base|||capability" "concat.split|||capability")
[ "${DRYRUN:-0}" = 1 ] && { echo "DRYRUN: built ${#pairs[@]} binaries"; exit 0; }
for rep in 1 2 3; do
  for p in "${pairs[@]}"; do IFS='|' read lab src hdr set <<<"$p"
    for s in $B/$set/throughput/*.bin; do
      printf "rep%d\t%s\t" $rep $lab; taskset -c $CORE $T/time_$lab/bin "$s" findall $R
    done
  done
done
