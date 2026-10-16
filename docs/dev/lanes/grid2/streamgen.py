#!/usr/bin/env python3
"""grid2: the STREAMED subject generator (regime_eval §2.4; r17b_prime §5.4 item 1).

One module, two users: grid2's item-1 fit-cell re-time (design2.py) and the
kit's E4 judge-cell timing (regime_eval E4 imports it). It owns the parts of a
streamed subject that do not depend on where the bytes come from:

  nbuf_for(n)               how many distinct buffers a streamed subject of
                            n-byte buffers holds (pre-registered, below)
  write_stream(dir, bufs)   writes buffers b00000..bNNNNN, refuses a repeated
                            buffer, writes MANIFEST.tsv (name, bytes, sha256)
                            beside them (gload.h skips dot-files only, so the
                            manifest is named with a leading dot: .manifest.tsv)
  verify_stream(dir)        re-reads and re-hashes; the manifest must match,
                            the buffers must be pairwise distinct
  disjoint(dirs)            the E6 disjointness proof's primitive: no sha256
                            appears in two subjects
  window_stream(dir, src, n, count, salt)
                            REAL text: count n-byte windows cut from the file
                            SRC at deterministic, strata-spread offsets (the
                            F2 streamed pass uses it; E4's pool drawing rule
                            of regime_eval §2.4 calls write_stream with its
                            own windows)
  synthetic_stream(dir, gen, name, nbuf)
                            nbuf buffers from gen(seed) -> (bytes, ...), one
                            seed per buffer derived from NAME

A streamed subject is a DIRECTORY of distinct buffers; grid1's driver cycles
its timed loops through them with one cursor that never resets, so
consecutive passes see distinct data (grid1/README.md item 5; check leg C).

PRE-REGISTERED SIZE (not fitted): STREAM_BYTES = 4 MiB of distinct data per
subject, so a 64 KiB subject has 64 buffers (regime_eval §2.4's 64 x 64 KiB),
clamped to [NBUF_MIN, NBUF_MAX] buffers: a 1 MiB subject keeps 16 buffers
(F2's fresh size), a 48-byte subject keeps 1024 distinct buffers (the cap on
file count; the buffers still differ, but the stream is 48 KiB, not 4 MiB).
grid1 streamed 64 MiB per subject; 4 MiB fits the 7700X's 32 MiB L3 as
regime_eval §2.4 ([r1 M-also]) states for the judge, and the load time per
launch falls from ~0.3 s to ~0.02 s.
"""
import hashlib, os, sys

STREAM_BYTES = 4 << 20
NBUF_MIN = 16
NBUF_MAX = 1024
MANIFEST = ".manifest.tsv"

def nbuf_for(n, total=STREAM_BYTES):
    return max(NBUF_MIN, min(NBUF_MAX, total // max(1, n)))

def seed_of(name, i):
    return int.from_bytes(hashlib.sha256(name.encode()).digest()[:8], "little") + i

def write_stream(path, bufs):
    """bufs: iterable of bytes. Returns the number of buffers written."""
    os.makedirs(path, exist_ok=True)
    seen, rows = set(), []
    for i, b in enumerate(bufs):
        d = hashlib.sha256(b).hexdigest()
        if d in seen:
            raise SystemExit(f"streamgen: {path}: buffer {i} repeats an earlier buffer")
        seen.add(d)
        nm = f"b{i:05d}"
        with open(os.path.join(path, nm), "wb") as f:
            f.write(b)
        rows.append((nm, len(b), d))
    with open(os.path.join(path, MANIFEST), "w") as f:
        f.write("name\tbytes\tsha256\n")
        for r in rows:
            f.write("%s\t%d\t%s\n" % r)
    return len(rows)

def verify_stream(path):
    """-> (nbuf, set of sha256). SystemExit on any mismatch."""
    want = {}
    for l in open(os.path.join(path, MANIFEST)).read().splitlines()[1:]:
        nm, n, d = l.split("\t")
        want[nm] = (int(n), d)
    have = sorted(f for f in os.listdir(path) if not f.startswith("."))
    if have != sorted(want):
        raise SystemExit(f"streamgen: {path}: files differ from the manifest")
    for nm in have:
        b = open(os.path.join(path, nm), "rb").read()
        if (len(b), hashlib.sha256(b).hexdigest()) != want[nm]:
            raise SystemExit(f"streamgen: {path}/{nm}: bytes differ from the manifest")
    if len({d for _, d in want.values()}) != len(want):
        raise SystemExit(f"streamgen: {path}: repeated buffers")
    return len(have), {d for _, d in want.values()}

def disjoint(dirs):
    """The E6 primitive: True when no buffer content is in two of DIRS."""
    seen = {}
    for p in dirs:
        _, hs = verify_stream(p)
        for h in hs:
            if h in seen and seen[h] != p:
                return False
            seen[h] = p
    return True

def window_offsets(size, n, count, name):
    """count offsets of n-byte windows over a SIZE-byte file, one per equal
    stratum, jittered by a hash of NAME (deterministic)."""
    if size < n:
        raise SystemExit(f"streamgen: source of {size} bytes holds no {n}-byte window")
    count = min(count, size // n)
    span = size // count
    out = []
    for j in range(count):
        room = max(1, min(span, size - n + 1 - j * span))
        h = int.from_bytes(hashlib.sha256(f"{name}/{j}".encode()).digest()[:8], "little")
        out.append(j * span + h % room)
    return out

def window_stream(path, src, n, count, name):
    data = open(src, "rb").read()
    offs = window_offsets(len(data), n, count, name)
    return write_stream(path, (data[o:o + n] for o in offs))

def synthetic_stream(path, gen, name, nbuf):
    """gen(seed) -> a tuple whose first element is the buffer's bytes."""
    return write_stream(path, (gen(seed_of(name, i))[0] for i in range(nbuf)))

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "verify":
        print("ok nbuf=%d" % verify_stream(sys.argv[2])[0])
    else:
        raise SystemExit(__doc__)
