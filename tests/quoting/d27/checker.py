#!/usr/bin/env python3
"""D27 quoting corpus checker -- INDEPENDENT of gen_corpus.py.

Re-parses every .rxt file in this directory from scratch (its own small
parser, not gen_corpus.py's in-memory Block objects) and re-queries
oracle_probe for every expectation, reporting agreement. This is what the
manager (or anyone else) runs to re-verify the corpus without trusting the
generator's own bookkeeping.

Run:
    python3 checker.py [dir]        (default: this script's directory)

Requires oracle_probe already built (see oracle_probe.c's header for the
build command) at ./oracle_probe next to this script, or set ORACLE env var.

Exit status: 0 if every cell agreed with the oracle, 1 otherwise.
"""
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
ORACLE = os.environ.get("ORACLE", os.path.join(HERE, "oracle_probe"))
TIMEOUT_BIN = "gnutimeout"


def run_oracle(args):
    cmd = [TIMEOUT_BIN, "20", ORACLE] + list(args)
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("oracle_probe failed (rc=%d) for %r: %s" % (p.returncode, args, p.stderr.decode("utf8", "replace")))
    return p.stdout.decode("utf8", "replace").rstrip("\n")


def oracle_compile(pattern, flags):
    out = run_oracle(["compile", pattern, flags])
    return out.split()[0] == "OK"


def oracle_match(pattern, flags, subject, startpos):
    out = run_oracle(["match", pattern, flags, subject, str(startpos)])
    parts = out.split()
    kind = parts[0]
    if kind == "MATCH":
        n = int(parts[1])
        vals = [int(x) for x in parts[2:]]
        pairs = [(vals[2 * i], vals[2 * i + 1]) for i in range(n)]
        return ("MATCH", pairs)
    return (kind, None)


# --- subject decoding, independent re-implementation of the .rxt escape
# table (docs/spec/rxt_format.md: \" \\ \n \t \r \f \v \xHH) ---
def decode_subject(quoted):
    assert quoted[0] == '"' and quoted[-1] == '"', "subject not quoted: %r" % quoted
    body = quoted[1:-1]
    out = []
    i = 0
    while i < len(body):
        c = body[i]
        if c == '\\':
            nc = body[i + 1]
            if nc == '"':
                out.append('"'); i += 2
            elif nc == '\\':
                out.append('\\'); i += 2
            elif nc == 'n':
                out.append('\n'); i += 2
            elif nc == 't':
                out.append('\t'); i += 2
            elif nc == 'r':
                out.append('\r'); i += 2
            elif nc == 'f':
                out.append('\f'); i += 2
            elif nc == 'v':
                out.append('\v'); i += 2
            elif nc == 'x':
                hexpair = body[i + 2:i + 4]
                out.append(chr(int(hexpair, 16)))
                i += 4
            else:
                raise AssertionError("unknown subject escape \\%s in %r" % (nc, quoted))
        else:
            out.append(c)
            i += 1
    return "".join(out)


class ParsedBlock:
    def __init__(self, pattern):
        self.pattern = pattern
        self.flags = ""
        self.features = None
        self.name = None
        self.is_perr = False
        self.cases = []  # list of dicts: kind m/n/ms/ns, subject, startpos, start, end, groups=[(slot,s,e)]


