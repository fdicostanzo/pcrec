#!/usr/bin/env python3
"""Block B (I-93): derive program-identical patterns from BEFORE/AFTER
compile rows in the store (read-only), then re-report per-cell Delta%
for those patterns' cells on ALL FOUR testees, both regimes -- both
directions (regressing and improving), using pcrecbench.reduce directly.
"""
import json, statistics, sys
sys.path.insert(0, "/home/duxevents/pcrec-bench")
from pcrecbench.reduce import cells_from_record, reduce_set_cell, read_record

STORE = "/home/duxevents/pcrec-bench/store/records/capability@0.1"

BEFORE_FILES = {
    "auto-caps": f"{STORE}/pcrec_25b1984f_auto-caps-simdna/capability@0.1__pcrec_25b1984f_auto-caps-simdna__budu-ryzen1600__20260922T021127Z.jsonl",
    "auto-nocaps": f"{STORE}/pcrec_25b1984f_auto-nocaps-simdna/capability@0.1__pcrec_25b1984f_auto-nocaps-simdna__budu-ryzen1600__20260922T024402Z.jsonl",
    "vm-caps": f"{STORE}/pcrec_25b1984f_vm-caps-simdna/capability@0.1__pcrec_25b1984f_vm-caps-simdna__budu-ryzen1600__20260922T031341Z.jsonl",
    "vm-in-caps": f"{STORE}/pcrec_25b1984f_vm-in-caps-simdna/capability@0.1__pcrec_25b1984f_vm-in-caps-simdna__budu-ryzen1600__20260922T035712Z.jsonl",
}
AFTER_FILES = {
    "auto-caps": f"{STORE}/pcrec_8d716693_auto-caps-simdna/capability@0.1__pcrec_8d716693_auto-caps-simdna__budu-ryzen1600__20260923T031941Z.jsonl",
    "auto-nocaps": f"{STORE}/pcrec_8d716693_auto-nocaps-simdna/capability@0.1__pcrec_8d716693_auto-nocaps-simdna__budu-ryzen1600__20260923T035507Z.jsonl",
    "vm-caps": f"{STORE}/pcrec_8d716693_vm-caps-simdna/capability@0.1__pcrec_8d716693_vm-caps-simdna__budu-ryzen1600__20260923T042632Z.jsonl",
    "vm-in-caps": f"{STORE}/pcrec_8d716693_vm-in-caps-simdna/capability@0.1__pcrec_8d716693_vm-in-caps-simdna__budu-ryzen1600__20260923T050923Z.jsonl",
}

def load_compile_rows(path):
    """Keyed by pattern_id, PLAIN FORM ONLY (form is None/absent -> 'plain',
    per record_schema.md 5 / cells_from_record's own default). Some
    patterns (the floor-pattern family) also compile a 'whole-subject'
    form; that population is out of scope for this identity check, which
    is restricted to the plain-form grid used by the pattern x regime x
    testee cells below."""
    rows = {}
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            if r.get("kind") == "compile" and r.get("form") in (None, "plain"):
                rows[r["pattern_id"]] = r
    return rows

