#!/usr/bin/env python3
"""tests/findings/findings_ref.py — an INDEPENDENT reference for the numbers
the findings seam computes, written from the spec text
(docs/spec/findings.md §3, §5 = docs/design/findings/design.md §2.5, §7) and
never from the C (learnings §3: two readings of one function share a source).

  findings_ref.py normalize        stdin: lines of 256 counts -> 256 ppm per line
  findings_ref.py digest PPM_TSV   the byte-rate digest of a 256-row ppm table
                                   (`byte<TAB>ppm`, decimal, as default_ppm.tsv)
  findings_ref.py vectors          the §2.5 test vectors' counts, one per line
  findings_ref.py bundle-digest RXT [NAME]
                                   [B2] the byte-rate digest a compile reading
                                   bundle NAME's `freq` block would stamp: its
                                   `row HH N` lines read by a regex (never by
                                   pcrec's parser), normalized and digested
                                   above. NAME defaults to the file's only
                                   bundle. The independent side of design
                                   §11.5 #17 (R18).
  findings_ref.py bundle-digest RXT NAME KIND VIA
                                   [B5] the same for bundle NAME's KIND block
                                   derived by VIA: `cpfreq` rows (`row U+HHHH
                                   N`) through `encode-utf8` or
                                   `encode-latin1` (derive, below).
  findings_ref.py derive VIA       [B5] stdin: `cp count` lines (hex, decimal);
                                   stdout: the 256 derived byte counts, then
                                   `dropped N` — design §2.4's definitions,
                                   with Python's own UTF-8 codec as the
                                   encoder (never pcrec's).
"""
import re
import sys

FLOOR = 2


def normalize(c):
    n = sum(c)
    if n == 0:
        return None
    z = sum(1 for x in c if x == 0)
    m = 10**6 - FLOOR * z
    ppm = [FLOOR if x == 0 else max(FLOOR, x * m // n) for x in c]
    r = 10**6 - sum(ppm)
    big = max(range(256), key=lambda b: (ppm[b], -b))  # largest, ties lowest byte
    ppm[big] += r
    return ppm


def fnv1a64(data, h=0xcbf29ce484222325):
    for byte in data:
        h ^= byte
        h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h


def digest(ppm):
    data = b"pcrec-find-1\0byte-rate\0" + b"".join(v.to_bytes(4, "little") for v in ppm)
    return "%016x" % fnv1a64(data)


MAX_COUNT = 2**40


def derive(via, cps):
    """design §2.4: encode-utf8 adds a code point's count once per byte of
    its UTF-8 encoding; encode-latin1 puts a code point <= U+00FF's count on
    that byte and DROPS the rest. None when a derived count exceeds the
    count ceiling (the reader refuses such a block)."""
    out, dropped = [0] * 256, 0
    for cp, n in cps:
        if via == "encode-utf8":
            bs = chr(cp).encode("utf-8")
        elif cp <= 0xFF:
            bs = bytes([cp])
        else:
            dropped += n
            continue
        for b in bs:
            out[b] += n
    if max(out) > MAX_COUNT:
        return None, dropped
    return out, dropped


VECTORS = {
    # all-equal: 10^6/256 = 3906.25 floors to 3906, residue 64 on byte 0
    "all-equal": [1] * 256,
    # one-nonzero: 255 floors of 2, the one counted byte takes the rest
    "one-nonzero": [5 if b == 0x61 else 0 for b in range(256)],
    # floors forcing a NEGATIVE residue: 255 counts of 1 each round to 0 and
    # are lifted to the floor, so the largest entry gives the excess back
    "negative-residue": [10**12] + [1] * 255,
}

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "normalize":
        for line in sys.stdin:
            c = [int(x) for x in line.split()]
            p = normalize(c)
            print("error -1" if p is None else " ".join(map(str, p)))
    elif mode == "digest":
        rows = [l.split("\t") for l in open(sys.argv[2]).read().split("\n")
                if l.strip() and not l.startswith("#")]
        ppm = [0] * 256
        for b, v in rows:
            ppm[int(b)] = int(v)
        print(digest(ppm))
    elif mode == "derive":
        cps = [(int(a, 16), int(b)) for a, b in
               (l.split() for l in sys.stdin if l.strip())]
        out, dropped = derive(sys.argv[2], cps)
        if out is None:
            print("error -1")
        else:
            print(" ".join(map(str, out)))
            print("dropped %d" % dropped)
    elif mode == "bundle-digest" and len(sys.argv) > 5:
        name, kind, via = sys.argv[3], sys.argv[4], sys.argv[5]
        cur, blk, cps, counts = None, None, [], [0] * 256
        for ln in open(sys.argv[2], encoding="utf-8"):
            m = re.match(r"analysis (\S+)$", ln.rstrip("\n"))
            if m:
                cur, blk = m.group(1), None
                continue
            m = re.match(r"    (\S+)$", ln.rstrip("\n"))
            if m:
                blk = m.group(1)
                continue
            if cur != name or blk != kind:
                continue
            m = re.match(r"\s+row U\+([0-9A-F]{4,6}) (\d+)$", ln)
            if m:
                cps.append((int(m.group(1), 16), int(m.group(2))))
            m = re.match(r"\s+row ([0-9a-f]{2}) (\d+)$", ln)
            if m:
                counts[int(m.group(1), 16)] = int(m.group(2))
        if via != "unigram":
            counts, _ = derive(via, cps)
        p = normalize(counts) if counts else None
        print("none" if p is None else digest(p))
    elif mode == "bundle-digest":
        want = sys.argv[3] if len(sys.argv) > 3 else None
        cur, counts = None, {}
        for ln in open(sys.argv[2], encoding="utf-8"):
            m = re.match(r"analysis (\S+)$", ln.rstrip("\n"))
            if m:
                cur = m.group(1)
                continue
            m = re.match(r"\s+row ([0-9a-f]{2}) (\d+)$", ln)
            if m and cur and (want is None or cur == want):
                counts.setdefault(cur, [0] * 256)[int(m.group(1), 16)] = int(m.group(2))
        if len(counts) != 1:
            sys.exit("bundle-digest: want exactly one bundle, found %d" % len(counts))
        p = normalize(list(counts.values())[0])
        print("none" if p is None else digest(p))
    elif mode == "vectors":
        for name, c in VECTORS.items():
            print(" ".join(map(str, c)))
    else:
        sys.exit(2)
