#!/usr/bin/env python3
"""
[K59RUNG-BYTEID] corpus-wide emit-diff sweep, cmtfix_report.md's methodology.

Baseline compiler: build from git-archive of the dial+K59 train's branch
point (parent 1 of cf0962e3). Fixed compiler: the merged main (cf0962e3,
built in worktrees/byteid). Every corpus `pattern`/`pattern-esc` line
compiled by BOTH at default flags (no --tune, no --features, no -i, no
--engine/--encoding override -- cmtfix's own simplified driver shape,
which is why module-gated patterns show up as "both-refuse" rather than
being fed the flags their own block would carry).

Uses each compiler's OWN --list-source to enumerate pattern blocks (avoids
hand-parsing the .rxt escape vocabulary wrong) and decodes column 5's
escape vocabulary (\\t \\n \\r \\\\ \\xNN) to raw bytes, passed to the
compiler via subprocess argv (never a shell string) -- this file's own
proof that a shell-string pattern with '/*'/'*/ ' bytes is exactly the
kind of thing to avoid.

Outputs go to per-index basenames in two separate directories (the
same-basename-different-directory trap run_trie_identity.sh warns about
does not apply here since we diff bytes directly rather than comparing
via any tool that infers identity from the basename -- but distinct
per-pattern basenames are still used so no compile clobbers another's
output on either side).
"""
import subprocess
import sys
import os
import re

BASELINE_PCREC = sys.argv[1]
FIXED_PCREC = sys.argv[2]
REPO_ROOT = sys.argv[3]  # the worktree, for enumerating tests/**/*.rxt
OUT_BASE = sys.argv[4]

BDIR = os.path.join(OUT_BASE, "baseline_out")
FDIR = os.path.join(OUT_BASE, "fixed_out")
os.makedirs(BDIR, exist_ok=True)
os.makedirs(FDIR, exist_ok=True)


def decode_escape(s: str) -> bytes:
    """Decode the .rxt subject-escape vocabulary: \\t \\n \\r \\\\ \\xNN."""
    out = bytearray()
    i = 0
    b = s.encode("utf-8", errors="surrogateescape")
    n = len(b)
    while i < n:
        c = b[i]
        if c == 0x5C and i + 1 < n:  # backslash
            nxt = b[i + 1]
            if nxt == ord('t'):
                out.append(0x09); i += 2; continue
            elif nxt == ord('n'):
                out.append(0x0A); i += 2; continue
            elif nxt == ord('r'):
                out.append(0x0D); i += 2; continue
            elif nxt == 0x5C:
                out.append(0x5C); i += 2; continue
            elif nxt == ord('x') and i + 3 < n:
                hx = bytes([b[i+2], b[i+3]])
                try:
                    val = int(hx, 16)
                    out.append(val)
                    i += 4
                    continue
                except ValueError:
                    pass
            # unrecognized escape: pass backslash through literally
            out.append(c); i += 1; continue
        else:
            out.append(c); i += 1
    return bytes(out)


def find_rxt_files(root):
    files = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(root, "tests")):
        for fn in filenames:
            if fn.endswith(".rxt"):
                files.append(os.path.join(dirpath, fn))
    return sorted(files)


