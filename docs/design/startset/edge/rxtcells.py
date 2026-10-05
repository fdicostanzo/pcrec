#!/usr/bin/env python3
"""[START-SET] edge lane: read the DRAFT edge cells back.

Two sources, one shape:
  * `*.rxt` here, in the house format (docs/spec/rxt_format.md), read with a
    MINIMAL reader of the subset these files use: `pattern`, `flags`,
    `encoding`, `engine vm`, `budget frames=`, `description`, `tag`,
    `ms`/`ns`/`m`/`n`, `g`, `gu`.  Anything else is a hard error, so a file
    that drifts outside the subset is not silently half-read.
  * `utfcheck_cells.tsv`: the `-futf-check` cells no `.rxt` directive can
    compile (tests/utfcheck/CLAUDE.md), one case per row.

A block is a dict: id (file:line), pat, flags, enc, engine, frames, xflags,
tags, cases = [(startpos, subject_bytes, expect)] where expect is
("m", [(s,e), ...slot spans, None for unset...]) | ("n",) | ("gu", word) | ("utf",),
plus `alt` (an also-acceptable answer, the Q-R3 give-up allowance) when tagged.
"""
import os, re

ESC = {'"': b'"', "\\": b"\\", "n": b"\n", "t": b"\t", "r": b"\r", "f": b"\f", "v": b"\v"}


def unq(s):
    """Decode one double-quoted subject; return (bytes, rest)."""
    assert s[0] == '"', s
    out = bytearray(); i = 1
    while s[i] != '"':
        if s[i] == "\\":
            c = s[i + 1]
            if c == "x": out += bytes([int(s[i + 2:i + 4], 16)]); i += 4; continue
            out += ESC[c]; i += 2; continue
        out += s[i].encode("utf-8"); i += 1
    return bytes(out), s[i + 1:].strip()


def read_rxt(path):
    blocks = []; cur = None
    for ln, raw in enumerate(open(path, encoding="utf-8"), 1):
        line = raw.rstrip("\n")
        if not line or line.startswith("#"): continue
        kw, _, rest = line.partition(" ")
        if kw == "pattern":
            cur = {"id": "%s:%d" % (os.path.basename(path), ln), "pat": rest, "flags": "", "enc": "byte",
                   "engine": None, "frames": None, "xflags": [], "tags": {}, "cases": [], "desc": ""}
            blocks.append(cur); continue
        assert cur is not None, "%s:%d: line before any pattern" % (path, ln)
        if kw == "flags": cur["flags"] = rest
        elif kw == "encoding": cur["enc"] = rest.strip()
        elif kw == "engine": assert rest.strip() == "vm"; cur["engine"] = "vm"
        elif kw == "budget":
            k, v = rest.strip().split("="); assert k == "frames"; cur["frames"] = int(v)
        elif kw == "description": cur["desc"] = rest
        elif kw == "tag":
            for it in rest.split(","):
                k, _, v = it.strip().partition("="); cur["tags"][k] = v or True
        elif kw in ("ms", "ns", "m", "n"):
            if kw in ("ms", "ns"): p, rest = rest.split(" ", 1); p = int(p)
            else: p = 0
            subj, tail = unq(rest)
            if kw in ("m", "ms"):
                s, e = map(int, tail.split()); cur["cases"].append([p, subj, ("m", [(s, e)])])
            else:
                assert not tail; cur["cases"].append([p, subj, ("n",)])
        elif kw == "g":
            k, s, e = map(int, rest.split()); exp = cur["cases"][-1][2]; assert exp[0] == "m"
            while len(exp[1]) <= k: exp[1].append(None)
            exp[1][k] = None if s < 0 else (s, e)
        elif kw == "gu":
            word, rest2 = rest.split(" ", 1); subj, tail = unq(rest2); assert not tail
            cur["cases"].append([0, subj, ("gu", word)])
        else:
            raise SystemExit("%s:%d: unsupported line kind %r in an edge draft" % (path, ln, kw))
    return blocks


def read_utfcheck(path):
    """id \t pattern_hex \t flags \t engine \t subject_hex \t startpos \t expect (utf | n | m s e)"""
    blocks = {}
    for ln, raw in enumerate(open(path), 1):
        if raw.startswith("#") or not raw.strip(): continue
        bid, ph, fl, eng, sh, sp, exp = raw.rstrip("\n").split("\t")
        b = blocks.setdefault(bid, {"id": "%s:%s" % (os.path.basename(path), bid), "pat": bytes.fromhex(ph).decode("utf-8"),
                                    "flags": fl if fl != "-" else "", "enc": "utf8", "engine": eng if eng != "-" else None,
                                    "frames": None, "xflags": ["-futf-check"], "tags": {}, "cases": [], "desc": ""})
        ex = exp.split()
        e = ("utf",) if ex[0] == "utf" else ("n",) if ex[0] == "n" else ("m", [(int(ex[1]), int(ex[2]))])
        b["cases"].append([int(sp), bytes.fromhex(sh), e])
    return list(blocks.values())


def load(dirpath):
    out = []
    for f in sorted(os.listdir(dirpath)):
        if f.endswith(".rxt"): out += read_rxt(os.path.join(dirpath, f))
    u = os.path.join(dirpath, "utfcheck_cells.tsv")
    if os.path.exists(u): out += read_utfcheck(u)
    return out