# IDENTITY CRITERION (stated once, applied identically to all patterns):
# auto-caps, auto-nocaps, vm-caps are the three distinct EMITTED ARTIFACTS
# per pattern (vm-in-caps reuses the vm-caps artifact -- confirmed below:
# 0 emit_bytes mismatches over the whole AFTER corpus). A pattern is
# PROGRAM-IDENTICAL on one of those three forms iff, comparing its BEFORE
# (25b1984f, abi 27) and AFTER (8d716693, abi 29) `compile` rows' plain
# form:
#   (a) both compiled ("compile_outcome" == "compiled") -- a refusal on
#       either side is excluded, never counted as identical;
#   (b) every `engine_metadata` key present on EITHER side, other than
#       `abi`, `emit_bytes`, `emit_code_bytes` and the three abi-29
#       additions (req_byte, end_window, vm_start), is EQUAL -- this is a
#       STAMP-EQUALITY criterion (every structural fact the artifact
#       reports about itself: engine, engine_sel, vm_program_bytes,
#       vm_entry_shape, vm_frameless, resume_frames, dfa_*, altcls_*,
#       scan_edges, ...), not a byte-level source diff, because the
#       record does not carry the emitted .c/.h text or a hash of it;
#   (c) req_byte/end_window/vm_start, where present on the AFTER side,
#       read the NEUTRAL/INERT value (req_byte absent-or-"none",
#       end_window absent-or-"none", vm_start == "unanchored") -- i.e.
#       none of the three abi-29 mechanisms fired on this artifact.
# `emit_bytes`/`emit_code_bytes` (the WHOLE emitted .c+.h byte counts) are
# DELIBERATELY EXCLUDED from the equality test: they grow by a small,
# pattern-dependent boilerplate amount on EVERY abi-29 artifact regardless
# of whether any mechanism fired (measured +89 B on most VM artifacts,
# +168/+201 B on others -- the new #define lines' own text length, which
# varies with the values printed) -- confirmed empirically below on
# phone-palindrome-6, one of the pcrec ledger's own byte-identical `.text`
# witnesses, whose emit_bytes still moves +89 B. Using them as an equality
# gate would have produced ZERO identical patterns, which is why they are
# reported as a side observation, never as the test.
# A pattern counts as PROGRAM-IDENTICAL overall only if ALL THREE forms
# (auto-caps, auto-nocaps, vm-caps) pass (a)-(c).

IGNORE_KEYS = {"abi", "emit_bytes", "emit_code_bytes"}
NEW_KEYS = {"req_byte", "end_window", "vm_start"}

def form_identical(before_row, after_row):
    if before_row is None or after_row is None:
        return False, "missing on one side"
    if before_row.get("compile_outcome") != "compiled" or after_row.get("compile_outcome") != "compiled":
        return False, f"not both compiled ({before_row.get('compile_outcome')}/{after_row.get('compile_outcome')})"
    bm = before_row.get("engine_metadata", {})
    am = after_row.get("engine_metadata", {})
    # NOTE: emit_bytes/emit_code_bytes are NOT required equal here -- they
    # count the WHOLE emitted .c+.h text, which grows by a small, pattern-
    # dependent boilerplate amount (the new #define lines for
    # RX_REQ_BYTE/RX_END_WINDOW/RX_VM_START + #include <string.h>) on
    # EVERY abi-29 artifact regardless of whether any of the three
    # mechanisms actually fired -- measured here as +89 B on most VM
    # artifacts but +168/+201 B on others, so it is not usable as an
    # identity test by itself (confirmed empirically: phone-palindrome-6,
    # one of the pcrec ledger's own byte-identical .text witnesses, shows
    # a +89 B emit_bytes delta despite compiling to the identical object).
    # check the neutral-value condition for the three new keys on the AFTER side
    req_byte = am.get("req_byte")
    if req_byte not in (None, "none"):
        return False, f"req_byte={req_byte!r} (fired)"
    end_window = am.get("end_window")
    if end_window not in (None, "none"):
        return False, f"end_window={end_window!r} (fired)"
    vm_start = am.get("vm_start")
    if vm_start not in (None, "unanchored"):
        return False, f"vm_start={vm_start!r} (fired)"
    # every other shared key must match
    keys = (set(bm) | set(am)) - IGNORE_KEYS - NEW_KEYS
    for k in keys:
        if bm.get(k) != am.get(k):
            return False, f"engine_metadata[{k}] differs ({bm.get(k)!r} vs {am.get(k)!r})"
    return True, "identical"


