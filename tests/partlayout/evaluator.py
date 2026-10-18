#!/usr/bin/env python3
"""tests/partlayout/evaluator.py -- [ENTRY-TABLE] E1's INDEPENDENT EVALUATOR
(docs/design/compound_entries.md §3.6, "a layout is read from the OBJECT and
judged against an expected set that shares no code with the tables").

It links nothing from src/ and reads no pcrec listing. For one witness and
one control setting it computes, from four inputs only:

  1. the CALL GRAPH of a copy of the DEFAULT artifact (compiled with no
     control) with every always_inline / noinline / noclone deleted by text,
     built `-O0 -fno-inline` and read from `objdump -dr` relocations -- the
     stripping happens here, so neither the emitter nor its bytes move;
  2. the OWNERS' attributes, read from the default artifact's own text: a
     function defined `always_inline` is folded into its callers when its
     callees' callers are counted (`callers`, §3.2);
  3. the HAND class map and HAND rank fixture (tests/partlayout/witnesses.tsv),
     and the copyable fact asked of gcc (the default text with the part
     forced always_inline: gcc's own "can never be copied/inlined" refusal,
     §2.1 H1/H2, is the fact);
  4. the RESOLVED controls, from the compile's own arguments and the preset
     cells of docs/spec/tuning.md §5.4 (read from the spec text, never from
     src/core/tune.c), and the rows' order as the spec's prose states it.

It then judges the REAL object (the artifact compiled WITH the controls,
`-O2`): a part expected `shared` must be one local symbol, a part expected
`inline` must be absent, and no shared part may have a clone
(`.constprop`, `.isra`, `.part.N`). It also computes the expected
`<PREFIX>_PART_LAYOUT` / `_WHY` stamp values and compares them with the
artifact's. Exit 0 and one `OK` line, or one `MISMATCH ...` line per finding
and exit 1.

usage: evaluator.py PCREC SPEC_TUNING_MD WORKDIR CLASSMAP RANKS PATTERN [CONTROL...]
  CLASSMAP: comma list FUNC=CLASS (CLASS a class token, or `owned`)
  RANKS:    comma list FUNC=Rn (the hand rank fixture for this witness)
"""
import os
import re
import subprocess
import sys

CC = os.environ.get("CC", "gcc")
CLASSES = ["prefilter", "compound", "find", "wrap"]
VALUES = {"auto": 1, "shared": 2, "inline": 3}
RANKS = {"none": 1, "R3": 2, "R2": 3, "R1": 4, "R0": 5, "measured": 6}
TUNE_COLS = {"-2": 1, "-1": 2, "0": 3, "+1": 4, "+2": 5,
             "min-size": 1, "size": 2, "balanced": 3, "speed": 4, "max-speed": 5}


def run(argv, **kw):
    return subprocess.run(argv, capture_output=True, text=True, **kw)


def presets(spec_path, col):
    """The §5.4 preset cells at one position: residual, rank, class values.
    A cell carrying a dagger is an em-dash pending its ruled diff, so it
    is UNSET; an em-dash is unset; anything else in backticks is a value."""
    want = {"part-residual": "residual", "part-inline-rank": "rank"}
    for c in CLASSES:
        want["part-layout " + c] = c
    out = {}
    for line in open(spec_path, encoding="utf-8"):
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        name = cells[0].strip("`")
        if name not in want:
            continue
        cell = cells[col]
        if "†" in cell or cell.startswith("—"):
            out[want[name]] = None
        else:
            m = re.search(r"`([^`]+)`", cell)
            out[want[name]] = m.group(1) if m else None
    missing = [k for k in want if want[k] not in out]
    if missing:
        sys.exit("evaluator: tuning.md §5.4 has no row for %s" % ", ".join(missing))
    return out


def resolve(controls, spec_path):
    """Row K and the measured group, as the spec's prose states them."""
    caller = {"residual": None, "rank": None}
    caller.update({c: None for c in CLASSES})
    col = 3
    for a in controls:
        if a.startswith("--part-layout="):
            for item in a.split("=", 1)[1].split(","):
                k, v = item.split(":")
                caller[k] = v
        elif a.startswith("--part-inline-rank="):
            caller["rank"] = a.split("=", 1)[1]
        elif a.startswith("--part-residual="):
            caller["residual"] = a.split("=", 1)[1]
        elif a.startswith("--tune="):
            col = TUNE_COLS[a.split("=", 1)[1]]
    pre = presets(spec_path, col)
    r = {k: (caller[k] if caller[k] is not None else pre[k]) for k in caller}
    why = None
    rank_set = False
    if r["rank"] == "measured":
        # No compile carries a measurement set: theta_hot is absent (T1).
        r["rank"] = "none"
        why = "threshold-unmeasured"
    trivial = (all(r[c] in (None, "auto") for c in CLASSES) and
               r["rank"] in (None, "none") and r["residual"] in (None, "auto"))
    return r, why, rank_set, trivial


