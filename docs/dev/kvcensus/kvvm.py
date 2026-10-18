"""kvcensus: the VM consumer's leading literal prefix, read off `--emit-ir`
(docs/spec/ir_listing.md's `#section program`, the emitter's own walk).

From L0, follow the straight line: a `label` row continues, a `goto` continues
at its target only when the next row is a label (an unconditional jump, not a
dispatch), and a `consume`/`compare` followed by `fail` is one test whose
success continues at its target. Anything else STOPS the prefix: a choice
(push, dispatch, island), an `assert` (an interleaved assertion), a `note`
(a meter charge or a backreference compare), `accept`, and -- in the strict
reading -- a `set` (a capture slot written on the way).

Returns (lit, cls, relaxed_lit, relaxed_cls):
  lit         leading LITERAL byte tests (a quoted `'x'` consume, a `compare`)
  cls         leading literal OR single-position class tests
  relaxed_*   the same, but a `set slot <- scan_position` row (a capture open
              whose value is the attempt start plus the bytes so far, a
              compile-time expression) does not stop the walk
"""
import re


def program(listing):
    rows, on = [], False
    for ln in listing.split("\n"):
        if ln.startswith("#section"):
            on = ln.split()[1] == "program"
            continue
        if not on or not ln or ln.startswith("#"):
            continue
        f = ln.split("\t")
        while len(f) < 5:
            f.append("")
        rows.append(dict(label=f[0], op=f[1], args=f[2], target=f[3], note=f[4]))
    return rows


def prefix(rows, relaxed=False):
    at = {r["label"]: i for i, r in enumerate(rows) if r["op"] == "label" and r["label"]}
    if "L0" not in at:
        return 0, 0
    i, lit, cls, lit_run, seen = at["L0"], 0, 0, True, set()
    while 0 <= i < len(rows):
        r = rows[i]
        op = r["op"]
        if op == "label":
            if "island" in r["note"] or "alternation" in r["note"]:
                break
            if i in seen:
                break
            seen.add(i)
            i += 1
            continue
        if op == "goto":
            nxt = rows[i + 1]["op"] if i + 1 < len(rows) else "label"
            if nxt != "label" or r["target"] not in at:
                break
            i = at[r["target"]]
            continue
        if op == "set" and relaxed and r["args"].endswith("<- scan_position"):
            i += 1
            continue
        if op in ("consume", "compare"):
            if i + 1 >= len(rows) or rows[i + 1]["op"] != "fail" or r["target"] not in at:
                break
            a = r["args"]
            m = re.search(r"\((\d+) bytes?\)", a)
            if op == "compare" and m and a.startswith("'") and "caseless" not in a:
                n, islit = int(m.group(1)), True
            elif op == "consume" and a.startswith("'"):
                n, islit = 1, True
            elif op == "consume" and a.startswith("["):
                n, islit = 1, False
            else:
                break
            cls += n
            if islit and lit_run:
                lit += n
            elif not islit:
                lit_run = False
            i = at[r["target"]]
            continue
        break
    return lit, cls


def vm_prefix(listing):
    rows = program(listing)
    a, b = prefix(rows, False)
    c, d = prefix(rows, True)
    return a, b, c, d
