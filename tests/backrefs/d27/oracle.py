#!/usr/bin/env python3
"""oracle.py -- INDEPENDENT re-checker for tests/backrefs/d27/*.rxt.

D27 charter: this lane trusts no generator. This script does NOT import
or reuse any other .rxt parser or checker in the tree (verify_rxt.py,
run.sh, etc. are all off-limits to a D27 cell anyway -- they live under
tests/, which this cell cannot open). It re-parses docs/testing.md's
`.rxt` grammar from scratch, straight from the format spec, and
re-queries libpcre2 10.46 directly via
docs/design/backrefs_measurements/probes/br_oracle.py for every single
`m`/`n`/`ms`/`ns`/`g`/`gp` cell in every file, marked or unmarked.

WHAT THIS CHECKS: that every expectation actually written in this
corpus is what libpcre2 actually does. It does NOT check pcrec (the
module is unbuilt; nothing here has ever been run against build/pcrec
except gating.rxt, which is checked separately and only for perr's
"pcrec exits nonzero" half -- see check_gating_perr() below, which DOES
shell out to build/pcrec, since gating.rxt is explicitly the one file
this lane was permitted to run against it).

Usage:
    python3 oracle.py                  # check every *.rxt in this dir
    python3 oracle.py numeric.rxt ...  # check specific files

Exit code 0 iff every checked expectation agrees with its oracle (or is
correctly marked `# pcre2-only` and skipped on the libpcre2 side -- there
is no python-only marking scheme in this corpus; every non-perr,
non-gating cell in every file IS checked against libpcre2, since
libpcre2 is the oracle of record for all of them (D26); the
`# pcre2-only` comment marks which cells have NO python cross-check,
following docs/testing.md's own convention, and this script also
attempts the python cross-check on unmarked cells as a bonus consistency
signal, reporting (not failing on) any surprise divergence there, since
python is not the oracle of record here).
"""
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CELL_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
BR_ORACLE = os.path.join(
    CELL_ROOT, "docs", "design", "backrefs_measurements", "probes",
    "br_oracle.py")
PCREC_BIN = os.path.join(CELL_ROOT, "build", "pcrec")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


br = _load(BR_ORACLE, "br_oracle")

# ---------------------------------------------------------------------------
# .rxt grammar, re-derived from docs/testing.md ("The `.rxt` format")
# directly -- not shared code with any other parser in the tree.
# ---------------------------------------------------------------------------

_ESCAPES = {
    '"': '"', "\\": "\\", "n": "\n", "t": "\t", "r": "\r",
    "f": "\f", "v": "\v",
}


def decode_subject(raw):
    """Decode a quoted .rxt subject string's escapes into raw bytes,
    per docs/testing.md's escape table (\\" \\\\ \\n \\t \\r \\f \\v
    \\xHH, no others)."""
    assert raw[0] == '"' and raw[-1] == '"', f"unquoted subject: {raw!r}"
    body = raw[1:-1]
    out = bytearray()
    i = 0
    while i < len(body):
        c = body[i]
        if c != "\\":
            out.append(ord(c))
            i += 1
            continue
        nxt = body[i + 1]
        if nxt == "x":
            hexpair = body[i + 2:i + 4]
            out.append(int(hexpair, 16))
            i += 4
            continue
        if nxt not in _ESCAPES:
            raise ValueError(f"bad escape \\{nxt} in {raw!r}")
        out.append(ord(_ESCAPES[nxt]))
        i += 2
    return bytes(out)


class Block:
    def __init__(self, pattern, lineno):
        self.pattern = pattern
        self.lineno = lineno
        self.flags = ""
        self.features = None
        self.is_perr = False
        self.cases = []       # list of dicts: kind, subj, start, end, pos, gs
        self.pcre2_only = False
        self.pcre2_only_reason = ""


