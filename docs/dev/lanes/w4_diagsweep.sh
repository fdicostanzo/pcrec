#!/usr/bin/env bash
# Every CLI diagnostic item 5 could touch, plus a wide argv sweep.
B="$1"
run() { printf '### %s\n' "$*"; "$B" "$@" 2>&1; printf '[rc=%d]\n' "$?"; }
run --unroll=0 -- a
run --unroll=4097 -- a
run --unroll=abc -- a
run --unroll= -- a
run --unroll=+3 --count-groups -- 'a(b)'
run --vm-entry-shape=-1 -- a
run --vm-entry-shape=5 -- a
run --vm-entry-shape=x -- a
run --vm-entry-shape= --count-groups -- 'a(b)'
run --vm-entry-shape=2 --count-groups -- 'a(b)'
run --tune=bogus -- a
run --tune -- a
run --tune=-2 --count-groups -- 'a(b)'
run --engine=bogus -- a
run --engine= -- a
run --engine=auto --count-groups -- 'a(b)'
run --engine=dfa --count-groups -- 'a(b)'
run --engine=vm --count-groups -- 'a(b)'
run --step-budget=0 -- a
run --step-budget=-1 -- a
run --step-budget=abc -- a
run --step-budget= -- a
run --step-budget=7 --count-groups -- 'a(b)'
run --work-budget=0 -- a
run --work-budget=xyz -- a
run --work-budget= -- a
run --warn-emit-bytes= -- a
run --warn-emit-bytes=-1 -- a
run --warn-emit-bytes=abc -- a
run --warn-emit-bytes=0 --count-groups -- 'a(b)'
run --backtrack-frames=0 -- a
run --backtrack-frames=1000001 -- a
run --backtrack-frames=zz -- a
run --backtrack-frames= -- a
run --backtrack-frames=16 --count-groups -- 'a(b)'
run --encoding=bogus -- a
run -e bogus -- a
run --probe-ask bogus -- '\d'
run --probe-ask claim -- '\d'
run --probe-ask verdict -- '\d'
run --probe-ask result -- '\d'
run --flavour bogus --list-syntax
run --flavour pcre2 --count-groups -- 'a(b)'
run --features bogus_mod -- a
run --bogus-flag -- a
run -x -- a
run -- -a
run --max-emit-bytes=1 -- a
run --max-emit-bytes=abc -- a
run --unroll
run --lib-path
run --source
run --target
run --list-source
run --probe-ask
run --features
run --explain
run --flavour
run -o
run -p
run -e
run a b
run --help
