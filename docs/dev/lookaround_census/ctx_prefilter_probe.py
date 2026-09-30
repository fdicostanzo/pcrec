#!/usr/bin/env python3
"""ctx_prefilter_probe.py PCREC TREE OUTDIR -- [CTX-PREFILTER] step 0
driver (plan.md's e79a53fd wording). Population: every pattern that is
STILL VM-routed after [UCP] U2 (tests/ucp/ctxnode_route.tsv, `default`
column == "vm" -- U2 already moved shape-(a) single-char lookarounds to
the DFA, so this is exactly "lookaround the ctx-node mechanism does not
already reach"), restricted to POSITIVE occurrences whose body is
MULTI-CHARACTER (shape b/c/d -- shape (a) is already handled by U2;
shape (e), which needs a capture/backref/nested-lookaround inside the
body, is out of scope: this tool's atom parser cannot resolve a
backreference's byteset and should not guess one).

For each occurrence:
  necessary_set = the FIRST byte set (lookahead: subject[p..] in L.Sigma*)
                  or LAST byte set (lookbehind: subject[..p] in Sigma*.L)
                  a matcher MUST see -- lac_engine.body_first_set /
                  body_last_set, the loose (ranged-quantifier-capable)
                  parser, walking "skip past every optional atom, stop at
                  the first mandatory one" (None if the body can match
                  zero-width at all -- reported separately, NOT folded
                  into "wide").
  narrow        = size(necessary_set) <= 8 (brief's own threshold), OR
                  the set does NOT already contain (is not a superset of)
                  the ADJACENT consuming atom's own byteset in the outer
                  pattern (best-effort: only computed when that adjacent
                  text is itself one simple, unquantified-optional atom;
                  "n/a" otherwise, not guessed).
  tightening    = an INDEPENDENCE-MODEL estimate on a representative
                  subject (APPROACH.md's own prose, ~21 KB, byte
                  encoding, stated here rather than the bench's subject
                  generators -- this population has only 4 bench rows
                  after the shape/polarity filter, all url/date-ish
                  capability patterns already read narrowly by
                  inspection; the corpus's own prose file is the more
                  representative "ordinary text" sample for a NARROW
                  literal-byte-selectivity question and needs no
                  checkout of pcrec-bench): selectivity(today's compiled
                  REQ_BYTE/REQ_RUN condition) * selectivity(necessary_set
                  alone) on the SAME subject, reported as a MODEL, not a
                  joint positional measurement (the two conditions sit at
                  different pattern offsets; this tool does not compute
                  the joint fraction at the correct relative offset --
                  named as the gap a real implementation's own evidence
                  would need to close).
"""
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import lac_engine as L
import shape_classify as sc

PCREC, TREE, OUTDIR = sys.argv[1:4]
ROUTE_TSV = os.path.join(TREE, "tests", "ucp", "ctxnode_route.tsv")
SUBJECT_PATH = os.path.join(TREE, "APPROACH.md")


