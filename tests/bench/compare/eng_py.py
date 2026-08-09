#!/usr/bin/env python3
"""eng_py.py — python3 `re` timing driver, used by
tests/bench/compare/compare.sh's cross-engine performance comparison.

Same role and same warmup-then-timed-loop shape as eng_pcrec.c / eng_pcre2.c
(see eng_pcrec.c's header for the full rationale); this file matches their
`status=` output line exactly so compare.sh has one parser for all three
engines. The one real difference is inherent to what's being measured: this
engine's real-world cost per search includes the interpreter dispatch and
Python-level function-call overhead around the compiled `re` object, not
just the C matcher underneath it. README.md's methodology section calls
this out explicitly -- it is intentionally NOT stripped out, because that
overhead is exactly what a real Python caller of `re.search` pays. Pattern
compilation itself (`re.compile`) is excluded from the timed region, same
as the compile-time exclusion applied to every other engine here.

Patterns are compiled with a bytes pattern (`pattern.encode()`) against a
bytes subject read straight from disk, so semantics match the other three
engines' byte-oriented matching (no str/codepoint decoding involved).

Usage: eng_py.py <pattern> <subject-file> <iters>
Prints exactly one line to stdout and exits 0:
  status=ok bytes=<n> iters=<k> secs=<s> mbps=<v> match=<0|1> start=<s> end=<e>
(start/end are 0 when match=0.) Exits 2 on usage/IO/compile error.
"""
import re
import sys
import time


def main() -> int:
    if len(sys.argv) != 4:
        sys.stderr.write(f"usage: {sys.argv[0]} <pattern> <subject-file> <iters>\n")
        return 2

    pattern_text, subject_path, iters_text = sys.argv[1], sys.argv[2], sys.argv[3]

    try:
        iters = int(iters_text)
        if iters <= 0:
            raise ValueError
    except ValueError:
        sys.stderr.write(f"eng_py: iters must be a positive integer, got '{iters_text}'\n")
        return 2

    try:
        with open(subject_path, "rb") as f:
            subject = f.read()
    except OSError as e:
        sys.stderr.write(f"eng_py: cannot read '{subject_path}': {e}\n")
        return 2

    try:
        compiled = re.compile(pattern_text.encode("utf-8"))
    except re.error as e:
        sys.stderr.write(f"eng_py: pattern compile error: {e}\n")
        print(f"status=cerr code=0 bytes={len(subject)} iters=0 secs=0.000000 "
              f"mbps=0.000 match=0 start=0 end=0")
        return 0

    n = len(subject)

    m = compiled.search(subject)  # untimed warmup, see module docstring

    t0 = time.perf_counter()
    for _ in range(iters):
        m = compiled.search(subject)
    t1 = time.perf_counter()

    secs = t1 - t0
    mb = (n * iters) / (1024.0 * 1024.0)
    mbps = mb / secs if secs > 0.0 else 0.0

    if m is None:
        print(f"status=ok bytes={n} iters={iters} secs={secs:.6f} "
              f"mbps={mbps:.3f} match=0 start=0 end=0")
    else:
        print(f"status=ok bytes={n} iters={iters} secs={secs:.6f} "
              f"mbps={mbps:.3f} match=1 start={m.start()} end={m.end()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
