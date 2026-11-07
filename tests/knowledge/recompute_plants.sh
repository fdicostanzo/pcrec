#!/usr/bin/env bash
# tests/knowledge/recompute_plants.sh -- the recompute check's PLANTS
# (span_cards.md §9, unit S2e's rows S2964-S2974): each plant edits ONE
# scratch copy of the committed format-2 set, its PROVENANCE.md and its run
# record, and meas_recompute.py must FAIL or REFUSE it with the named reason.
# A CONTROL (the unmodified copy) must PASS first. Where a plant has to
# isolate one detector, the dependent copies are rewritten consistently (the
# record re-hashed into PROVENANCE.md and the header `run` value; the values
# digest re-computed with ks_ref.py when a digest-covered field moves).
#
#   recompute_plants.sh [ROOT]     ROOT defaults to this file's tree
#
# One line per row `<row> <S-id> DETECTED|UNDETECTED <reason seen>`, then
# `== recompute plants COMPLETE: rows=7 detected=D control=PASS|FAIL`;
# exit 0 iff every row is DETECTED and the control PASSes.
set -u
export LC_ALL=C

HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=${1:-$(cd "$HERE/../.." && pwd)}
SET_REL=measure_store/zen4-grid3/1
TMPROOT=${PCREC_TMPDIR:-/var/tmp/pcrec-$(id -un)}/scratch/memfn/s2e/recompute
mkdir -p "$TMPROOT" || exit 2
WORK=$(mktemp -d -p "$TMPROOT" plants.XXXXXX) || exit 2
[ -n "${KEEP:-}" ] || trap 'rm -rf -- "$WORK"' EXIT   # our own mktemp dir only
CHECK="$HERE/meas_recompute.py"
TO=$(command -v gnutimeout || command -v timeout)

# The edits, in python (stdlib + ks_ref.py and meas_recompute.py for the
# digest and the unit's median launch; nothing from the slot harness).
cat > "$WORK/plant.py" <<'EOF'
import hashlib, os, re, shutil, sys
sys.path.insert(0, sys.argv[1])
import ks_ref, meas_recompute as mr

def rd(p): return open(p, "rb").read()
def wr(p, b): open(p, "wb").write(b)

def recpath(prov):
    return mr.provenance_record(prov)[0]

def setup(src, dst, set_rel):
    os.makedirs(os.path.join(dst, set_rel))
    for f in ("set.tsv", "PROVENANCE.md"):
        shutil.copy(os.path.join(src, set_rel, f), os.path.join(dst, set_rel, f))
    rp = recpath(os.path.join(src, set_rel, "PROVENANCE.md"))
    os.makedirs(os.path.dirname(os.path.join(dst, rp)), exist_ok=True)
    shutil.copy(os.path.join(src, rp), os.path.join(dst, rp))

def edit_lines(path, fn):
    out, hits = [], 0
    for ln in rd(path).split(b"\n"):
        new = fn(ln)
        hits += new != ln
        out.append(new)
    if hits != 1 and fn.__name__ != "multi":
        sys.exit("plant edited %d lines of %s, want 1" % (hits, path))
    wr(path, b"\n".join(out))
    return hits

def field_edit(path, first, col, new):
    def f(ln):
        c = ln.split(b"\t")
        if c[0] == first:
            c[col] = new(c[col])
            return b"\t".join(c)
        return ln
    edit_lines(path, f)

def redigest(setf):
    d = ks_ref.digest(ks_ref.load(setf))
    field_edit(setf, b"values_digest", 1, lambda v: d.encode())

def rehash(dst, set_rel):
    setf = os.path.join(dst, set_rel, "set.tsv")
    prov = os.path.join(dst, set_rel, "PROVENANCE.md")
    old = mr.provenance_record(prov)[1].encode()
    new = hashlib.sha256(rd(os.path.join(dst, recpath(prov)))).hexdigest().encode()
    wr(prov, rd(prov).replace(old, new))
    field_edit(setf, b"run", 1, lambda v: v.replace(old, new))   # not digest-covered

