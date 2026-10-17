#!/usr/bin/env python3
"""tests/findings/structural_check.py — the findings seam's STRUCTURAL rules
(docs/design/findings/design.md §6.3 "The structural check", §11.7), read off
the source text ([FINDINGS] B1).

  S1  NO READER TESTS A RATE [D126 Q4]. No function that calls a
      `pcrec_find_*` function may test a rate pointer (`!rate`, `rate ==
      NULL`, `rate != NULL`, `NULL == rate`) or the encoding (`bytekey`,
      `PCREC_ENC_`) — except the four PRIMITIVES, whose bodies ARE the one
      place each question kind spells its NONE answer.
  S2  NO RATE TABLE OUTSIDE src/core/findings.c. No identifier spelling a
      frequency table (`byte_freq`, `freq_ppm`, `_ppm_tbl`) anywhere else
      under src/.
  S3  NO TABLE POINTER IN A *Sel STRUCT (R39): no member of a struct whose
      typedef name ends in `Sel` is a `uint32_t *`/`unsigned *` pointer.
  S4  THE MEMO HAS NO OUTSIDE READER ([WINDOW-E1] C-E1-6, window_contract.md
      §3.7.1): the consumption record's memo fields (`byte_rate_have`,
      `_status`, `_block`, `_via`, `_bundle`, `_digest` and `byte_rate[]`)
      are named by a member access (`.f` / `->f`) nowhere under src/, cli/
      or lib/ but src/core/findings.c. The memo is filled by whoever derives
      first, the ask or the analysis object's offer, so a reader outside the
      seam that read it would consume without ASKING: its artifact would
      depend on data its stamp does not name. `byte_rate_asked` is not a
      memo field (it IS the ask).

WHAT IT CANNOT SEE (coding_guide §5 item 4): a function is found by a
top-level `name(...) {` line and its body by brace depth, so a call through a
function POINTER or a macro that expands to a `pcrec_find_*` call is invisible
to S1; S2 is a name filter and sees only those three spellings. Each rule
reports its population, and an EMPTY one is a failure (K35): S1 must find the
known readers, or it has stopped reaching them.

Usage: structural_check.py ROOT     (prints PASS:/FAIL: lines, exit 1 on any FAIL)
"""
import os
import re
import sys

ROOT = sys.argv[1]
PRIMITIVES = {"pcrec_find_pick", "pcrec_find_no_commoner",
              "pcrec_find_set_mass", "pcrec_find_seq_mass"}
# The readers S1 must reach, by name: if one of these is not found calling a
# pcrec_find_* function, the scan has stopped seeing the population it exists
# for (a witness that stopped reaching its site, [MECH-REACH]).
KNOWN_READERS = {"pcrec_find_set_pick", "pcrec_find_run_scan_index",
                 "pcrec_find_run_window_start", "pcrec_find_set_ppm",
                 "pcrec_req_window", "pcrec_req_pick", "req_byte_dominated_by"}
RATE_TEST = re.compile(r"!\s*rate\b|\brate\s*[!=]=\s*NULL|NULL\s*[!=]=\s*rate\b"
                       r"|\bbytekey\b|PCREC_ENC_")
FN_HEAD = re.compile(r"^[A-Za-z_][\w \*]*?\b(\w+)\s*\([^;]*$")

fails = 0


def ok(m):
    print("PASS: " + m)


def bad(m):
    global fails
    fails += 1
    print("FAIL: " + m)


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


# A brace inside a string or character literal is emitted text, not code, and
# so is a `/*` inside one: `functions` counts depth over braces, so S1 reads a
# text with comments AND literals blanked in ONE left-to-right pass (a comment
# opener inside a literal is not a comment). With `strip_comments` alone,
# `emit_search_head`'s emitted function head `"...)\n{\n"` opened a body that
# ran on for thousands of lines, and the day [START-LANDING] SL2 moved where
# the stray closer sat it swallowed `req_byte_dominated_by`, so S1 lost a known
# reader (lane sltri, 2026-10-10).
TOKEN = re.compile(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\\n])*"' r"|'(?:\\.|[^'\\\n])*'", re.S)


def code_only(text):
    def blank(m):
        t = m.group(0)
        return t[0] * 2 if t[0] in "\"'" else "\n" * t.count("\n")
    return TOKEN.sub(blank, text)


