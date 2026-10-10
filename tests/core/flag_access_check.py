#!/usr/bin/env python3
"""[FLAG-ACCESS] the option word's reader census as a gate.

Every read of `pcrec_options.flags` under src/, cli/ and lib/ goes through
the four accessors in src/core/internal.h (`pcrec_flags_has`, `pcrec_opt_has`,
`pcrec_flags_masked`, `pcrec_flags_without`). This check refuses a raw read
(`flags & PCREC_X`, `x & PCREC_X`, `r->deny & flags`, `flags & ~mask`)
anywhere outside the accessor block, which internal.h brackets with the
`FLAG-ACCESS-BEGIN` / `FLAG-ACCESS-END` marker comments.

THE CONTROL SHARES NOTHING WITH THE THING IT CONTROLS. The key population
(which macros are option bits) is read from lib/pcrec.h's own
`PCREC_BIT(n)` definitions, not from the accessor or the call sites; the
detector is proved by SELF-TEST FIXTURES that live in this file as literals
(lines that MUST be flagged and lines that MUST NOT), run through the same
detector before the tree is scanned; and two POPULATION floors make a scan
that silently saw nothing a failure (learnings.md section 3, K35):
the number of option bits parsed and the number of accessor call sites seen.

Usage: flag_access_check.py ROOT     (exit 0 clean, 1 findings, 2 setup error)
"""
import os
import re
import sys

BEGIN = "FLAG-ACCESS-BEGIN"
END = "FLAG-ACCESS-END"
MIN_BITS = 50          # lib/pcrec.h defines 55 PCREC_BIT keys at this writing
MIN_ACCESSOR_USES = 55 # the census at the lane: 63 reads replaced

def strip_noise(text):
    """Blank comments and string/char literals, keeping line structure."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join("\n" if ch == "\n" else " " for ch in text[i:j]))
            i = j
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == "\\" else 1
            j = min(j + 1, n)
            out.append("".join("\n" if ch == "\n" else " " for ch in text[i:j]))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)

def option_keys(pcrec_h):
    """Names of the option-word keys: every macro/enumerator bound to PCREC_BIT(n)."""
    txt = strip_noise(open(pcrec_h, encoding="utf-8").read())
    keys = set(re.findall(r"\b(PCREC_[A-Z0-9_]+)\s*=\s*PCREC_BIT\s*\(", txt))
    keys |= set(re.findall(r"#\s*define\s+(PCREC_[A-Z0-9_]+)\s+PCREC_BIT\s*\(", txt))
    return keys

def make_detector(keys):
    key = "(?:" + "|".join(sorted(keys)) + ")"
    amp = r"(?<!&)&(?![&=])"
    pats = [
        re.compile(amp + r"\s*[~(]*\s*" + key + r"\b"),          # x & PCREC_KEY
        re.compile(r"\b" + key + r"\b[\s)]*" + amp),             # PCREC_KEY & x
        re.compile(r"\b\w*flags\b\s*" + amp),                    # flags & anything
        re.compile(r"\bfl\b\s*" + amp),                          # the local word `fl`
        re.compile(amp + r"\s*~?\s*\(?\s*[\w>.\-\[\]]*flags\b"), # anything & flags
        re.compile(r"\bdeny\b[\w>.\-\[\]]*\s*" + amp + r"\s*[\w>.\-\[\]]*flags"),
    ]
    addr = re.compile(r"([(,=]|\breturn)\s*&(?!&)")
    def hit(line):
        if "RF_" in line:       # registry-row flags are a different word
            return False
        line = addr.sub(r"\1 ", line)   # unary address-of is not a mask
        return any(p.search(line) for p in pats)
    return hit

# lines that MUST be flagged / MUST NOT be, proved before the scan
MUST_FLAG = [
    "if (cx->opt->flags & PCREC_NO_COUNTER) return;",
    "x = (opts.flags & PCREC_UCP) != 0;",
    "if (PCREC_TRACE & f) y();",
    "if (cand->deny & flags) continue;",
    "return (flags & ~strategy_denials);",
    "d = cx->opt->flags & pf_deny[f];",
    "q->a = !(fl & PCREC_NO_POSS_CTX_FOLLOW);",
]
MUST_PASS = [
    "if (pcrec_opt_has(cx->opt, PCREC_NO_COUNTER)) return;",
    "opt.flags |= PCREC_UCP;",
    "opt.flags &= ~PCREC_SIZE_CAP_REFUSE;",
    "if (a && flags) go();",
    "if (r->flags & RF_INDEX) continue;",
    "uint64_t m = pcrec_flags_masked(flags, k);",
    "else if (cli_axis_apply(a, &opt.flags)) { }",
]

def scan(root, hit):
    findings, uses = [], 0
    use_re = re.compile(r"\bpcrec_(?:opt|flags)_(?:has|masked|without)\s*\(")
    for top in ("src", "cli", "lib"):
        for dp, dn, fn in os.walk(os.path.join(root, top)):
            for f in sorted(fn):
                if not f.endswith((".c", ".h", ".inc", ".def")):
                    continue
                path = os.path.join(dp, f)
                raw = open(path, encoding="utf-8", errors="replace").read()
                lines = raw.split("\n")
                skip = set()
                inside = False
                for i, l in enumerate(lines):
                    if BEGIN in l: inside = True
                    if inside: skip.add(i)
                    if END in l: inside = False
                clean = strip_noise(raw).split("\n")
                for i, l in enumerate(clean):
                    if i in skip:
                        continue
                    uses += len(use_re.findall(l))
                    if hit(l):
                        findings.append((os.path.relpath(path, root), i + 1, lines[i].strip()))
    return findings, uses

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    keys = option_keys(os.path.join(root, "lib", "pcrec.h"))
    if len(keys) < MIN_BITS:
        print(f"FAIL: parsed only {len(keys)} option keys from lib/pcrec.h (floor {MIN_BITS})")
        return 2
    hit = make_detector(keys)
    for l in MUST_FLAG:
        if not hit(strip_noise(l)):
            print(f"FAIL: self-test: detector missed a raw read: {l}")
            return 2
    for l in MUST_PASS:
        if hit(strip_noise(l)):
            print(f"FAIL: self-test: detector flagged a clean line: {l}")
            return 2
    findings, uses = scan(root, hit)
    for p, ln, t in findings:
        print(f"FAIL: raw option-word read outside the accessors: {p}:{ln}: {t}")
    if uses < MIN_ACCESSOR_USES:
        print(f"FAIL: saw only {uses} accessor uses (floor {MIN_ACCESSOR_USES}): the scan is not reaching the tree")
        return 2
    if findings:
        return 1
    print(f"PASS: flag_access_check: {len(keys)} option keys, {uses} accessor uses, 0 raw reads")
    return 0

sys.exit(main())