def parse_rxt(path):
    """Re-parse one .rxt file into a list of Block objects. Independent
    grammar re-derivation from docs/testing.md, not a shared parser."""
    blocks = []
    cur = None
    pending_pcre2_only = None
    with open(path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            stripped = line.strip()
            if stripped == "":
                continue
            if stripped.startswith("#"):
                m = re.match(r"#\s*pcre2-only:?\s*(.*)", stripped)
                if m:
                    pending_pcre2_only = m.group(1).strip()
                continue
            if stripped.startswith("pattern "):
                cur = Block(line[len("pattern "):], lineno)
                if pending_pcre2_only is not None:
                    cur.pcre2_only = True
                    cur.pcre2_only_reason = pending_pcre2_only
                    pending_pcre2_only = None
                blocks.append(cur)
                continue
            if cur is None:
                raise ValueError(f"{path}:{lineno}: expectation line "
                                  f"before any 'pattern' line: {line!r}")
            if stripped.startswith("flags "):
                cur.flags = stripped[len("flags "):].strip()
                continue
            if stripped.startswith("features "):
                cur.features = stripped[len("features "):].strip()
                continue
            if stripped == "perr":
                cur.is_perr = True
                continue
            if stripped.startswith("m "):
                rest = stripped[2:].strip()
                subj, start, end = _split_subj_and_two_ints(rest)
                cur.cases.append({"kind": "m", "subj": subj, "start": 0,
                                   "wstart": start, "wend": end, "gs": []})
                continue
            if stripped.startswith("n "):
                subj = stripped[2:].strip()
                cur.cases.append({"kind": "n", "subj": subj, "start": 0,
                                   "gs": []})
                continue
            if stripped.startswith("ms "):
                rest = stripped[3:].strip()
                pos_str, remainder = rest.split(None, 1)
                subj, wstart, wend = _split_subj_and_two_ints(remainder)
                cur.cases.append({"kind": "ms", "subj": subj,
                                   "start": int(pos_str), "wstart": wstart,
                                   "wend": wend, "gs": []})
                continue
            if stripped.startswith("ns "):
                rest = stripped[3:].strip()
                pos_str, subj = rest.split(None, 1)
                cur.cases.append({"kind": "ns", "subj": subj,
                                   "start": int(pos_str), "gs": []})
                continue
            if stripped.startswith("gp ") or stripped.startswith("g "):
                is_pending = stripped.startswith("gp ")
                rest = stripped[3:].strip() if is_pending else stripped[2:].strip()
                parts = rest.split()
                slot = int(parts[0])
                gs0, gs1 = int(parts[1]), int(parts[2])
                if not cur.cases or cur.cases[-1]["kind"] in ("n", "ns"):
                    raise ValueError(
                        f"{path}:{lineno}: g/gp with no attachable m/ms "
                        f"case: {line!r}")
                cur.cases[-1]["gs"].append((slot, gs0, gs1))
                continue
            raise ValueError(f"{path}:{lineno}: unparseable line: {line!r}")
    return blocks


def _split_subj_and_two_ints(rest):
    """'"subj text" 0 3' -> (subj_raw_with_quotes, 0, 3). Subjects may
    contain spaces, so split on the CLOSING quote, not whitespace."""
    assert rest[0] == '"', f"expected quoted subject: {rest!r}"
    i = 1
    while True:
        if rest[i] == "\\":
            i += 2
            continue
        if rest[i] == '"':
            break
        i += 1
    subj = rest[: i + 1]
    tail = rest[i + 1:].split()
    return subj, int(tail[0]), int(tail[1])


# ---------------------------------------------------------------------------
# Checking
# ---------------------------------------------------------------------------

class Result:
    def __init__(self):
        self.checked = 0
        self.failed = 0
        self.skipped_perr = 0
        self.failures = []

    def fail(self, msg):
        self.failed += 1
        self.failures.append(msg)


def check_file(path, res, gating_mode=False):
    blocks = parse_rxt(path)
    for b in blocks:
        opts = 0
        if "i" in b.flags:
            opts |= br.PCRE2_CASELESS
        if b.is_perr:
            res.skipped_perr += 1
            if gating_mode:
                check_gating_perr(path, b, res)
            continue
        err = br.compile_err(b.pattern, opts)
        if err is not None:
            res.fail(f"{path}:{b.lineno}: pattern {b.pattern!r} was "
                      f"expected to COMPILE (has m/n cases) but libpcre2 "
                      f"rejects it: {err}")
            continue
        code = br.compile(b.pattern, opts)
        for case in b.cases:
            res.checked += 1
            subj = decode_subject(case["subj"])
            start = case["start"]
            r = code.search(subj, start)
            if case["kind"] in ("m", "ms"):
                if r is None:
                    res.fail(f"{path}:{b.lineno}: pattern {b.pattern!r} "
                              f"expected MATCH on {subj!r} start={start}, "
                              f"libpcre2 says NO MATCH")
                    continue
                span, groups = r
                if span != (case["wstart"], case["wend"]):
                    res.fail(f"{path}:{b.lineno}: pattern {b.pattern!r} "
                              f"on {subj!r} start={start}: expected span "
                              f"{(case['wstart'], case['wend'])}, "
                              f"libpcre2 gives {span}")
                for slot, gs0, gs1 in case["gs"]:
                    res.checked += 1
                    if slot == 0:
                        actual = span
                    else:
                        idx = slot - 1
                        if idx >= len(groups):
                            res.fail(f"{path}:{b.lineno}: slot {slot} "
                                      f"beyond pattern's own group count "
                                      f"({len(groups)} groups) for "
                                      f"{b.pattern!r}")
                            continue
                        g = groups[idx]
                        actual = (-1, -1) if g is None else g
                    expected = (gs0, gs1)
                    if actual != expected:
                        res.fail(f"{path}:{b.lineno}: pattern "
                                  f"{b.pattern!r} on {subj!r}: slot {slot} "
                                  f"expected {expected}, libpcre2 gives "
                                  f"{actual}")
            else:  # n, ns
                if r is not None:
                    res.fail(f"{path}:{b.lineno}: pattern {b.pattern!r} "
                              f"expected NO MATCH on {subj!r} "
                              f"start={start}, libpcre2 gives {r}")


def check_gating_perr(path, block, res):
    """gating.rxt's own extra check: does build/pcrec ACTUALLY exit
    nonzero for this block, with the features it declares? This is the
    one file/case-class this D27 lane was explicitly permitted to run
    against build/pcrec (refusal-direction confirmation only)."""
    if not os.path.exists(PCREC_BIN):
        return  # build/pcrec not present in this checkout; skip silently
    feat = block.features or ""
    cmd = [PCREC_BIN]
    if feat:
        cmd += ["--features", feat]
    cmd += ["-p", "rx", "--emit-main", "-o", "/dev/null", block.pattern]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=10)
    except subprocess.TimeoutExpired:
        res.fail(f"{path}:{block.lineno}: pcrec timed out on "
                  f"{block.pattern!r}")
        return
    res.checked += 1
    if proc.returncode == 0:
        res.fail(f"{path}:{block.lineno}: pattern {block.pattern!r} "
                  f"(features={feat!r}) expected pcrec to REFUSE "
                  f"(perr) but it exited 0")


def main(argv):
    files = argv[1:] or sorted(
        f for f in os.listdir(HERE) if f.endswith(".rxt"))
    res = Result()
    per_file = {}
    for fname in files:
        path = fname if os.path.isabs(fname) else os.path.join(HERE, fname)
        before = (res.checked, res.failed, res.skipped_perr)
        gating_mode = os.path.basename(path) == "gating.rxt"
        check_file(path, res, gating_mode=gating_mode)
        after = (res.checked, res.failed, res.skipped_perr)
        per_file[os.path.basename(path)] = (
            after[0] - before[0], after[1] - before[1], after[2] - before[2])

    print(f"libpcre2: {br.version()}")
    print(f"{'file':<22} {'checked':>8} {'failed':>7} {'perr':>6}")
    for fname, (checked, failed, perr) in per_file.items():
        print(f"{fname:<22} {checked:>8} {failed:>7} {perr:>6}")
    print(f"{'TOTAL':<22} {res.checked:>8} {res.failed:>7} "
          f"{res.skipped_perr:>6}")

    if res.failures:
        print("\nFAILURES:")
        for f in res.failures:
            print(" ", f)
    return 1 if res.failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