def strip_attrs(text):
    text = re.sub(r"__attribute__\(\((always_inline|noinline|noclone)\)\)\s*", "", text)
    return re.sub(r"\binline\s+", "", text)


def functions_and_calls(cfile, workdir):
    """The call graph at `-O0 -fno-inline` (no IPA pass may fold a call away,
    which `-O2` does to a part that returns a constant): {function: callees}."""
    o = os.path.join(workdir, "graph.o")
    r = run([CC, "-O0", "-fno-inline", "-c", cfile, "-o", o])
    if r.returncode:
        sys.exit("evaluator: the stripped copy does not compile:\n" + r.stderr)
    d = run(["objdump", "-dr", "--no-show-raw-insn", o]).stdout
    graph, cur = {}, None
    for line in d.splitlines():
        m = re.match(r"^[0-9a-f]+ <([\w.]+)>:$", line)
        if m:
            cur = m.group(1)
            graph.setdefault(cur, set())
            continue
        # A call to a function in another section is a relocation; one in
        # the same section is resolved by the assembler and only the call
        # instruction's target names it.
        m = (re.search(r"R_X86_64_(?:PLT32|PC32)\s+([\w.]+)-0x4", line) or
             re.search(r"\bcall\s+[0-9a-f]+ <([\w.]+)>", line))
        if m and cur:
            graph[cur].add(m.group(1))
    return graph


def definitions(text):
    """{function: (head line, body text)} for every top-level definition."""
    defs = {}
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^(?:static\s+)?(?:inline\s+)?(?:__attribute__\(\(\w+\)\)\s+)*"
                     r"[\w\s\*]*?\b(\w+)\(", lines[i])
        if (m and m.group(1) not in ("__attribute__", "_Static_assert") and
                not lines[i].rstrip().endswith(";") and
                not lines[i].startswith((" ", "\t", "#", "__attribute__"))):
            j, depth, body, started = i, 0, [], False
            while j < len(lines):
                body.append(lines[j])
                depth += lines[j].count("{") - lines[j].count("}")
                if "{" in lines[j]:
                    started = True
                if started and depth <= 0:
                    break
                j += 1
            defs[m.group(1)] = (lines[i], "\n".join(body))
            i = j + 1
            continue
        i += 1
    return defs


def gcc_copies(text, fn, workdir):
    """copyable(fn), asked of gcc itself (§2.1 H1/H2: its own refusal is the
    fact): the default text with `fn`'s definition forced always_inline
    compiles, or gcc refuses it as a body that "can never be copied" (a label
    table) or "can never be inlined" (a computed goto)."""
    head = re.compile(r"^static (int %s\()" % re.escape(fn), re.M)
    lines = [l for l in text.split("\n")]
    out, done = [], False
    for l in lines:
        if not done and head.match(l) and not l.rstrip().endswith(";"):
            l = head.sub(r"static inline __attribute__((always_inline)) \1", l)
            done = True
        out.append(l)
    if not done:
        sys.exit("evaluator: no definition head for %s" % fn)
    probe = os.path.join(workdir, "base", "probe.c")
    with open(probe, "w") as f:
        f.write("\n".join(out))
    r = run([CC, "-O2", "-c", probe, "-o", os.path.join(workdir, "probe.o")])
    if r.returncode == 0:
        return True
    if "can never be copied" in r.stderr or "can never be inlined" in r.stderr:
        return False
    sys.exit("evaluator: the copyable probe failed for another reason:\n" + r.stderr)


