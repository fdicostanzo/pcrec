#!/usr/bin/env python3
"""lens10kit MEASUREMENT part 2 -- the shape the emitters ACTUALLY have.

Part 1 (count_runs.py) answers lens 2's literal question: runs of >= 5
CONSECUTIVE sb_* calls emitting a contiguous literal block. Part 2 asks the
question that question was a proxy for, because the emitters already merge
such runs into ONE sb_printf with a multi-line concatenated format:

  per sb_printf/sb_puts CALL, how big is the literal block it carries, how
  many prefix substitutions does it perform, and could pcrec_enc_emit_text
  ($-template) replace it AS IT STANDS?

Classification of one call's format literal:
  LIT       - no conversions at all           -> $-template trivially
  PFX-ONLY  - every conversion is %s and every vararg is a prefix expression
              -> $-template EXACTLY replaces it, byte for byte
  MIXED     - carries at least one non-prefix substitution -> a $-template
              CANNOT replace it; the primitive has no second placeholder and
              no formatting.  This is the decisive bucket.

Also reproduces lens 2's `%s_` substitution count and splits it by bucket.
"""
import re, sys, json, collections
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from count_runs import (strip_map, find_calls, split_args, is_string_literal,
                        literal_body, conversions, PREFIX_EXPRS)
from decompose_652 import expand_macros


def unescape_len(body):
    """Approximate emitted byte count of a C string literal body."""
    n, i = 0, 0
    while i < len(body):
        if body[i] == "\\":
            i += 2
            n += 1
        else:
            i += 1
            n += 1
    return n


def main():
    paths = sys.argv[1:]
    grand = {}
    big = []
    for path in paths:
        src = open(path, encoding="utf-8", errors="replace").read()
        kind = strip_map(src)
        calls = find_calls(src, kind)
        buckets = collections.Counter()
        subs = collections.Counter()          # %s_-style prefix substitutions
        span_hist = collections.defaultdict(collections.Counter)
        bytes_by = collections.Counter()
        for c in calls:
            args = split_args(c["args"], c["argkind"])
            if len(args) < 2 or c["fn"] == "sb_putc":
                buckets["OTHER-NONLITERAL"] += 1
                continue
            a1t, a1k = args[1]
            if not is_string_literal(a1t, a1k):
                buckets["OTHER-NONLITERAL"] += 1
                continue
            fmt = literal_body(a1t, a1k)
            convs = conversions(fmt)
            rest = expand_macros([a.strip() for a, _ in args[2:]])
            nprefix = sum(1 for r in rest if r in PREFIX_EXPRS)
            # source lines the format literal spans
            lit_start = c["argstart"] + a1t.index('"') if '"' in a1t else c["argstart"]
            span = a1t.count("\n") + 1
            nbytes = unescape_len(fmt)
            if not convs:
                b = "LIT"
            elif all(cv == "s" for cv in convs) and len(convs) == len(rest) \
                    and all(r in PREFIX_EXPRS for r in rest):
                b = "PFX-ONLY"
            else:
                b = "MIXED"
            buckets[b] += 1
            subs[b] += nprefix
            bytes_by[b] += nbytes
            span_hist[b][span] += 1
            if b in ("LIT", "PFX-ONLY") and span >= 5:
                big.append((path.split("/")[-1], c["line"], span, nbytes,
                            nprefix, b))
        grand[path] = {
            "calls": len(calls),
            "buckets": dict(buckets),
            "prefix_subs_by_bucket": dict(subs),
            "prefix_subs_total": sum(subs.values()),
            "literal_bytes_by_bucket": dict(bytes_by),
            "fmt_span_lines": {k: dict(sorted(v.items()))
                               for k, v in span_hist.items()},
            "blocks_span_ge5_LIT_or_PFXONLY":
                sum(n for k in ("LIT", "PFX-ONLY")
                    for s, n in span_hist[k].items() if s >= 5),
        }
    print(json.dumps(grand, indent=2))
    print("\n=== single-call literal BLOCKS spanning >= 5 source lines, "
          "convertible as-is to a $-template (file, line, span, bytes, "
          "#prefix-subs, bucket) ===")
    for e in sorted(big, key=lambda x: -x[2]):
        print("%-14s %5d  span=%-3d bytes=%-5d pfx=%-2d %s" % e)
    print("total such blocks: %d" % len(big))


if __name__ == "__main__":
    main()
