#!/usr/bin/env python3
"""tests/startset/startset_lib.py -- shared pieces of the [START-SET] checks
(D148; docs/design/startset.md §6.2) and the stage-1 census
(docs/design/startset/s1/census_s1.py), so the two read ONE population.

  corpus_blocks(pcrec, tree)  every `pattern`/`pattern-esc` block of every
      `.rxt` under <tree>/tests, read through `pcrec --list-source` (the
      format's own parser, header-keyed columns), WITH ITS OWN OPTIONS the
      way tests/harness/run.sh builds a block's compile: `flags` i -> -i,
      u -> --ucp; `features` -> --features; `encoding`; `engine`; `tune`.
      Budgets are dropped (they bound a run, not a route or a fact). Blocks
      are deduplicated on (pattern bytes, options) -- review r4 sound-F4: the
      r3 census deduplicated on text alone and merged `[a-z]` with its `-i`
      twin. A pattern holding NUL cannot travel on argv and is counted out.
  facts(listing_text)  the `--emit-facts` listing's `facts` and `decisions`
      sections, header-keyed (docs/spec/facts_listing.md).
  machine_sets(c_text, pfx)  the forward DFA's start-context sets read off
      an EMITTED artifact: E (s0's escape set), the emitted can_begin_match
      table, the seed family, and Tdfa -- the bytes that begin a live thread
      from SOME seed state. Ported from docs/design/startset/rev2/estar.py
      (lane ssrev), which reads only the subset construction's tables and
      shares no code with the start-set walk; the port keeps its two
      instrument repairs (the initializer parse; the strided/signed table).
"""
import os, re, subprocess

FLAG_MAP = {"i": "-i", "u": "--ucp"}


def dec_field(b):
    """--list-source's escape vocabulary (\\t \\n \\r \\\\ \\xNN) -> bytes."""
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5c and i + 1 < len(b):
            n = b[i + 1]
            if n == 0x5c: out.append(0x5c); i += 2; continue
            if n == 0x74: out.append(9); i += 2; continue
            if n == 0x6e: out.append(10); i += 2; continue
            if n == 0x72: out.append(13); i += 2; continue
            if n == 0x78 and i + 3 < len(b):
                try:
                    out.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                except ValueError:
                    pass
        out.append(c); i += 1
    return bytes(out)


def block_args(row):
    """A block's own compile options, as tests/harness/run.sh builds them."""
    a = []
    for ch in row.get("flags", ""):
        if ch in FLAG_MAP: a.append(FLAG_MAP[ch])
    if row.get("features"): a += ["--features", row["features"]]
    if row.get("encoding"): a.append("--encoding=" + row["encoding"])
    if row.get("engine"): a.append("--engine=" + row["engine"])
    if row.get("tune"): a.append("--tune=" + row["tune"])
    return a


def rxt_files(tree):
    out = []
    for root, _d, fs in os.walk(os.path.join(tree, "tests")):
        out += [os.path.join(root, f) for f in fs if f.endswith(".rxt")]
    return sorted(out)


def corpus_blocks(pcrec, tree):
    """(blocks, counts): blocks deduplicated on (pattern, options)."""
    seen, blocks = set(), []
    n_rows = n_nul = n_dup = n_files = 0
    for f in rxt_files(tree):
        r = subprocess.run([pcrec, "--list-source", f], capture_output=True, timeout=120)
        if r.returncode:
            continue
        n_files += 1
        hdr = None
        for ln in r.stdout.split(b"\n"):
            if ln.startswith(b"#kind\t"):
                hdr = ln[1:].decode().split("\t"); continue
            if ln.startswith(b"#section"):
                break
            if hdr is None or not ln or ln.startswith(b"#"):
                continue
            fl = ln.split(b"\t")
            if fl[0] not in (b"pattern", b"pattern-esc"):
                continue
            row = {h: (fl[i] if i < len(fl) else b"") for i, h in enumerate(hdr)}
            n_rows += 1
            pat = dec_field(row["pattern"])
            if b"\x00" in pat:
                n_nul += 1; continue
            args = block_args({k: v.decode("utf-8", "replace") for k, v in row.items() if k != "pattern"})
            key = (pat, tuple(args))
            if key in seen:
                n_dup += 1; continue
            seen.add(key)
            blocks.append({"id": "%s:%s" % (os.path.relpath(f, tree), row["line"].decode()),
                           "pattern": pat, "args": args})
    return blocks, {"files": n_files, "rows": n_rows, "nul": n_nul, "dup": n_dup}


