#!/usr/bin/env bash
# docs/design/memfn/r17b_prime/fdb1/plant_fail.sh ARGV... -- a PLANT for shadow_census.py's
# K35 check (lane b4close2): stands in for the traced harness (PLANT_HARNESS), passes every
# call through, and FAILS (rc 2, one line on stderr) any call whose pattern argument equals
# PLANT_MATCH. Run shadow_census.py manifest --bin this-script with PLANT_* set: the run
# must exit 3 naming the lost compile, while the same population through the real harness
# exits 0 (the control).
for a in "$@"; do
    if [ "$a" = "${PLANT_MATCH:-}" ]; then echo "plant_fail: planted failure" >&2; exit 2; fi
done
exec "${PLANT_HARNESS:?}" "$@"
