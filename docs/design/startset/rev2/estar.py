#!/usr/bin/env python3
"""[START-SET] rev 2: the DFA hat's candidate sets, read off an EMITTED artifact
(docs/design/startset.md rev 2 §4.1, review r4 sound-F1).  For prefix PFX:

  s0     the start state (forward_state's initializer; 0 on a seeded machine)
  E      s0's escape set {b : delta(s0,b) != s0}, checked equal to the
         emitted can_begin_match where the row emits one
  Estar  the union over every seed state sigma (each forward_seed_state[c],
         plus s0) of {b : delta(sigma,b) != sigma}       -- option (a)'s E*
  Tdfa   the union over every seed state sigma of
         {b : delta(sigma,b) is neither a seed state nor dead} -- the bytes that
         begin a live thread in SOME context the skip can be in.  Derived from
         the subset construction's tables alone, sharing no code with the AST
         walk: THE INDEPENDENT FLOOR any sound narrowed set must contain.

    estar.py ARTIFACT.c PFX S_hex64   -> one JSON line
"""
import json, re, sys

def table(src, name):
    m = re.search(r"static const (?:unsigned |signed )?(?:char|short|int) %s\[(\d+)\] = \{(.*?)\};" % re.escape(name), src, re.S)
    if not m: return None
    v = [int(x) for x in re.findall(r"-?\d+", m.group(2))]
    assert len(v) == int(m.group(1)), name
    return v

def sets(path, pfx, s_hex):
    src = open(path).read()
    cls = table(src, pfx + "_forward_byte_class")
    nxt = table(src, pfx + "_forward_next_state")
    seed = table(src, pfx + "_forward_seed_state")
    cbm = table(src, pfx + "_can_begin_match")
    if None in (cls, nxt): return {"status": "no-table"}
    im = re.search(r"%s_forward_state forward_state = (?:search_from \? %s_forward_seed_state\[.*?\] : )?(\d+);" % (re.escape(pfx), re.escape(pfx)), src)
    if not im: return {"status": "no-init"}
    s0 = int(im.group(1))                # the start state (0 on a seeded machine; any id on an unseeded one)
    if seed is None: seed = [s0]         # an UNSEEDED machine: s0 is the only start context
    step = re.search(r"%s_forward_step\(.*?\)\s*\{\s*return transitions\[(.*?)\];" % re.escape(pfx), src, re.S)
    sm = re.fullmatch(r"s(?: \* (\d+))? \+ cl", step.group(1).strip()) if step else None
    assert sm, "unknown step form: %r" % (step and step.group(1))
    stride = int(sm.group(1) or 1)       # premultiplied (s + cl) or -fno-premul-table / wide (s * NCLS + cl)
    dm = re.search(r"%s_forward_is_dead\(%s_forward_state s\) \{ return s (==|<) (\d+);" % (re.escape(pfx), re.escape(pfx)), src)
    isdead = (lambda s, v=int(dm.group(2)): s == v) if dm.group(1) == "==" else (lambda s: s < 0)
    d = lambda s, b: nxt[s * stride + cls[b]]
    seeds = set(seed) | {s0}
    E = {b for b in range(256) if d(s0, b) != s0}
    # memchr / offset rows emit no table; E is then read off the machine.  Where a
    # table exists it must be state 0's escape set: cbm_agrees reports it (the
    # sweep requires it; the control counts the exceptions)
    cbm_agrees = cbm is None or E == {b for b in range(256) if cbm[b]}
    Es = {b for s in seeds for b in range(256) if d(s, b) != s}
    Td = {b for s in seeds for b in range(256) if d(s, b) not in seeds and not isdead(d(s, b))}
    S = {i for i in range(256) if bytes.fromhex(s_hex)[i >> 3] >> (i & 7) & 1}
    return {"status": "ok", "cbm_agrees": cbm_agrees, "Ecbm": None if cbm is None else [b for b in range(256) if cbm[b]], "nseeds": len(seeds), "E": sorted(E), "Estar": sorted(Es), "Tdfa": sorted(Td), "S": sorted(S),
            "fwd_class": cls}

if __name__ == "__main__":
    print(json.dumps(sets(*sys.argv[1:4])))
