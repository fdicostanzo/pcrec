#!/usr/bin/env bash
# tests/memfn/run_purity_reach.sh — THE PURITY HARNESS's per-row REACH table
# (span_pick unit 1d fix, review 2026-11-05-r1 F1; run by run_finder.sh).
#
# For every row of tests/memfn/purity_rows.tsv: a COPY of memfn/src has that
# row DROPPED unconditionally (window.c, one text replaced, exactly once), is
# built with the fixture driver, and its `--purity-control` print is compared
# with the unplanted build's. REACH rows must MOVE some reply (the harness
# sites reach the row); UNREACHED rows must stay equal (a row that cannot
# move a reply by construction, with its reason). Either deviation is red.
# The table's ids are also held EXACTLY to window.c's row ids (the
# population): a new row without a line here reads red.
#
# usage: run_purity_reach.sh ROOT WORK CC FX     (FX: the unplanted driver)
# Prints `ok`/`FAIL` lines and `checks passed:`/`checks failed:` counts.
set -u
ROOT=$1 WORK=$2 CC=$3 FX=$4
TSV="$ROOT/tests/memfn/purity_rows.tsv"
W="$WORK/preach"
mkdir -p "$W/obj"
tp=0 tf=0
ok()   { echo "ok   purity reach: $1"; tp=$((tp + 1)); }
fail() { echo "FAIL: purity reach: $1"; tf=$((tf + 1)); }

# THE POPULATION: window.c's row ids, found in its tables.
win="$ROOT/memfn/src/window.c"
{ grep -oE 'WF_CT_A\([a-z_]+, *"[^"]+"' "$win" | sed 's/.*"\(.*\)"/\1/'
  grep -oE 'WF_CT_M\([a-z_]+, *"[^"]+"' "$win" | sed 's/.*"\(.*\)"/\1/'
  grep -oE '^    \{ [0-9], "C-[^"]+"' "$win" | sed 's/.*"\(.*\)"/\1/'
} | sort > "$W/ids.src"
grep -v '^#' "$TSV" | cut -f1 | grep -v '^+' | sort > "$W/ids.tsv"
if [ -s "$W/ids.src" ] && cmp -s "$W/ids.src" "$W/ids.tsv"; then
    ok "the table covers exactly window.c's $(wc -l < "$W/ids.src") rows"
else
    fail "purity_rows.tsv and window.c's rows differ: $(diff "$W/ids.src" "$W/ids.tsv" | grep '^[<>]' | tr '\n' ' ')"
fi

"$FX" --purity-control > "$W/base.ctl" 2>&1
[ -s "$W/base.ctl" ] || fail "the unplanted control printed nothing"

# the kit built once; a plant rebuilds window.c only
mkdir -p "$W/src"
cp "$ROOT"/memfn/src/*.c "$ROOT"/memfn/src/*.h "$ROOT"/memfn/src/*.def "$W/src/"
built=1
for s in "$W"/src/*.c; do
    "$CC" -std=gnu11 -O1 -I"$ROOT/memfn/include" -I"$W/src" -c -o "$W/obj/$(basename "${s%.c}").o" "$s" || built=0
done
"$CC" -std=gnu11 -O1 -I"$ROOT/memfn/include" -c -o "$W/fixture.o" "$ROOT/tests/memfn/arm_fixtures.c" || built=0
[ "$built" -eq 1 ] || { fail "the base kit and fixture do not build"; echo "checks passed: $tp"; echo "checks failed: $tf"; exit 1; }

NEVER='static int pur_never_x(const wf_x *x) { (void)x; return 0; }
static int pur_never_d(const wf_dec *d) { (void)d; return 0; }'
while IFS=$'\t' read -r id old new status; do
    case "$id" in '#'*|'') continue ;; esac
    if [ "$old" = "-" ]; then
        case "$status" in UNREACHED*) ok "$id: ${status#UNREACHED }" ;; *) fail "$id: nothing to drop but status is not UNREACHED" ;; esac
        continue
    fi
    p="$W/p"; rm -rf "$p"; mkdir -p "$p"
    awk -v o="$old" -v n="$new" -v nv="$NEVER" '
        index($0, "static const wf_arow wf_arows[] = {") == 1 { print nv }
        { i = index($0, o); if (i) { $0 = substr($0, 1, i - 1) n substr($0, i + length(o)); hit++ } print }
        END { exit hit == 1 ? 0 : 3 }' "$win" > "$p/window.c"
    if [ $? -ne 0 ]; then fail "$id: its text does not occur exactly once in window.c"; continue; fi
    if ! "$CC" -std=gnu11 -O1 -I"$ROOT/memfn/include" -I"$W/src" -c -o "$p/window.o" "$p/window.c" 2>"$p/cc.log"; then
        fail "$id: the plant does not build"; continue
    fi
    objs=$(ls "$W"/obj/*.o | grep -v '/window\.o$')
    # shellcheck disable=SC2086
    if ! "$CC" -std=gnu11 -O1 "$W/fixture.o" $objs "$p/window.o" -o "$p/fx"; then fail "$id: the plant does not link"; continue; fi
    "$p/fx" --purity-control > "$p/ctl" 2>&1
    if cmp -s "$W/base.ctl" "$p/ctl"; then moved=0; else moved=1; fi
    case "$status" in
    REACH)      [ "$moved" -eq 1 ] && ok "$id: dropped, a reply moves" || fail "$id: dropped, NO reply moves (no harness site reaches the row)" ;;
    UNREACHED*) [ "$moved" -eq 0 ] && ok "$id: dropped, no reply moves, as declared (${status#UNREACHED })" || fail "$id: declared UNREACHED but a reply moves (update the table)" ;;
    *)          fail "$id: status '$status' is neither REACH nor UNREACHED" ;;
    esac
done < "$TSV"
echo "checks passed: $tp"
echo "checks failed: $tf"
[ "$tf" -eq 0 ]
