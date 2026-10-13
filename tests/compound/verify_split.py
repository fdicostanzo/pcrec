#!/usr/bin/env python3
"""tests/compound/verify_split.py -- re-check tests/compound/split.rxt against
libpcre2, INDEPENDENTLY of gen_split.py: its own parser for the vocabulary
the generator writes (pattern / encoding / features / perr / m n ms ns / g /
mc), and every question re-asked of the oracle -- the span, every group slot
and the find-all count (its own match_api.md §3.1 loop). Nothing is imported
from the generator, so a transcription fault between table and file shows.

  verify_split.py ORACLE_BIN SCRATCH [FILE]

ORACLE_BIN is tests/fuzz/pcre2_oracle.c built against libpcre2-8 (options=0;
`encoding utf8` is a `(*UTF)` prefix on the pattern). Exit 0 = every cell
agrees; the cell counts are printed with a non-vacuity floor."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def unq(s):
    """The quoted subject's bytes (the `.rxt` subject escapes)."""
    assert s[0] == '"' and s[-1] == '"', s
    s, out, i = s[1:-1], bytearray(), 0
    while i < len(s):
        if s[i] == "\\":
            n = s[i + 1]
            if n == "x":
                out.append(int(s[i + 2:i + 4], 16)); i += 4; continue
            out += {"n": b"\n", "t": b"\t", "r": b"\r", '"': b'"', "\\": b"\\"}[n]
            i += 2
        else:
            out += s[i].encode(); i += 1
    return bytes(out)


def split_q(rest):
    """`"subject" tail...` -> (subject-bytes, tail-words)."""
    j = 1
    while rest[j] != '"':
        j += 2 if rest[j] == "\\" else 1
    return unq(rest[:j + 1]), rest[j + 1:].split()


def ask(binp, scratch, pat, utf, subj, sp):
    f = os.path.join(scratch, "vs")
    open(f, "wb").write(subj)
    r = subprocess.run([binp, (b"(*UTF)" if utf else b"") + pat, f, str(sp)],
                       capture_output=True, timeout=60)
    a = r.stdout.decode().split()
    return None if a[0] == "nomatch" else list(map(int, a[1:]))


def count(binp, scratch, pat, utf, subj):
    n, p, c = len(subj), 0, 0
    while p <= n:
        v = ask(binp, scratch, pat, utf, subj, p)
        if v is None:
            break
        c += 1
        if v[1] > v[0]:
            p = v[1]
        else:
            p = v[0] + 1
            while utf and p < n and (subj[p] & 0xC0) == 0x80:
                p += 1
    return c


def main():
    binp, scratch = sys.argv[1:3]
    path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "split.rxt")
    os.makedirs(scratch, exist_ok=True)
    pat, utf, last, bad, cells, groups, mcs, perrs = None, False, None, [], 0, 0, 0, 0
    for no, ln in enumerate(open(path, encoding="utf-8"), 1):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("#"):
            continue
        kw, _, rest = ln.partition(" ")
        if kw == "pattern":
            pat, utf, last = rest.encode(), False, None
        elif kw == "encoding":
            utf = rest == "utf8"
        elif kw in ("features",):
            pass
        elif kw == "perr":
            perrs += 1
        elif kw in ("m", "n", "ms", "ns"):
            sp = 0
            if kw in ("ms", "ns"):
                sp, rest = rest.split(" ", 1)
                sp = int(sp)
            subj, tail = split_q(rest)
            last = ask(binp, scratch, pat, utf, subj, sp)
            cells += 1
            want = None if kw in ("n", "ns") else list(map(int, tail))
            if (last is None) != (want is None) or (want and last[:2] != want):
                bad.append("%d: %s -> oracle %s" % (no, ln[:120], last))
        elif kw == "g":
            k, s0, e0 = map(int, rest.split())
            groups += 1
            if not last or last[2 * k:2 * k + 2] != [s0, e0]:
                bad.append("%d: %s -> oracle %s" % (no, ln, last))
        elif kw == "mc":
            subj, tail = split_q(rest)
            mcs += 1
            c = count(binp, scratch, pat, utf, subj)
            if c != int(tail[0]):
                bad.append("%d: %s -> oracle %d" % (no, ln[:120], c))
        else:
            bad.append("%d: an unknown line kind %r" % (no, kw))
    for b in bad[:20]:
        print("FAIL: " + b)
    floor = cells >= 5000 and mcs >= 1000
    print("%s: %s: %d span cells, %d group slots, %d find-all counts, %d perr blocks "
          "re-asked of libpcre2; %d disagreements" %
          ("PASS" if not bad and floor else "FAIL", os.path.basename(path), cells, groups,
           mcs, perrs, len(bad)))
    return 0 if not bad and floor else 1


if __name__ == "__main__":
    sys.exit(main())