def load_vm_routed():
    rows = []
    with open(ROUTE_TSV, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 6:
                continue
            rid, enc, flags, default, denied, pat = parts[:6]
            if default == "vm":
                rows.append(dict(id=rid, enc=enc, pattern=pat))
    return rows


def req_byte_set(pattern_text, enc):
    """Compiles pattern_text at default (auto) engine and reads back the
    emitted RX_REQ_BYTE (a single required byte value, decimal, or "none")
    -- today's own necessary-byte prefilter fact, read from the SAME
    artifact the hybrid ships, not re-derived."""
    with tempfile.TemporaryDirectory() as td:
        out_c = os.path.join(td, "out.c")
        cmd = [PCREC, "--features", "all", "-e", enc, "-o", out_c, "--pattern", pattern_text]
        r = subprocess.run(["timeout", "10"] + cmd, capture_output=True, text=True)
        if r.returncode != 0:
            return None, r.stderr.strip()
        src = open(out_c).read()
    m = re.search(r'#define RX_REQ_BYTE "(\d+|none)"', src)
    if not m or m.group(1) == "none":
        return None, "RX_REQ_BYTE none"
    return int(m.group(1)), ""


def selectivity(subject, byteset):
    if byteset is None:
        return None
    if not byteset:
        return 0.0
    hits = sum(1 for b in subject if b in byteset)
    return hits / len(subject)


def adjacent_atom_set(pattern_bytes, span_start, span_end, direction):
    """Best-effort byteset of the SINGLE simple atom immediately BEFORE
    (direction='before', for a lookbehind) or AFTER (direction='after',
    for a lookahead) the occurrence's construct span, for the redundancy
    half of `narrow`. Returns None if that neighbor is not resolvable as
    one simple atom (a group, another lookaround, end of pattern, etc.)
    -- "n/a", never guessed."""
    if direction == "after":
        try:
            fbs, lbs, mand, _ = L._parse_atom_loose(pattern_bytes, span_end, len(pattern_bytes))
            return fbs if mand else None
        except (L.Unresolvable, IndexError):
            return None
    else:
        try:
            seq, stop = L.parse_seq_loose(pattern_bytes, 0, span_start)
        except (L.Unresolvable, IndexError):
            return None
        if stop != span_start or not seq:
            return None
        fbs, lbs, mand = seq[-1]
        return lbs if mand else None


def main():
    subject = open(SUBJECT_PATH, "rb").read()
    rows = load_vm_routed()
    print("VM-routed rows (post-U2): %d" % len(rows), file=sys.stderr)

    results = []
    skipped = []
    req_cache = {}
    for r in rows:
        pat_text = r["pattern"]
        pat_bytes = pat_text.encode("utf-8", "surrogateescape")
        occs = sc.classify_pattern(pat_bytes)
        if not occs:
            continue
        for occ in occs:
            if occ["polarity"] != "+" or occ["shape"] not in ("b", "c", "d"):
                continue
            branches, resolved = L.try_parse_body_loose(occ["body"])
            if not resolved:
                skipped.append((r["id"], occ["kind"], "loose-parser unresolved: %r" % occ["body"]))
                continue
            if occ["kind"] == "lookahead":
                nec = L.body_first_set(branches)
            else:
                nec = L.body_last_set(branches)
            if nec is None:
                results.append(dict(id=r["id"], kind=occ["kind"], shape=occ["shape"],
                                     body=occ["body"].decode("utf-8", "backslashreplace"),
                                     necessary_size="n/a-zero-width-possible", narrow="n/a",
                                     redundant="", tighten_today="", tighten_new="", note=""))
                continue
            size = len(nec)
            narrow_by_size = size <= 8
            span = L.construct_span(pat_bytes, occ["offset"])
            adj = adjacent_atom_set(pat_bytes, span[0], span[1],
                                     "after" if occ["kind"] == "lookahead" else "before")
            if adj is None:
                redundant = "n/a"
                narrow = narrow_by_size
            else:
                redundant_bool = adj <= nec  # existing consuming class already implies the condition
                redundant = "yes" if redundant_bool else "no"
                narrow = narrow_by_size or not redundant_bool

            key = (pat_text, r["enc"])
            if key not in req_cache:
                req_cache[key] = req_byte_set(pat_text, r["enc"])
            req_byte, req_err = req_cache[key]
            req_bs = frozenset({req_byte}) if req_byte is not None else None
            sel_today = selectivity(subject, req_bs)
            sel_new = selectivity(subject, nec)
            tighten_model = (sel_today * sel_new) if (sel_today is not None and sel_new is not None) else None

            results.append(dict(
                id=r["id"], kind=occ["kind"], shape=occ["shape"],
                body=occ["body"].decode("utf-8", "backslashreplace"),
                necessary_size=size, narrow=narrow, redundant=redundant,
                sel_today="%.4f" % sel_today if sel_today is not None else "n/a(%s)" % req_err,
                sel_new="%.4f" % sel_new,
                tighten_model="%.6f" % tighten_model if tighten_model is not None else "n/a",
                note=""))

    os.makedirs(OUTDIR, exist_ok=True)
    cols = ("id", "kind", "shape", "body", "necessary_size", "narrow", "redundant",
            "sel_today", "sel_new", "tighten_model", "note")
    with open(os.path.join(OUTDIR, "ctx_prefilter.tsv"), "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in results:
            f.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    with open(os.path.join(OUTDIR, "ctx_prefilter_skipped.tsv"), "w") as f:
        f.write("id\tkind\treason\n")
        for rid, kind, reason in skipped:
            f.write("%s\t%s\t%s\n" % (rid, kind, reason))

    print("\n== results ==", file=sys.stderr)
    print("positive multi-char occurrences: %d, skipped (unresolved body): %d"
          % (len(results), len(skipped)), file=sys.stderr)
    zero_width = [r for r in results if r["necessary_size"] == "n/a-zero-width-possible"]
    sized = [r for r in results if isinstance(r["necessary_size"], int)]
    print("zero-width-possible (no sound necessary byte): %d" % len(zero_width), file=sys.stderr)
    print("with a computable necessary set: %d" % len(sized), file=sys.stderr)
    if sized:
        narrow_n = sum(1 for r in sized if r["narrow"] is True)
        print("NARROW (size<=8 or not-redundant): %d / %d (%.1f%%)"
              % (narrow_n, len(sized), 100.0 * narrow_n / len(sized)), file=sys.stderr)
        by_kind = {}
        for r in sized:
            by_kind.setdefault(r["kind"], []).append(r)
        for kind, rs in sorted(by_kind.items()):
            sizes = [r["necessary_size"] for r in rs]
            print("  %s n=%d size(min/mean/max)=%d/%.1f/%d narrow=%d"
                  % (kind, len(rs), min(sizes), sum(sizes) / len(sizes), max(sizes),
                     sum(1 for r in rs if r["narrow"])), file=sys.stderr)


if __name__ == "__main__":
    main()
