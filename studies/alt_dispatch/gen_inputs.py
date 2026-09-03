#!/usr/bin/env python3
"""gen_inputs.py -- derive this study's patterns/*.branches and subjects/*.bin
from pcrec-bench's bench/altwide/ set (READ-ONLY input; never written to).

[ENG-ISL.S0], the alternation-dispatch study (chartered 2026-09-03). Every
file this script writes carries a PROVENANCE comment naming its bench source
(path + a content check) so a reader can tell derived data from bench canon
without re-running this script.

WHAT THIS EXTRACTS, per the charter's seven shapes (w, srt, pfx3, ci, cnt,
s, sh1):

  - w, s, sh1, pfx3       -- literal branch lists, parsed straight out of the
                             bench's committed `.rx` files at every width the
                             bench provides for that shape.
  - srt-1024, srt-2048    -- NOT in the bench (`srt-*.rx` stops at 512). Built
                             here by the exact rule `gen_patterns.py`'s
                             `wrap()` uses for `wrapper == "sorted"`:
                             `sorted(words)` (a full lexicographic sort, not
                             merely a first-byte sort -- the bench's own
                             wrapper does the same) applied to `w-1024`'s and
                             `w-2048`'s OWN branch lists, which the bench does
                             commit. No new pool words are drawn; this is a
                             pure reordering of already-committed branches, so
                             it needs no fresh randomness and cannot drift
                             from the bench's own pool.
  - ci-1024, ci-2048      -- likewise not in the bench. `w-1024`/`w-2048`'s
                             branch lists, unreordered, tagged MODE ci so the
                             harness folds case per position (see
                             src/common.h's ByteSet -- a ci branch is a
                             sequence of {lower, upper} sets, not a second
                             copy of the word).
  - cnt                   -- the charter's note applies: a `{1,3}` bounded
                             wrapper multiplies how many times the SAME
                             alternation entry is dispatched per match
                             attempt, but does not change what one entry's
                             dispatch costs -- `cnt-64`'s inner alternation is
                             `w-64`'s own branch list. No separate pattern
                             file is derived; the design note says why
                             `w-64`'s numbers stand in for it.
  - sh1/pfx3 beyond 512   -- NOT derivable. Both pools cap at 512 words in
                             every bench artifact this study may read (`sh1`
                             and `pfx3` `POOL_SPECS` entries in
                             bench/altwide/altwidetext.py both draw n=512),
                             and no committed `.rx` file uses more than the
                             first 512 of either. Extending would mean
                             drawing NEW pool words with the bench's RNG,
                             which is bench-side generation this script does
                             not perform (the scope mandate: bench dependencies
                             live in pcrec-bench, never here, and inventing a
                             second, uncoordinated draw under the same pool
                             name would silently diverge from the bench's own
                             `POOL_SEED` draw if the bench ever widens it).
                             Recorded as a gap in docs/design/alt_dispatch_study.md.

Usage:
    python3 gen_inputs.py            # write patterns/ and subjects/
    python3 gen_inputs.py --check    # re-derive to a temp dir and diff
"""
import argparse
import filecmp
import hashlib
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = "/home/duxevents/pcrec-bench/bench/altwide"
PAT_OUT = os.path.join(HERE, "patterns")
SUB_OUT = os.path.join(HERE, "subjects")

# name -> (bench .rx basename, extra note)
DIRECT_SHAPES = [
    "w-8", "w-64", "w-96", "w-128", "w-192", "w-256", "w-384", "w-512",
    "w-1024", "w-2048",
    "s-256", "s-512", "s-2048", "s-4096",
    "sh1-64", "sh1-256", "sh1-512",
    "pfx3-256", "pfx3-512",
    "srt-256", "srt-512",
    "ci-256", "ci-512",
    "cnt-64",
]

