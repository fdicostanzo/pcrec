#!/usr/bin/env python3
"""sr_check.py -- re-verify every d27/*.rxt expectation against libpcre2.

DELIBERATELY NOT sr_gen.py's emitter run backwards. This program re-reads
the .rxt files as TEXT and re-parses them from docs/testing.md's format
section, so a generator bug that wrote a syntactically wrong line, attached
a g line to the wrong case, or emitted a subject whose escapes decode to
something other than what the oracle was asked about, is caught here rather
than agreed with. The oracle is the same one (there is only one for this
module -- D26, and the extract's own oracle rules say so plainly), but the
PARSE and the ATTACHMENT are independent.

Checks, per file and in total:
  1. every block's `pattern` compiles under libpcre2, or the block says
     `perr` -- and a `perr` block libpcre2 ACCEPTS must be one of the
     declared pcrec-only refusals, listed by pattern below, never a
     silent pass.
  2. every m/ms span equals the oracle's span at that startpos.
  3. every n/ns really is a nomatch at that startpos.
  4. every g line's slot span equals the oracle's group span for the
     attached case; RX_UNSET is -1 -1 and is symmetric.
  5. structural: a g line attaches to the most recent m/ms in the block and
     never to an n/ns or to nothing; a slot exceeds neither the pattern's
     own group count nor 0.
  6. every subject decodes through the documented escape table only.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)
_s = importlib.util.spec_from_file_location(
    "sr_oracle", os.path.join(CELL, "docs", "design",
                              "subroutines_measurements", "probes",
                              "sr_oracle.py"))
sr = importlib.util.module_from_spec(_s)
_s.loader.exec_module(sr)

# The ONLY blocks allowed to say `perr` while libpcre2 accepts the pattern:
# the [DD-14.LB] amendment's pcrec-only refusal. Listed by exact pattern so
# a new one cannot appear by accident.
PCREC_ONLY_PERR = {
    "^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$",
}

ESCAPES = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t', 'r': '\r',
           'f': '\f', 'v': '\v'}


def unquote(field, where, errs):
    """Decode one double-quoted .rxt subject; returns (text, rest)."""
    if not field.startswith('"'):
        errs.append("%s: subject does not start with a quote: %r"
                    % (where, field[:40]))
        return None, ""
    out = []
    i = 1
    while i < len(field):
        ch = field[i]
        if ch == '"':
            return "".join(out), field[i + 1:]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        i += 1
        if i >= len(field):
            errs.append("%s: trailing backslash in subject" % where)
            return None, ""
        e = field[i]
        if e in ESCAPES:
            out.append(ESCAPES[e])
            i += 1
        elif e == "x":
            h = field[i + 1:i + 3]
            if len(h) != 2 or any(c not in "0123456789abcdefABCDEF" for c in h):
                errs.append("%s: bad \\xHH escape %r" % (where, h))
                return None, ""
            out.append(chr(int(h, 16)))
            i += 3
        else:
            errs.append("%s: escape \\%s is not in the documented table"
                        % (where, e))
            return None, ""
    errs.append("%s: unterminated subject" % where)
    return None, ""


def check_file(path, errs, stats):
    pat = None
    ncap = 0
    compiled_ok = False
    saw_case = False           # a g line may attach only after m/ms
    last = None                # (subject, startpos) of the most recent m/ms
    block_line = 0
    seen_perr = False

    for lineno, raw in enumerate(open(path), 1):
        line = raw.rstrip("\n")
        where = "%s:%d" % (os.path.basename(path), lineno)
        if not line.strip() or line.lstrip().startswith("#"):
            if line.strip() and not line.startswith("#"):
                errs.append("%s: a comment must start at column 1" % where)
            continue
        head, _, rest = line.partition(" ")

        if head == "pattern":
            pat = rest
            block_line = lineno
            seen_perr = False
            saw_case = False
            last = None
            stats["blocks"] += 1
            e = sr.compile_err(pat, 0)
            compiled_ok = e is None
            ncap = (sr.ngroups(pat, 0) or 0) if compiled_ok else 0
            continue

        if pat is None:
            errs.append("%s: %r before any pattern line" % (where, head))
            continue

        if head in ("flags", "features", "engine", "budget"):
            if head == "features":
                stats["featlists"].add(rest)
            continue

        if head == "perr":
            seen_perr = True
            stats["perr"] += 1
            if compiled_ok and pat not in PCREC_ONLY_PERR:
                errs.append("%s: perr block, but libpcre2 ACCEPTS %r -- if "
                            "this is a pcrec-only refusal it must be "
                            "declared in PCREC_ONLY_PERR" % (where, pat))
            continue

        if seen_perr:
            errs.append("%s: %r follows a perr line in the same block"
                        % (where, head))
            continue

        if head in ("m", "n", "ms", "ns"):
            if head in ("ms", "ns"):
                sp_s, _, rest2 = rest.partition(" ")
                if not sp_s.isdigit():
                    errs.append("%s: startpos %r is not a non-negative "
                                "decimal integer" % (where, sp_s))
                    continue
                start = int(sp_s)
                rest = rest2
            else:
                start = 0
            subj, tail = unquote(rest, where, errs)
            if subj is None:
                continue
            if not compiled_ok:
                errs.append("%s: case on a pattern libpcre2 refuses: %r"
                            % (where, pat))
                continue
            got = sr.search(pat, subj, start, 0)
            if head in ("m", "ms"):
                stats[head] += 1
                nums = tail.split()
                if len(nums) != 2:
                    errs.append("%s: expected exactly two span numbers, got "
                                "%r" % (where, tail))
                    continue
                want = (int(nums[0]), int(nums[1]))
                if got is None:
                    errs.append("%s: file says match %s, libpcre2 says "
                                "NOMATCH -- pattern %r subject %r startpos "
                                "%d" % (where, want, pat, subj, start))
                elif got[0] != want:
                    errs.append("%s: file says match %s, libpcre2 says %s -- "
                                "pattern %r subject %r startpos %d"
                                % (where, want, got[0], pat, subj, start))
                saw_case = True
                last = (subj, start)
            else:
                stats[head] += 1
                if tail.strip():
                    errs.append("%s: a nomatch case takes no numbers: %r"
                                % (where, tail))
                if got is not None:
                    errs.append("%s: file says NOMATCH, libpcre2 says %s -- "
                                "pattern %r subject %r startpos %d"
                                % (where, got[0], pat, subj, start))
                saw_case = False
                last = None
            continue

        if head in ("g", "gp"):
            stats[head] += 1
            f = rest.split()
            if len(f) != 3:
                errs.append("%s: a %s line takes slot start end, got %r"
                            % (where, head, rest))
                continue
            slot, gs, ge = int(f[0]), int(f[1]), int(f[2])
            if (gs == -1) != (ge == -1):
                errs.append("%s: RX_UNSET is symmetric; a lone -1 is a "
                            "parse error" % where)
                continue
            if not saw_case or last is None:
                errs.append("%s: %s line with no preceding m/ms case in this "
                            "block (a nomatch has no captures)"
                            % (where, head))
                continue
            if slot < 0 or slot > ncap:
                errs.append("%s: slot %d is outside the pattern's own group "
                            "count %d for %r" % (where, slot, ncap, pat))
                continue
            subj, start = last
            got = sr.search(pat, subj, start, 0)
            if got is None:
                errs.append("%s: attached case does not match at all" % where)
                continue
            oracle = got[0] if slot == 0 else got[1][slot - 1]
            want = None if gs == -1 else (gs, ge)
            if oracle != want:
                errs.append("%s: g slot %d says %s, libpcre2 says %s -- "
                            "pattern %r subject %r startpos %d"
                            % (where, slot, want, oracle, pat, subj, start))
            continue

        if head == "gu":
            stats["gu"] += 1
            code, _, rest2 = rest.partition(" ")
            if code not in ("steps", "frames", "work", "recurse"):
                errs.append("%s: %r is not a gu code" % (where, code))
                continue
            if code == "recurse":
                errs.append("%s: gu recurse has no producer today and no "
                            "block may expect it (D71 item 1)" % where)
            subj, tail = unquote(rest2, where, errs)
            if subj is None:
                continue
            if tail.strip():
                errs.append("%s: a gu case takes no numbers: %r"
                            % (where, tail))
            saw_case = False
            last = None
            continue

        errs.append("%s: unknown directive %r" % (where, head))


def main():
    if sr.SELFCHECK:
        print("ORACLE SELFCHECK FAILED:", sr.SELFCHECK)
        return 1
    files = sorted(f for f in os.listdir(HERE) if f.endswith(".rxt"))
    if not files:
        print("no .rxt files in", HERE)
        return 1
    errs = []
    stats = dict(blocks=0, m=0, n=0, ms=0, ns=0, g=0, gp=0, gu=0, perr=0,
                 featlists=set())
    print("libpcre2:", sr.version())
    for f in files:
        before = len(errs)
        b0 = dict(stats)
        check_file(os.path.join(HERE, f), errs, stats)
        print("  %-22s blocks=%-4d m=%-4d n=%-4d ms=%-3d ns=%-3d g=%-5d "
              "gu=%-3d perr=%-3d  errors=%d"
              % (f, stats["blocks"] - b0["blocks"], stats["m"] - b0["m"],
                 stats["n"] - b0["n"], stats["ms"] - b0["ms"],
                 stats["ns"] - b0["ns"], stats["g"] - b0["g"],
                 stats["gu"] - b0["gu"], stats["perr"] - b0["perr"],
                 len(errs) - before))
    cases = stats["m"] + stats["n"] + stats["ms"] + stats["ns"] + stats["gu"]
    print("  TOTAL blocks=%d cases=%d (m=%d n=%d ms=%d ns=%d gu=%d) "
          "g=%d perr=%d  distinct feature lists=%d"
          % (stats["blocks"], cases, stats["m"], stats["n"], stats["ms"],
             stats["ns"], stats["gu"], stats["g"], stats["perr"],
             len(stats["featlists"])))
    if errs:
        print("\n%d CHECK FAILURE(S):" % len(errs))
        for e in errs[:80]:
            print("  *", e)
        if len(errs) > 80:
            print("  … and %d more" % (len(errs) - 80))
        return 1
    print("\nAll %d expectations re-verified against libpcre2 10.46." % (
        cases + stats["g"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