def main():
    pcrec, spec, workdir, cmap, rmap, pattern = sys.argv[1:7]
    controls = sys.argv[7:]
    flags = [a for a in controls if not a.startswith("--part-")]
    os.makedirs(workdir, exist_ok=True)
    classes = dict(kv.split("=") for kv in cmap.split(",") if kv)
    ranks = {k: int(v[1]) for k, v in (kv.split("=") for kv in rmap.split(",") if kv)}
    # One file name in two directories: the artifact names its own header.
    for d in ("base", "art"):
        os.makedirs(os.path.join(workdir, d), exist_ok=True)
    base = os.path.join(workdir, "base", "x.c")
    art = os.path.join(workdir, "art", "x.c")
    r = run([pcrec, "-p", "rx", "--features", "all"] + flags + ["-o", base, "--pattern", pattern])
    if r.returncode:
        sys.exit("evaluator: the default compile refused: " + r.stderr)
    r = run([pcrec, "-p", "rx", "--features", "all"] + controls + ["-o", art, "--pattern", pattern])
    if r.returncode:
        sys.exit("evaluator: the controlled compile refused: " + r.stderr)
    btext = open(base).read()
    atext = open(art).read()
    bdefs = definitions(btext)
    stripped = os.path.join(workdir, "base", "stripped.c")   # beside x.h
    with open(stripped, "w") as f:
        f.write(strip_attrs(btext))
    graph = functions_and_calls(stripped, workdir)
    owners_inline = {fn for fn, (head, _) in bdefs.items() if "always_inline" in head}
    resolved, why, rank_set, trivial = resolve(controls, spec)
    bad = []
    subjects = [fn for fn, c in classes.items() if c != "owned"]
    expect, held = {}, {c: False for c in CLASSES}
    present = {c: False for c in CLASSES}
    for fn in subjects:
        if fn not in graph:
            continue
        cls = classes[fn]
        present[cls] = True
        callers = {g for g, cs in graph.items() if fn in cs and g != fn}
        changed = True
        while changed:
            changed = False
            for g in list(callers):
                if g in owners_inline:
                    callers.discard(g)
                    callers |= {h for h, cs in graph.items() if g in cs and h != g}
                    changed = True
        copyable = gcc_copies(btext, fn, workdir)
        if trivial:
            expect[fn] = None
            continue
        cv = resolved[cls]
        thr = {"R3": 3, "R2": 2, "R1": 1, "R0": 0}.get(resolved["rank"] or "", -1)
        if not copyable:
            e, h = "shared", True                          # P2
        elif len(callers) == 1:
            e, h = None, True                              # P3
        elif cv in ("shared", "inline", "auto"):
            e, h = (None if cv == "auto" else cv), False   # P4-P6
        elif thr >= 0 and ranks.get(fn, -1) >= thr:
            e, h = "inline", False                         # P7
        elif resolved["residual"] in ("shared", "inline"):
            e, h = resolved["residual"], False             # P8-P9
        else:
            e, h = None, False                             # P10
        expect[fn] = e
        if h:
            held[cls] = True
    # The expected stamps.
    stamp = None
    if not trivial:
        parts = []
        if resolved["residual"]:
            parts.append("residual=" + resolved["residual"])
        if resolved["rank"]:
            parts.append("rank=" + resolved["rank"] + ("@set" if rank_set else ""))
        for c in CLASSES:
            if resolved[c]:
                parts.append("%s=%s%s" % (c, resolved[c],
                             "/none" if not present[c] else "/held" if held[c] else ""))
        stamp = ";".join(parts)
    got = re.search(r'#define RX_PART_LAYOUT "([^"]*)"', atext)
    gwhy = re.search(r'#define RX_PART_LAYOUT_WHY "([^"]*)"', atext)
    if (got.group(1) if got else None) != stamp:
        bad.append("stamp: expected %r, artifact %r" % (stamp, got.group(1) if got else None))
    if (gwhy.group(1) if gwhy else None) != why:
        bad.append("why: expected %r, artifact %r" % (why, gwhy.group(1) if gwhy else None))
    if trivial:
        rest = [l for l in atext.split("\n") if not l.startswith("#define RX_PART_LAYOUT")]
        if rest != btext.split("\n"):
            bad.append("T0: the artifact differs from the default beyond the WHY line")
    # Judge the real object.
    o = os.path.join(workdir, "art.o")
    r = run([CC, "-O2", "-Wall", "-Wextra", "-Werror", "-c", art, "-o", o])
    if r.returncode:
        bad.append("the controlled artifact does not compile: " + r.stderr.strip()[:300])
    else:
        syms = run(["nm", o]).stdout
        local = set(re.findall(r" t (\S+)$", syms, re.M))
        allsyms = set(re.findall(r" \w (\S+)$", syms, re.M))
        for fn, e in expect.items():
            if e == "shared" and fn not in local:
                bad.append("%s: expected shared (one local symbol), absent" % fn)
            if e == "inline" and fn in allsyms:
                bad.append("%s: expected inline (no symbol), present" % fn)
            if e == "shared":
                clones = [s for s in allsyms
                          if re.match(re.escape(fn) + r"\.(constprop|isra|part)\b", s)]
                if clones:
                    bad.append("%s: shared part cloned: %s" % (fn, ",".join(clones)))
    for b in bad:
        print("MISMATCH %s [%s]: %s" % (pattern, " ".join(controls), b))
    if bad:
        sys.exit(1)
    print("OK %s [%s] %s" % (pattern, " ".join(controls),
          ",".join("%s=%s" % (f, e or "-") for f, e in sorted(expect.items()))))


if __name__ == "__main__":
    main()