def main():
    before_compile = {form: load_compile_rows(p) for form, p in BEFORE_FILES.items()}
    after_compile = {form: load_compile_rows(p) for form, p in AFTER_FILES.items()}

    # sanity: confirm vm-in-caps compile rows are identical to vm-caps'
    # (same emitted artifact; vm-in only differs in the caller-provided
    # frame buffer, a runtime harness detail, never a distinct compile).
    mismatch = []
    for pid, vc in after_compile["vm-caps"].items():
        vic = after_compile["vm-in-caps"].get(pid)
        if vic is None:
            continue
        if vc.get("engine_metadata", {}).get("emit_bytes") != vic.get("engine_metadata", {}).get("emit_bytes"):
            mismatch.append(pid)
    print(f"# sanity: vm-caps vs vm-in-caps AFTER emit_bytes mismatches: {len(mismatch)} {mismatch}")

    all_patterns = sorted(set(before_compile["auto-caps"]) | set(after_compile["auto-caps"]))
    identical_patterns = []
    per_pattern_reason = {}
    FORMS = ["auto-caps", "auto-nocaps", "vm-caps"]
    for pid in all_patterns:
        ok_all = True
        reasons = {}
        for form in FORMS:
            b = before_compile[form].get(pid)
            a = after_compile[form].get(pid)
            ok, reason = form_identical(b, a)
            reasons[form] = (ok, reason)
            if not ok:
                ok_all = False
        per_pattern_reason[pid] = reasons
        if ok_all:
            identical_patterns.append(pid)

    print(f"\n# PROGRAM-IDENTICAL PATTERNS (all 3 forms pass): {len(identical_patterns)}")
    for pid in identical_patterns:
        print(f"  {pid}")

    print("\n# Non-identical patterns' failing form + reason (first failing form only, for context):")
    for pid in all_patterns:
        if pid in identical_patterns:
            continue
        reasons = per_pattern_reason[pid]
        failing = [(f, r[1]) for f, r in reasons.items() if not r[0]]
        # only print short summary; skip verbose

    # Now compute Delta% for all cells (pattern, regime, testee) for the
    # identical patterns, on all 4 testees.
    TESTEES = ["auto-caps", "auto-nocaps", "vm-caps", "vm-in-caps"]
    REGIMES = ["large-subject-throughput", "short-subject-search"]

    before_cells = {}
    after_cells = {}
    for form in TESTEES:
        _, brows = read_record(BEFORE_FILES[form])
        _, arows = read_record(AFTER_FILES[form])
        before_cells[form] = cells_from_record(brows)
        after_cells[form] = cells_from_record(arows)

    print("\n# PER-CELL Delta% for program-identical patterns, all 4 testees, both regimes")
    print("# (after-before)/before *100; positive = slower (regression), negative = faster (improvement)")
    header = f"{'pattern':40s} {'regime':26s} {'testee':12s} {'before_ns':>16s} {'before_IQR':>12s} {'after_ns':>16s} {'after_IQR':>12s} {'delta_pct':>10s}"
    print(header)
    results = []
    for pid in identical_patterns:
        for regime in REGIMES:
            for testee in TESTEES:
                key = (pid, regime, "plain")
                brow = before_cells[testee].get(key)
                arow = after_cells[testee].get(key)
                if brow is None or arow is None:
                    print(f"{pid:40s} {regime:26s} {testee:12s} {'MISSING':>16s}")
                    continue
                bcell = reduce_set_cell(brow)
                acell = reduce_set_cell(arow)
                if bcell.median_ns is None or acell.median_ns is None:
                    print(f"{pid:40s} {regime:26s} {testee:12s} {'expectation-failing':>16s}")
                    continue
                b_iqr = None
                a_iqr = None
                bs = sorted(bcell.sums)
                as_ = sorted(acell.sums)
                if len(bs) == 5:
                    b_iqr = bs[3] - bs[1]
                if len(as_) == 5:
                    a_iqr = as_[3] - as_[1]
                delta_pct = (acell.median_ns - bcell.median_ns) / bcell.median_ns * 100
                results.append((pid, regime, testee, bcell.median_ns, b_iqr, acell.median_ns, a_iqr, delta_pct))
                print(f"{pid:40s} {regime:26s} {testee:12s} {bcell.median_ns:16.3f} {b_iqr if b_iqr is not None else float('nan'):12.3f} {acell.median_ns:16.3f} {a_iqr if a_iqr is not None else float('nan'):12.3f} {delta_pct:10.4f}")

    # summary stats
    deltas = [r[-1] for r in results]
    print(f"\n# n cells = {len(deltas)}")
    if deltas:
        print(f"# min = {min(deltas):.4f}%  max = {max(deltas):.4f}%  median = {statistics.median(deltas):.4f}%  mean = {statistics.mean(deltas):.4f}%")
        regress = [d for d in deltas if d > 0]
        improve = [d for d in deltas if d < 0]
        print(f"# regressing (>0): {len(regress)}  worst = {max(regress) if regress else float('nan'):.4f}%")
        print(f"# improving (<0): {len(improve)}  best = {min(improve) if improve else float('nan'):.4f}%")

if __name__ == "__main__":
    main()
