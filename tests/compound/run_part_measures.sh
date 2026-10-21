#!/usr/bin/env bash
# tests/compound/run_part_measures.sh -- [MEASURE-SET] a compound's parts read
# P's measurement set, and the shell's MEASURES stamp is the union over P and
# its parts (docs/spec/measures.md §4¶3, §5¶8; match_api.md §6.3.10¶13;
# lane partmeas). Sabotage rows S1291-S1294.
#
# A -DPCREC_CAND_TRACE build of this tree, the split witness '^\s+|\s+$'
# (every compile checked to stamp RX_COMPOUND "split"), two set arms:
#   H  the harness lever, `--harness=measures=FILE`, a synthetic set whose id
#      is not the build's default -- the arm where a part that resolves its
#      own set reads a DIFFERENT one (the default);
#   F  the shipped `--measures=FILE`, a copy of the committed store set -- the
#      arm where a part that re-reads the file gets an EQUAL set but not the
#      SAME one.
#   (A) INHERITANCE. PCREC_MF_MEAS_TRACE's MFMEAS records (one per kit art,
#       read off mf_art_begin's argument, memfn_sites.c): exactly one for P
#       (role `-`) and one per part (f, q). Every record names the arm's set
#       `id@rev:digest`, the expected text read from the FILE by awk (never
#       from pcrec), and every part's view and loaded-set addresses equal P's
#       (the same object, within the one process).
#   (B) THE UNION. No kit row reads a set key before the kit's B4, so the
#       consult is SYNTHETIC: PCREC_MF_MEAS_CONSULT=ROLE makes that part's
#       art read as consulted (trace build only). With f or q consulting, the
#       shell's RX_MEASURES and rx_info.measures are the arm's set; with no
#       consult, or a role no part has, both are "". Control: a pattern that
#       is no compound stays "" under a consult.
# The records' and the stamps' expected values are the FILE's header, so the
# check does not share a source with the code under test. Env: CC, KEEP=1.
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
W="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-partmeas.XXXXXX")"
[ "${KEEP:-0}" = 1 ] || trap 'rm -rf "$W"' EXIT
pass=0; fail=0
ok()  { echo "PASS: $*"; pass=$((pass + 1)); }
bad() { echo "FAIL: $*"; fail=$((fail + 1)); }
WIT='^\s+|\s+$'

TRB="$W/trace"
if ! "$TIMEOUT_BIN" 900 make -s -C "$ROOT_DIR" -j4 BUILD_DIR="$TRB" \
        CFLAGS="-O2 -g -DPCREC_CAND_TRACE" all > "$W/trace.log" 2>&1; then
    echo "FAIL: the -DPCREC_CAND_TRACE build failed: $(tail -3 "$W/trace.log" | tr '\n' ' ')"
    echo "run_part_measures: FAIL"
    exit 1
fi
H="$TRB/pcrec-harness"