def list_source_patterns(pcrec_bin, rxt_file):
    """Run --list-source, return list of (kind, decoded_pattern_bytes)."""
    try:
        r = subprocess.run([pcrec_bin, "--list-source", rxt_file],
                            capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        return []
    out = r.stdout.decode("utf-8", errors="surrogateescape")
    rows = []
    for line in out.splitlines():
        if line.startswith("#"):
            continue
        if not line.strip():
            continue
        fields = line.split("\t")
        if len(fields) < 5:
            continue
        kind = fields[0]
        if kind not in ("pattern", "pattern-esc"):
            continue
        pattern_field = fields[4]
        rows.append((kind, decode_escape(pattern_field)))
    return rows


def main():
    files = find_rxt_files(REPO_ROOT)
    print(f"# .rxt files found: {len(files)}", file=sys.stderr)

    all_patterns = []  # list of bytes
    for f in files:
        rows = list_source_patterns(FIXED_PCREC, f)
        for kind, pat in rows:
            all_patterns.append(pat)

    print(f"# total pattern/pattern-esc lines: {len(all_patterns)}", file=sys.stderr)

    identical = 0
    both_refuse = 0
    newly_fixed = 0
    newly_broken = 0
    movers = []  # (idx, pattern, baseline_size, fixed_size, delta, diff_summary)

    for idx, pat in enumerate(all_patterns):
        bout = os.path.join(BDIR, f"p{idx}.c")
        fout = os.path.join(FDIR, f"p{idx}.c")
        argv_b = [BASELINE_PCREC, "-p", "rx", "-o", bout, "--", pat]
        argv_f = [FIXED_PCREC, "-p", "rx", "-o", fout, "--", pat]
        # subprocess needs bytes args; Python's subprocess accepts bytes in argv on POSIX
        try:
            rb = subprocess.run(argv_b, capture_output=True, timeout=30)
        except subprocess.TimeoutExpired:
            rb = None
        try:
            rf = subprocess.run(argv_f, capture_output=True, timeout=30)
        except subprocess.TimeoutExpired:
            rf = None

        b_ok = rb is not None and rb.returncode == 0 and os.path.exists(bout)
        f_ok = rf is not None and rf.returncode == 0 and os.path.exists(fout)

        if not b_ok and not f_ok:
            both_refuse += 1
            continue
        if not b_ok and f_ok:
            newly_fixed += 1
            os.remove(fout) if os.path.exists(fout) else None
            continue
        if b_ok and not f_ok:
            newly_broken += 1
            os.remove(bout) if os.path.exists(bout) else None
            continue

        # both compiled -- byte compare
        with open(bout, "rb") as fh:
            bdata = fh.read()
        with open(fout, "rb") as fh:
            fdata = fh.read()

        if bdata == fdata:
            identical += 1
            os.remove(bout)
            os.remove(fout)
            continue

        # mover -- record delta and a short diff summary
        delta = len(fdata) - len(bdata)
        # find first differing byte offset for a summary
        minlen = min(len(bdata), len(fdata))
        first_diff = None
        for i in range(minlen):
            if bdata[i] != fdata[i]:
                first_diff = i
                break
        if first_diff is None:
            first_diff = minlen
        movers.append((idx, pat, len(bdata), len(fdata), delta, first_diff))
        # keep the files for inspection; don't delete

    print("")
    print("=== RESULTS ===")
    print(f"identical:      {identical}")
    print(f"both_refuse:    {both_refuse}")
    print(f"newly_fixed:    {newly_fixed}")
    print(f"newly_broken:   {newly_broken}")
    print(f"movers:         {len(movers)}")
    print(f"total:          {len(all_patterns)}")
    print("")

    if movers:
        print("=== MOVER DETAIL ===")
        from collections import Counter
        delta_counts = Counter(d for (_, _, _, _, d, _) in movers)
        print("Delta histogram (bytes fixed - baseline -> count):")
        for d, c in sorted(delta_counts.items()):
            print(f"  {d:+d}  x{c}")
        print("")
        print("First 20 movers:")
        for (idx, pat, bsz, fsz, delta, fdiff) in movers[:20]:
            try:
                pstr = pat.decode("utf-8", errors="backslashreplace")
            except Exception:
                pstr = repr(pat)
            print(f"  idx={idx} delta={delta:+d} baseline={bsz} fixed={fsz} first_diff_offset={fdiff} pattern={pstr!r}")

    # write full mover list to a file for the report
    with open(os.path.join(OUT_BASE, "movers.tsv"), "w") as fh:
        fh.write("idx\tdelta\tbaseline_size\tfixed_size\tfirst_diff_offset\tpattern\n")
        for (idx, pat, bsz, fsz, delta, fdiff) in movers:
            try:
                pstr = pat.decode("utf-8", errors="backslashreplace")
            except Exception:
                pstr = repr(pat)
            fh.write(f"{idx}\t{delta}\t{bsz}\t{fsz}\t{fdiff}\t{pstr}\n")


if __name__ == "__main__":
    main()