def functions(text):
    """(name, body) for every top-level function definition."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        m = FN_HEAD.match(lines[i])
        if m and not lines[i].startswith((" ", "\t", "#")):
            # find the opening brace at column 0 or end of a header line
            j = i
            while j < len(lines) and "{" not in lines[j] and ";" not in lines[j]:
                j += 1
            if j < len(lines) and "{" in lines[j] and ";" not in lines[j].split("{")[0]:
                depth, k, body = 0, j, []
                while k < len(lines):
                    depth += lines[k].count("{") - lines[k].count("}")
                    body.append(lines[k])
                    if depth == 0:
                        break
                    k += 1
                out.append((m.group(1), "\n".join(body)))
                i = k + 1
                continue
        i += 1
    return out


srcs = []
for d, _, fs in os.walk(os.path.join(ROOT, "src")):
    for f in fs:
        if f.endswith(".c"):
            srcs.append(os.path.join(d, f))

# S1
readers, s1bad = set(), 0
for path in sorted(srcs):
    rel = os.path.relpath(path, ROOT)
    for name, body in functions(code_only(open(path, encoding="latin-1").read())):
        if name in PRIMITIVES and rel == "src/core/findings.c":
            continue
        calls = set(re.findall(r"\b(pcrec_find_\w+)\s*\(", body)) - {name}
        if not calls:
            continue
        readers.add(name)
        hit = RATE_TEST.search(body)
        if hit:
            s1bad += 1
            bad(f"S1 {rel}: {name}() calls {', '.join(sorted(calls))} and tests "
                f"'{hit.group(0)}' — a reader must hand the rate to a primitive "
                "untested; the NONE answer is the primitive's (findings design §6.3)")
missing = KNOWN_READERS - readers
if missing:
    bad("S1 the scan no longer reaches reader(s) " + ", ".join(sorted(missing)) +
        " — the check has lost its population, or a reader stopped asking")
elif not s1bad:
    ok(f"S1 no reader tests a rate or the encoding ({len(readers)} functions "
       "call the findings seam, the 4 primitives exempt)")

# S2
s2 = 0
for path in sorted(srcs):
    rel = os.path.relpath(path, ROOT)
    if rel == "src/core/findings.c":
        continue
    for n, line in enumerate(strip_comments(open(path, encoding="latin-1").read()).split("\n"), 1):
        m = re.search(r"\b\w*(byte_freq|freq_ppm|_ppm_tbl)\w*\b", line)
        if m:
            s2 += 1
            bad(f"S2 {rel}:{n}: '{m.group(0)}' — a rate table outside "
                "src/core/findings.c (findings design §11.7)")
if not s2:
    ok(f"S2 no rate-table identifier outside src/core/findings.c ({len(srcs) - 1} files scanned)")

# S3
hdrs = [os.path.join(d, f) for d, _, fs in os.walk(os.path.join(ROOT, "src"))
        for f in fs if f.endswith((".h", ".c"))]
nsel, s3 = 0, 0
for path in hdrs:
    text = strip_comments(open(path, encoding="latin-1").read())
    for m in re.finditer(r"typedef struct\s*\w*\s*\{([^{}]*)\}\s*(\w+Sel)\s*;", text):
        nsel += 1
        if re.search(r"\b(uint32_t|unsigned|uint64_t)\s*(const\s*)?\*", m.group(1)):
            s3 += 1
            bad(f"S3 {os.path.relpath(path, ROOT)}: {m.group(2)} carries a table "
                "pointer (R39: a row predicate reaches the rate through the accessor)")
if nsel == 0:
    bad("S3 found no *Sel struct at all — the check has lost its population")
elif not s3:
    ok(f"S3 no *Sel struct carries a table pointer ({nsel} structs)")

# S4
MEMO = re.compile(r"(?:\.|->)\s*(byte_rate(?:_have|_status|_block|_via|_bundle|_digest)?)\b(?!\s*\()")
s4, inside = 0, 0
for d in ("src", "cli", "lib"):
    for dd, _, fs in os.walk(os.path.join(ROOT, d)):
        for f in fs:
            if not f.endswith((".c", ".h")):
                continue
            path = os.path.join(dd, f)
            rel = os.path.relpath(path, ROOT)
            text = code_only(open(path, encoding="latin-1").read())
            for n, line in enumerate(text.split("\n"), 1):
                for m in MEMO.finditer(line):
                    if rel == "src/core/findings.c":
                        inside += 1
                        continue
                    s4 += 1
                    bad(f"S4 {rel}:{n}: reads the memo field '{m.group(1)}' outside "
                        "src/core/findings.c — ask the accessor (window_contract.md §3.7.1)")
if inside == 0:
    bad("S4 found no memo read even in src/core/findings.c — the check has lost its population")
elif not s4:
    ok(f"S4 the consumption record's memo is read only in src/core/findings.c ({inside} reads there)")

sys.exit(1 if fails else 0)
