#!/usr/bin/env python3
"""clsmask_candidates: the REFERENCE rows -- patterns the brief names that no
population carries verbatim. Today one: ipv4 `(\\d{1,3}\\.){3}\\d{1,3}`
(capturing; the bench's bounded/dotted4 is its non-capturing twin), run over
the loglines throughput texts and the rw L02/L03 apache samples (both
carry IPv4-shaped addresses; the corpus's scrubbing rewrote real ones, see
rwcorpus PROVENANCE).

    pop_ref.py BENCHCOPY RWSUBJDIR > pop_ref.tsv
"""
import glob, os, sys
bench, rw = sys.argv[1], sys.argv[2]
subs = sorted(glob.glob(os.path.join(bench, "bench", "loglines", "throughput", "*.bin")))
subs += [os.path.join(rw, q) for q in ("L02", "L03") if os.path.exists(os.path.join(rw, q))]
print("pid\tset\tenc\ticase\tpattern_hex\tregime\tsubjects\textra")
print("ref/ipv4-cap\tref\tbyte\t0\t%s\tfindall\t%s\t" % (rb"(\d{1,3}\.){3}\d{1,3}".hex(), ",".join(subs)))
