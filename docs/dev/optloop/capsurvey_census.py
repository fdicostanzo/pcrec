#!/usr/bin/env python3
"""[capsurvey] The prefilter-route census behind captures_via_dfa_survey.md §1.5.

Compiles every pcrec-bench `capability` pattern export at the SHIPPED DEFAULT
(`--features all`: captures on, engine auto) and reads the D81 stamps off the
emitted `.c`.  Compile-side only: no timing, no subject is ever matched.

pcrec-bench is READ-ONLY here (scope mandate): the `.rx` exports are read and
nothing in that repo is written.  Output goes to stdout as TSV; the committed
copy is `capsurvey_census.tsv`.

    PCREC=/path/to/build/pcrec \
    BENCH=/path/to/pcrec-bench/bench/capability/patterns \
    OUT=/tmp/scratch/art \
    python3 capsurvey_census.py > capsurvey_census.tsv

Columns: name, RX_ENGINE, RX_ENGINE_WHY, RX_VM_PREFILTER,
         RX_VM_PREFILTER_LANG, RX_NCAPS, prefilter_reason

`prefilter_reason` is the `prefilter` row of `--emit-ir`'s own listing
(second field) -- the compiler's own word for why a prefilter was or was not
built -- rather than anything this script derives.  A REFUSED row carries the
first line of the compiler's diagnostic in the RX_ENGINE_WHY column and empty
stamps.
"""
import os
import re
import subprocess
import sys

BENCH = os.environ.get(
    "BENCH", "/Users/fdicostanzo/pcrec-bench/bench/capability/patterns")
PCREC = os.environ.get("PCREC", "build/pcrec")
OUT = os.environ.get("OUT", "/tmp/capsurvey_art")
STAMPS = ("RX_ENGINE", "RX_ENGINE_WHY", "RX_VM_PREFILTER",
          "RX_VM_PREFILTER_LANG", "RX_NCAPS")


def emit_ir_prefilter(pattern):
    """The `prefilter` row's VALUE field from --emit-ir, or '' if unavailable."""
    r = subprocess.run([PCREC, "--features", "all", "--emit-ir",
                        "--pattern", pattern],
                       capture_output=True, timeout=600)
    if r.returncode != 0:
        return ""
    for line in r.stdout.decode("utf8", "replace").split("\n"):
        f = line.split("\t")
        if f and f[0] == "prefilter":
            return f[1] if len(f) > 1 else ""
    return ""


def main():
    os.makedirs(OUT, exist_ok=True)
    print("\t".join(("name",) + STAMPS + ("prefilter_reason",)))
    for fn in sorted(os.listdir(BENCH)):
        if not fn.endswith(".rx"):
            continue
        name = fn[:-3]
        with open(os.path.join(BENCH, fn), "rb") as fh:
            pattern = fh.read()
        art = os.path.join(OUT, re.sub(r"[^A-Za-z0-9_.-]", "_", name) + ".c")
        r = subprocess.run([PCREC, "--features", "all", "-o", art,
                            "--pattern", pattern],
                           capture_output=True, timeout=600)
        if r.returncode != 0:
            why = r.stderr.decode("utf8", "replace").strip().split("\n")[0]
            print("\t".join([name, "REFUSED", why] + [""] * 3 + [""]))
            continue
        # The stamps are split across the pair: the axis stamps live in the
        # .c, `RX_NCAPS` in the .h.  Read BOTH -- reading only the .c reports
        # every artifact's capture count as absent.
        text = ""
        for path in (art, art[:-2] + ".h"):
            try:
                with open(path, encoding="utf8", errors="replace") as fh:
                    text += fh.read()
            except OSError:
                pass
        st = dict(re.findall(r"^#define\s+(RX_[A-Z0-9_]+)\s+(.*?)\s*$",
                             text, re.M))
        row = [name] + [st.get(k, "-") for k in STAMPS]
        row.append(emit_ir_prefilter(pattern))
        print("\t".join(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