def plant(name, dst, set_rel):
    setf = os.path.join(dst, set_rel, "set.tsv")
    prov = os.path.join(dst, set_rel, "PROVENANCE.md")
    rec = os.path.join(dst, recpath(prov))
    if name == "p":      # one row's noise_e6 +1, digest re-computed
        field_edit(setf, b"kit.find_byte.libc", 4, lambda v: str(int(v) + 1).encode())
        redigest(setf)
    elif name == "q":    # the unit's median-launch 1 Mi walk cell, +1 %
        c = mr.Checker(setf, prov, dst, "q")
        for step in (c.load_set, c.three_copies, c.read_record, c.read_cards,
                     c.read_cells, c.read_plan_jobs, c.base_rule, c.needed_cells,
                     c.estimate):
            step()
        v = c.pl[c.unit_key]["v"]
        la = v.index(mr.med(v)) + 1
        cid = ("J2.unit/%s/1048576/%d" % (c.unit_key, la)).encode()
        field_edit(setf, cid, 7, lambda x: str(int(x) * 101 // 100).encode())
    elif name == "w":    # the record edited after the set; nothing re-hashed
        edit_lines(rec, lambda ln: b"J3\tnever-ran\tfailed" if ln == b"J3\tran\t-" else ln)
    elif name == "x":    # j1_verdict c -> b, shas re-written consistently
        field_edit(rec, b"j1_verdict", 1, lambda v: b"b")
        rehash(dst, set_rel)
    elif name == "x2":   # launch 5's cell id names launch 4 (the id only)
        cid = b"J2.byte/kit.find_byte.libc/1048576/5"
        field_edit(setf, cid, 0, lambda v: v[:-1] + b"4")
    elif name == "x3":   # a find_hit libc row and its twin name base.walk
        key = b"kit.find_hit.libc.random.one.1024"
        def multi(ln):
            c = ln.split(b"\t")
            if len(c) == 8 and c[2] in (key, key + b"#b") and c[0].endswith(b"/base.libc"):
                c[0] = c[0][:-len(b"base.libc")] + b"base.walk"
                return b"\t".join(c)
            return ln
        n = edit_lines(setf, multi)
        if n != 14:
            sys.exit("x3 edited %d cells, want 14" % n)
    elif name == "x4":   # the header `run` sha edited only
        def flip(v):
            return v[:-1] + (b"0" if v[-1:] != b"0" else b"1")
        field_edit(setf, b"run", 1, flip)
    else:
        sys.exit("no plant " + name)

if sys.argv[2] == "setup":
    setup(sys.argv[3], sys.argv[4], sys.argv[5])
else:
    plant(sys.argv[3], sys.argv[4], sys.argv[5])
EOF

run_check() {  # DIR -> output on stdout, exit status of the check
    "$TO" 120 python3 -I "$CHECK" --set "$1/$SET_REL/set.tsv" \
        --provenance "$1/$SET_REL/PROVENANCE.md" --root "$1"
}

mk() {  # NAME -> a fresh scratch root holding the copies
    local d="$WORK/$1"
    python3 -I "$WORK/plant.py" "$HERE" setup "$ROOT" "$d" "$SET_REL" || return 1
    echo "$d"
}

ctl=FAIL
if d=$(mk control); then
    out=$(run_check "$d"); rc=$?
    if [ $rc -eq 0 ] && ! grep -q '^FAIL\|^REFUSED' <<<"$out" && grep -q '^PASS' <<<"$out"; then
        ctl=PASS
    else
        printf '%s\n' "$out" | grep '^FAIL\|^REFUSED' | head -3
    fi
fi
echo "control - $ctl"

det=0
while read -r row sid reason; do
    seen="(plant failed)"
    status=UNDETECTED
    if d=$(mk "$row") && python3 -I "$WORK/plant.py" "$HERE" plant "$row" "$d" "$SET_REL"; then
        out=$(run_check "$d"); rc=$?
        first=$(grep -m1 '^REFUSED\|^FAIL' <<<"$out")
        seen=${first:-"(none: exit $rc)"}
        if [ $rc -ne 0 ] && grep -q "^\(REFUSED: $reason \|FAIL: .* $reason: \)" <<<"$out"; then
            status=DETECTED
            det=$((det + 1))
            seen=$(grep -m1 "^\(REFUSED: $reason \|FAIL: .* $reason: \)" <<<"$out")
        fi
    fi
    echo "$row $sid $status ${seen:0:160}"
done <<'ROWS'
p S2964 ROW-MISMATCH
q S2965 ROW-MISMATCH
w S2970 RECORD-SHA
x S2971 J1-VERDICT
x2 S2972 ID-COLUMNS
x3 S2973 BASE-RULE
x4 S2974 THREE-COPY
ROWS

echo "== recompute plants COMPLETE: rows=7 detected=$det control=$ctl"
[ "$det" -eq 7 ] && [ "$ctl" = PASS ]