printf '#section header\n#key\tvalue\nid\tpartmeas-synth\nrev\t7\nvalues_digest\t00000000deadbeef\n' > "$W/h.tsv"
# the build's default set (measure_store/DEFAULTS: `idk<TAB>id@rev`), found by
# its id and rev, so no box name is spelled here (C4's arch-noun class)
dset=$(awk -F'\t' 'NR == 1 {split($2, a, "@"); print a[1] "/" a[2] "/set.tsv"}' "$ROOT_DIR/measure_store/DEFAULTS")
cp "$ROOT_DIR/measure_store/$dset" "$W/f.tsv"
# a set's stamp text, from its header section alone
want() { awk -F'\t' '/^#section /{s = ($0 == "#section header")} s && $1 == "id" {i = $2}
                     s && $1 == "rev" {r = $2} s && $1 == "values_digest" {d = $2}
                     END {print i "@" r ":" d}' "$1"; }
stamp() { sed -n 's/^#define RX_MEASURES "\(.*\)"$/\1/p' "$1" | head -1; }
mirror() { sed -n 's/^    \.measures = "\(.*\)",$/\1/p' "$1" | head -1; }

# compile ARM-FLAG PATTERN CONSULT OUT: the records to OUT.rec, the C to OUT.c
compile() {
    PCREC_MF_MEAS_TRACE=1 PCREC_MF_MEAS_CONSULT="$3" "$TIMEOUT_BIN" 60 "$H" \
        --features all -p rx -o "$4.c" "$1" --pattern "$2" 2> "$4.err"
    local rc=$?
    grep '^MFMEAS	' "$4.err" > "$4.rec"
    return $rc
}

for arm in "H --harness=measures=$W/h.tsv $W/h.tsv" "F --measures=$W/f.tsv $W/f.tsv"; do
    set -- $arm
    name=$1 flag=$2 exp="$(want "$3")"
    case "$exp" in *@*:?*) ;; *) bad "$name: the set file's header gave no stamp text ('$exp')"; continue ;; esac
    o="$W/$name"
    if ! compile "$flag" "$WIT" "" "$o"; then
        bad "$name: the witness did not compile: $(head -1 "$o.err")"; continue
    fi
    if [ "$(sed -n 's/^#define RX_COMPOUND "\(.*\)"$/\1/p' "$o.c")" != split ]; then
        bad "$name: the witness is not a split compound: the arm measures nothing"; continue
    fi
    # (A) the population, then every record against the file and against P
    roles="$(cut -f2 "$o.rec" | sort | tr '\n' ' ')"
    if [ "$roles" = "- f q " ]; then ok "$name (A): one MFMEAS record for P and one per part (f, q)"
    else bad "$name (A): MFMEAS roles '$roles', not '- f q ' (one per art)"; fi
    pv="$(awk -F'\t' '$2 == "-" {print $4 "\t" $5}' "$o.rec")"
    nbad="$(awk -F'\t' -v e="$exp" -v pv="$pv" '$3 != e || ($2 != "-" && $4 "\t" $5 != pv)' "$o.rec" | wc -l | tr -d ' ')"
    if [ -n "$pv" ] && [ "$nbad" = 0 ]; then
        ok "$name (A): every art is handed $exp, each part P's own view and loaded set (the same objects)"
    else
        bad "$name (A): $nbad record(s) name another set than $exp or another object than P's: $(tr '\t\n' ' |' < "$o.rec")"
    fi
    # (B) the union
    for c in f q; do
        compile "$flag" "$WIT" "$c" "$o.$c" ||
            { bad "$name (B): consult=$c did not compile: $(head -1 "$o.$c.err")"; continue; }
        s="$(stamp "$o.$c.c")" m="$(mirror "$o.$c.c")"
        if [ "$s" = "$exp" ] && [ "$m" = "$exp" ]; then
            ok "$name (B): part $c consulting makes the shell stamp $exp (macro and rx_info.measures)"
        else
            bad "$name (B): part $c consulted, the shell stamps '$s' / rx_info '$m', not $exp (the union dropped a part, or the consult never reached its art)"
        fi
    done
    for c in "" x; do
        compile "$flag" "$WIT" "$c" "$o.n$c" ||
            { bad "$name (B): consult='$c' did not compile: $(head -1 "$o.n$c.err")"; continue; }
        s="$(stamp "$o.n$c.c")" m="$(mirror "$o.n$c.c")"
        if [ -z "$s" ] && [ -z "$m" ] && grep -q '^#define RX_MEASURES ""$' "$o.n$c.c"; then
            if [ -n "$c" ]; then what="a consult by '$c', a role no part has"; else what="no consult"; fi
            ok "$name (B): with $what the shell stamps \"\""
        else
            bad "$name (B): consult='$c' reached nothing, yet the shell stamps '$s' / rx_info '$m'"
        fi
    done
    compile "$flag" 'a(b|c)+d' q "$o.plain" ||
        { bad "$name (B): the control did not compile: $(head -1 "$o.plain.err")"; continue; }
    if grep -q '^#define RX_MEASURES ""$' "$o.plain.c" &&
       [ -z "$(sed -n 's/^#define RX_COMPOUND "\(.*\)"$/\1/p' "$o.plain.c" | grep -v '^none$')" ]; then
        ok "$name (B) control: a pattern that is no compound stamps \"\" under consult=q"
    else
        bad "$name (B) control: 'a(b|c)+d' under consult=q stamps '$(stamp "$o.plain.c")'"
    fi
done
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] && [ "$pass" -ge 14 ] && { echo "run_part_measures: PASS"; exit 0; }
[ "$pass" -ge 14 ] || echo "FAIL: population: $pass checks passed, under the floor 14, seven per arm (K35)"
echo "run_part_measures: FAIL"
exit 1