def facts(text):
    """{fact: row-dict} and {stamp: value} from an --emit-facts listing."""
    fact, dec, sec, hdr = {}, {}, None, None
    for ln in text.split("\n"):
        if ln.startswith("#section "):
            sec = ln.split()[1]; hdr = None; continue
        if ln.startswith("#"):
            hdr = ln[1:].split("\t"); continue
        if not ln or hdr is None:
            continue
        row = dict(zip(hdr, ln.split("\t")))
        if sec == "facts": fact[row.get("fact")] = row
        elif sec == "decisions": dec[row.get("stamp")] = row.get("value", "")
    return fact, dec


def set_of(value):
    """A `start_set` value -> (nullable, set of bytes)."""
    if value == "nullable":
        return True, set(range(256))
    n, hx = value.split(":")
    b = bytes.fromhex(hx)
    s = {i for i in range(256) if b[i >> 3] >> (i & 7) & 1}
    assert len(s) == int(n), value
    return False, s


def _table(src, name):
    m = re.search(r"static const (?:unsigned |signed )?(?:char|short|int) %s\[(\d+)\] = \{(.*?)\};"
                  % re.escape(name), src, re.S)
    if not m:
        return None
    v = [int(x) for x in re.findall(r"-?\d+", m.group(2))]
    return v if len(v) == int(m.group(1)) else None


def machine_sets(src, pfx="rx"):
    """The forward machine's start-context sets, or {'status': why-unread}."""
    cls = _table(src, pfx + "_forward_byte_class")
    nxt = _table(src, pfx + "_forward_next_state")
    seed = _table(src, pfx + "_forward_seed_state")
    cbm = _table(src, pfx + "_can_begin_match")
    if cls is None or nxt is None:
        return {"status": "no-table"}
    im = re.search(r"%s_forward_state forward_state = (?:\w+ \? %s_forward_seed_state\[.*?\] : )?(\d+);"
                   % (re.escape(pfx), re.escape(pfx)), src)
    if not im:
        return {"status": "no-init"}
    s0 = int(im.group(1))
    if seed is None:
        seed = [s0]
    step = re.search(r"%s_forward_step\(.*?\)\s*\{\s*return transitions\[(.*?)\];" % re.escape(pfx), src, re.S)
    sm = re.fullmatch(r"s(?: \* (\d+))? \+ cl", step.group(1).strip()) if step else None
    if not sm:
        return {"status": "step-form"}
    stride = int(sm.group(1) or 1)
    dm = re.search(r"%s_forward_is_dead\(%s_forward_state s\) \{ return s (==|<) (\d+);"
                   % (re.escape(pfx), re.escape(pfx)), src)
    if not dm:
        return {"status": "dead-form"}
    isdead = (lambda s, v=int(dm.group(2)): s == v) if dm.group(1) == "==" else (lambda s: s < 0)
    d = lambda s, b: nxt[s * stride + cls[b]]
    seeds = set(seed) | {s0}
    E = {b for b in range(256) if d(s0, b) != s0}
    Ecbm = None if cbm is None else {b for b in range(256) if cbm[b]}
    Td = {b for s in seeds for b in range(256) if d(s, b) not in seeds and not isdead(d(s, b))}
    return {"status": "ok", "nseeds": len(seeds), "E": E, "Ecbm": Ecbm,
            "cbm_agrees": Ecbm is None or E == Ecbm, "Tdfa": Td}
