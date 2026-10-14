#!/usr/bin/env python3
# docs/design/findall_iter/twin/label_census.py — lane iterdes, [FINDALL-NEXT].
#
# Counts, over every distinct corpus pattern (emit_sweep's own enumeration) at
# `-p rx --features all` on the byte and utf8 arms, the artifacts whose
# <prefix>_search body keeps label addresses in a STATIC table
# (`static const void *const rx_targets_N[] = { &&...`), which gcc refuses to
# duplicate by inlining (twin/run_twin.sh's `rg` case). Those bodies must stay
# ONE static function that `_search` and `_next` both call (findall_iter.md
# §2.2); the census sizes that population, split by the artifact's own
# RX_ENGINE / RX_DFA_SCAN stamps. The detector reads the text BETWEEN the
# search definition and its closing brace, so a table elsewhere (another
# entry's body) is not counted.
#
# usage: python3 -I label_census.py TREE [JOBS]
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

TREE = os.path.abspath(sys.argv[1])
JOBS = int(sys.argv[2]) if len(sys.argv) > 2 else 8
sys.path.insert(0, os.path.join(TREE, "scripts"))
import emit_sweep as es  # noqa: E402

PCREC = os.path.join(TREE, "build", "pcrec")
SIG = re.compile(r"\nint rx_search\(const unsigned char \*subject, size_t subject_length,"
                 r"\s*size_t search_from,\s*ptrdiff_t \(\*capture_spans\)\[2\]\)\n\{")
TBL = re.compile(r"static const void \*const \w+\[\d+\] = \{ *&&")
STAMP = re.compile(r'#define RX_(ENGINE|DFA_SCAN) "([^"]*)"')
ARMS = {"byte": [], "utf8": ["-e", "utf8"]}

pats = sorted({p for _, _, p in es.enumerate_corpus(PCREC, TREE, 60)})


def one(job):
    arm, pat = job
    argv = [PCREC, "-p", "rx", "--features", "all"] + ARMS[arm] + ["-o", "-", "--pattern", pat]
    try:
        r = subprocess.run(argv, capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        return arm, None
    if r.returncode != 0:
        return arm, None
    t = r.stdout.decode("utf-8", "surrogateescape")
    m = SIG.search(t)
    if not m:
        return arm, ("nosig", "", "")
    end = t.find("\n}\n", m.end())
    st = dict(STAMP.findall(t))
    return arm, ("table" if TBL.search(t[m.end():end]) else "plain",
                 st.get("ENGINE", "?"), st.get("DFA_SCAN", "-"))


tally = {}
with ThreadPoolExecutor(JOBS) as ex:
    for arm, v in ex.map(one, [(a, p) for a in ARMS for p in pats]):
        key = (arm,) + (v if v else ("refused", "", ""))
        tally[key] = tally.get(key, 0) + 1
print(f"distinct corpus patterns: {len(pats)}")
for k in sorted(tally):
    print("\t".join(k), tally[k], sep="\t")