def parse_rxt(path):
    """Minimal, independent .rxt body parser: only the productions this
    corpus's own files use (pattern/name/flags/features/perr/m/n/ms/ns/g/gp
    and whole-line # comments). No head support needed -- every file here
    has no head (first non-comment line is 'pattern')."""
    blocks = []
    cur = None
    last_m_case = None
    with open(path) as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith("#"):
                continue
            parts = line.split(None, 1)
            kw = parts[0]
            rest = parts[1] if len(parts) > 1 else ""
            if kw == "pattern":
                if cur:
                    blocks.append(cur)
                # rest-of-line verbatim after exactly one space
                cur = ParsedBlock(line[len("pattern "):])
                last_m_case = None
            elif kw == "name":
                cur.name = rest
            elif kw == "flags":
                cur.flags = rest.strip()
            elif kw == "features":
                cur.features = rest.strip()
            elif kw == "perr":
                cur.is_perr = True
            elif kw in ("m", "n", "ms", "ns"):
                if kw in ("m", "n"):
                    p = rest.split(None, 1)
                    subj_and_rest = p[1] if len(p) > 1 else p[0]
                    startpos = 0
                    body = rest
                else:
                    toks = rest.split(None, 1)
                    startpos = int(toks[0])
                    body = toks[1]
                # body is: "<subject>" [<start> <end>]  -- extract the
                # quoted subject (handling escaped quotes) then trailing ints
                assert body[0] == '"'
                i = 1
                while True:
                    if body[i] == '\\':
                        i += 2
                        continue
                    if body[i] == '"':
                        break
                    i += 1
                quoted = body[0:i + 1]
                trailer = body[i + 1:].split()
                subject = decode_subject(quoted)
                case = {"kind": kw, "subject": subject, "startpos": startpos}
                if kw in ("m", "ms"):
                    case["start"] = int(trailer[0])
                    case["end"] = int(trailer[1])
                    case["groups"] = []
                    last_m_case = case
                else:
                    last_m_case = None
                cur.cases.append(case)
            elif kw in ("g", "gp"):
                toks = rest.split()
                slot, s, e = int(toks[0]), int(toks[1]), int(toks[2])
                assert last_m_case is not None, "%s:%d: %s with no preceding m/ms case" % (path, lineno, kw)
                last_m_case["groups"].append((kw, slot, s, e))
            else:
                raise AssertionError("%s:%d: unknown line kind %r" % (path, lineno, kw))
    if cur:
        blocks.append(cur)
    return blocks


def check_file(path):
    blocks = parse_rxt(path)
    total_cases = 0
    total_blocks = 0
    fails = []
    for b in blocks:
        total_blocks += 1
        if b.is_perr:
            total_cases += 1
            ok = oracle_compile(b.pattern, b.flags)
            if ok:
                fails.append("%s: pattern %r expected PERR but oracle compiled it OK" % (path, b.pattern))
            continue
        for case in b.cases:
            total_cases += 1
            kind, pairs = oracle_match(b.pattern, b.flags, case["subject"], case["startpos"])
            if case["kind"] in ("n", "ns"):
                if kind != "NOMATCH":
                    fails.append("%s: pattern %r subject %r startpos %d expected NOMATCH, oracle said %s" %
                                  (path, b.pattern, case["subject"], case["startpos"], kind))
                continue
            # m / ms
            if kind != "MATCH":
                fails.append("%s: pattern %r subject %r startpos %d expected MATCH %d %d, oracle said %s" %
                              (path, b.pattern, case["subject"], case["startpos"], case["start"], case["end"], kind))
                continue
            s0, e0 = pairs[0]
            if (s0, e0) != (case["start"], case["end"]):
                fails.append("%s: pattern %r subject %r startpos %d: corpus says %d %d, oracle says %d %d" %
                              (path, b.pattern, case["subject"], case["startpos"], case["start"], case["end"], s0, e0))
            for (directive, slot, s, e) in case["groups"]:
                total_cases += 1
                if slot >= len(pairs):
                    fails.append("%s: pattern %r: %s slot %d >= oracle ovector count %d" %
                                  (path, b.pattern, directive, slot, len(pairs)))
                    continue
                gs, ge = pairs[slot]
                if (gs, ge) != (s, e):
                    fails.append("%s: pattern %r: %s slot %d: corpus says %d %d, oracle says %d %d" %
                                  (path, b.pattern, directive, slot, s, e, gs, ge))
    return total_blocks, total_cases, fails


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else HERE
    files = sorted(glob.glob(os.path.join(directory, "*.rxt")))
    if not files:
        print("no .rxt files found under %s" % directory)
        return 1
    grand_blocks = 0
    grand_cases = 0
    grand_fails = []
    for path in files:
        nb, nc, fails = check_file(path)
        grand_blocks += nb
        grand_cases += nc
        grand_fails.extend(fails)
        status = "OK" if not fails else "FAIL (%d)" % len(fails)
        print("%-40s blocks=%-3d cases=%-3d %s" % (os.path.basename(path), nb, nc, status))
    print()
    print("TOTAL: %d files, %d blocks, %d cases, %d failures" % (len(files), grand_blocks, grand_cases, len(grand_fails)))
    if grand_fails:
        print()
        print("FAILURES:")
        for f in grand_fails:
            print("  " + f)
        return 1
    print("AGREEMENT: 100%% (%d/%d cells)" % (grand_cases, grand_cases))
    return 0


if __name__ == "__main__":
    sys.exit(main())