SUBJECT_FILES = [
    # field/hit and near-miss short subjects (bench/altwide/subjects/*.bin)
    "f-w0", "f-w7", "f-w255", "f-w511", "f-w2047",
    "f-s0", "f-s4095",
    "f-sh1", "f-pfx3", "f-sfx", "f-nar4",
    "f-upper", "f-cnt2", "f-near", "f-prefix", "f-glued", "f-bg",
]
THROUGHPUT_FILES = [
    "t-128k-clean", "t-128k-sparse", "t-128k-dense", "t-512k-sparse",
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def strip_wrapper(text, name):
    """-> (words, mode, note). `text` is one bench .rx file's raw content."""
    t = text.strip()
    mode = "literal"
    if t.startswith("(?i)"):
        mode = "ci"
        t = t[len("(?i)"):]
    m = re.match(r"^\(\?:(.*)\)(\{1,3\})?$", t)
    if not m:
        raise ValueError("%s: unrecognized wrapper shape: %r" % (name, t[:60]))
    body = m.group(1)
    words = body.split("|")
    for w in words:
        if not re.match(r"^[a-z]+$", w):
            raise ValueError("%s: non-literal branch %r (not this study's "
                              "shape)" % (name, w))
    return words, mode, m.group(2) or ""


def write_branches(name, words, mode, provenance):
    path = os.path.join(PAT_OUT, name + ".branches")
    with open(path, "w") as f:
        f.write("# PROVENANCE: %s\n" % provenance)
        f.write("# MODE %s\n" % mode)
        f.write("# BRANCHES %d\n" % len(words))
        for w in words:
            f.write(w + "\n")
    return path


def load_direct(name):
    src = os.path.join(BENCH, "patterns", name + ".rx")
    with open(src) as f:
        text = f.read()
    words, mode, suffix = strip_wrapper(text, name)
    prov = "bench/altwide/patterns/%s.rx sha256=%s (%d bytes)%s" % (
        name, sha256_file(src), len(text), " suffix=%r" % suffix if suffix else "")
    write_branches(name, words, mode, prov)
    return words, mode


def derive_sorted(base_name, out_name, base_words):
    words = sorted(base_words)
    prov = ("derived: sorted(%s.rx's branch list) -- gen_patterns.py's own "
            "wrap(wrapper='sorted') rule, no new pool words drawn"
            % base_name)
    write_branches(out_name, words, "literal", prov)


def derive_ci(base_name, out_name, base_words):
    prov = ("derived: %s.rx's branch list, tagged MODE ci -- no new pool "
            "words drawn, no words rewritten (the harness folds case per "
            "position, see src/common.h)" % base_name)
    write_branches(out_name, base_words, "ci", prov)


def copy_subjects():
    manifest_path = os.path.join(SUB_OUT, "PROVENANCE.md")
    lines = ["# subjects/ provenance\n",
             "\n",
             "Every file below is copied byte-for-byte from pcrec-bench's "
             "`bench/altwide/`\n(subjects/ for the short field/hit files, "
             "throughput/ for the long prose files).\nRead-only source; "
             "this study never writes into pcrec-bench.\n\n",
             "| file | source | sha256 | bytes |\n|---|---|---|---|\n"]
    for name in SUBJECT_FILES:
        src = os.path.join(BENCH, "subjects", name + ".bin")
        dst = os.path.join(SUB_OUT, name + ".bin")
        shutil.copyfile(src, dst)
        lines.append("| %s.bin | subjects/%s.bin | %s | %d |\n" % (
            name, name, sha256_file(src), os.path.getsize(src)))
    for name in THROUGHPUT_FILES:
        src = os.path.join(BENCH, "throughput", name + ".bin")
        dst = os.path.join(SUB_OUT, name + ".bin")
        shutil.copyfile(src, dst)
        lines.append("| %s.bin | throughput/%s.bin | %s | %d |\n" % (
            name, name, sha256_file(src), os.path.getsize(src)))
    with open(manifest_path, "w") as f:
        f.writelines(lines)


def run(outdir_pat, outdir_sub):
    global PAT_OUT, SUB_OUT
    PAT_OUT, SUB_OUT = outdir_pat, outdir_sub
    os.makedirs(PAT_OUT, exist_ok=True)
    os.makedirs(SUB_OUT, exist_ok=True)

    words_by_name = {}
    for name in DIRECT_SHAPES:
        words, mode = load_direct(name)
        words_by_name[name] = words

    derive_sorted("w-1024", "srt-1024", words_by_name["w-1024"])
    derive_sorted("w-2048", "srt-2048", words_by_name["w-2048"])
    derive_ci("w-1024", "ci-1024", words_by_name["w-1024"])
    derive_ci("w-2048", "ci-2048", words_by_name["w-2048"])

    copy_subjects()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if not args.check:
        run(PAT_OUT, SUB_OUT)
        print("wrote patterns/ and subjects/")
        return 0

    with tempfile.TemporaryDirectory() as td:
        run(os.path.join(td, "patterns"), os.path.join(td, "subjects"))
        ok = True
        for sub, want_out in (("patterns", PAT_OUT_REAL), ("subjects", SUB_OUT_REAL)):
            got = os.path.join(td, sub)
            cmp = filecmp.dircmp(got, want_out)
            if cmp.left_only or cmp.right_only or cmp.diff_files:
                ok = False
                print("MISMATCH in %s: only-in-derived=%s only-in-committed=%s diff=%s"
                      % (sub, cmp.left_only, cmp.right_only, cmp.diff_files))
        if ok:
            print("--check: derived output matches committed patterns/ and subjects/")
            return 0
        return 1


PAT_OUT_REAL = PAT_OUT
SUB_OUT_REAL = SUB_OUT

if __name__ == "__main__":
    sys.exit(main())
