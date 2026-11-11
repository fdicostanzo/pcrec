#!/usr/bin/env python3
"""Self-test for occurrence_oracle.py: hand-written rows from the contract alone.
Run: python3 -I tests_oracle/selftest.py"""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ORACLE = os.path.join(HERE, "occurrence_oracle.py")
sys.path.insert(0, HERE)
import occurrence_oracle as O  # noqa: E402


def setx(*bytes_):
    """Encode a set by the iface rule: byte b is bit b%4 of hex digit 63 - b//4."""
    d = [0] * 64
    for b in bytes_:
        d[63 - b // 4] |= 1 << (b % 4)
    return "".join("%x" % x for x in d)


A, B = setx(97), setx(98)
X = setx(*range(256))


def row(subject, sets, origin, c, reads="", omin=0, vlo=0, vlen=None, call="entry"):
    if vlen is None:
        vlen = len(sets)
    return "\t".join(["s", call, subject.encode("latin-1").hex(), str(origin), str(omin),
                      ",".join(sets), str(vlo), str(vlen), str(c), reads])


# (name, row, expected set of violated items)
CASES = [
    # item 1
    ("1 ok: c at floor", row("xxab", [A, B], 1, 2, "2,3"), set()),
    ("1 bad: c below floor", row("abab", [A, B], 3, 0, "0,1"), {1}),
    ("1 ok: omin<0 candidate before origin", row("abab", [A, B], 2, 0, "0,1", omin=-2), set()),
    ("1 bad: omin<0 candidate below origin+omin", row("abab", [A, B], 3, 0, "0,1", omin=-1), {1}),
    ("1 bad: negative candidate", row("abab", [A, B], 0, -1, "", omin=0), {1, 3}),
    # negative omin, origin < -omin: floor clamps to 0, no wrap
    ("clamp ok: c=0 with origin 1 omin -3", row("abab", [A, B], 1, 0, "0,1", omin=-3), set()),
    ("clamp bad: MISS though occurrence at 0", row("abab", [A, B], 1, "MISS", "", omin=-3), {2}),
    ("clamp ok: MISS, none exists", row("zzzz", [A, B], 1, "MISS", "", omin=-3), set()),
    # item 2
    ("2 ok: least", row("ababab", [A, B], 0, 0, "0,1"), set()),
    ("2 bad: occurrence before c", row("ababab", [A, B], 0, 2, "2,3"), {2}),
    ("2 bad: partial verify, whole-run occurrence before c", row("abxa", [A, B], 0, 3, "3", vlen=1), {2}),
    ("2 ok: partial verify, no whole occurrence before c", row("acab", [A, B], 0, 2, "2", vlen=1), set()),
    ("2 ok: occurrence before floor is not counted", row("ababab", [A, B], 1, 2, "2,3"), set()),
    ("2 ok: truncated run at end is no occurrence", row("xxa", [A, B], 0, 2, "2", vlen=1), set()),
    # MISS
    ("miss bad: occurrence at floor", row("ab", [A, B], 0, "MISS", ""), {2}),
    ("miss bad: occurrence after floor", row("abab", [A, B], 1, "MISS", "2"), {2}),
    ("miss ok: occurrence only before floor", row("abab", [A, B], 3, "MISS", "3"), set()),
    ("miss ok: floor past the subject", row("abab", [A, B], 10, "MISS", ""), set()),
    # item 3
    ("3 ok: whole verified", row("xxab", [A, B], 0, 2, "2,3"), set()),
    ("3 bad: position 0 fails", row("xxab", [A, B], 0, 0, "0,1"), {3}),
    ("3 bad: position 1 fails", row("aaab", [A, B], 0, 1, "1,2"), {3}),
    ("3 ok: verified extent is the tail only", row("zb", [A, B], 0, 0, "1", vlo=1, vlen=1), set()),
    ("3 bad: verified tail fails", row("za", [A, B], 0, 0, "1", vlo=1, vlen=1), {3}),
    ("3 bad: verified position past the subject", row("a", [A, B], 0, 0, "0"), {3}),
    ("3 ok: ver_len 0, unverified candidate", row("zz", [A, B], 0, 0, "", vlen=0), set()),
    ("3 ok: ver_len n, longer subject", row("qab", [A, B], 0, 1, "1,2", vlo=0, vlen=2), set()),
    # item 4
    ("4 ok: reads inside", row("abab", [A, B], 0, 0, "0,1,2,3"), set()),
    ("4 bad: read at n", row("abab", [A, B], 0, 0, "0,1,4"), {4}),
    ("4 bad: read below 0", row("abab", [A, B], 1, 0, "-1,0,1", omin=-1), {4}),
    ("4 bad: read outside on a MISS", row("zz", [A, B], 0, "MISS", "2"), {4}),
    ("4 bad: empty subject, any read", row("", [A], 0, "MISS", "0"), {4}),
    # empty subject, long run, ver extents
    ("empty ok: MISS, no reads", row("", [A], 0, "MISS", ""), set()),
    ("empty bad: a candidate in an empty subject", row("", [A], 0, 0, "", vlen=0), {1}),
    ("long run ok: MISS", row("ab", [A, B, A, B], 0, "MISS", "0,1"), set()),
    ("long run bad: verified past the subject", row("ab", [A, B, A, B], 0, 0, "0,1"), {3}),
    ("ver_len n bad vs ok handled above; ver_len 0 floor edge", row("zzzz", [A], 2, 2, "", vlen=0), set()),
    # item 5: re-entry is the same contract with lo as origin
    ("5 ok: reentry at lo", row("xabab", [A, B], 2, 3, "3,4", call="reentry"), set()),
    ("5 bad: reentry candidate below lo", row("xabab", [A, B], 3, 1, "1,2", call="reentry"), {1}),
    ("5 bad: reentry reads below 0", row("xabab", [A, B], 2, 1, "-1,1,2", omin=-1, call="reentry"), {4}),
    # bit order, hand-built hex
    ("bit: byte 0", row("\x00", ["0" * 63 + "1"], 0, 0, "0"), set()),
    ("bit: byte 255", row("\xff", ["8" + "0" * 63], 0, 0, "0"), set()),
    ("bit: byte 4 is not byte 1", row("\x01", ["0" * 62 + "10"], 0, 0, "0"), {3}),
    ("bit: 'a' hand-built", row("a", ["0" * 39 + "2" + "0" * 24], 0, 0, "0"), set()),
    ("bit: wrong byte rejected", row("b", [A], 0, 0, "0"), {3}),
    ("bit: wildcard", row("q", [X], 0, 0, "0"), set()),
]

MALFORMED = [
    ("9 columns", "s\tentry\t00\t0\t0\t%s\t0\t1\t0" % A),
    ("bad call", row("a", [A], 0, 0, call="rentry")),
    ("odd hex", row("a", [A], 0, 0).replace("\t61\t", "\t6\t")),
    ("upper hex subject", row("a", [A], 0, 0).replace("\t61\t", "\t6F\t")),
    ("short set", row("a", [A[:63]], 0, 0)),
    ("ver exceeds sets", row("a", [A], 0, 0, vlo=1, vlen=1)),
    ("negative origin", row("a", [A], -1, 0)),
    ("non-numeric result", row("a", [A], 0, "miss")),
    ("empty sets", row("a", [], 0, 0)),
    ("blank line", ""),
]


def check_cases():
    bad = 0
    for name, line, want in CASES:
        got = {i for i, _ in O.check_row(O.parse_row(line))}
        ok = got == want
        bad += not ok
        print("%s  %s  want=%s got=%s" % ("ok  " if ok else "FAIL", name, sorted(want), sorted(got)))
    return bad


def run_cli(text):
    p = subprocess.run([sys.executable, "-I", ORACLE], input=text, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def check_cli():
    bad = 0

    def expect(name, cond):
        nonlocal bad
        print("%s  %s" % ("ok  " if cond else "FAIL", name))
        bad += not cond

    for name, line in MALFORMED:
        rc, _, err = run_cli(O.HEADER + "\n" + line + "\n")
        expect("malformed refused (exit 2): " + name, rc == 2 and err != "")
    rc, _, _ = run_cli("")
    expect("empty input refused", rc == 2)
    rc, _, _ = run_cli(CASES[0][1] + "\n")
    expect("missing header refused", rc == 2)

    good, badrow = CASES[0][1], CASES[1][1]
    rc, out, _ = run_cli(O.HEADER + "\n" + good + "\n")
    expect("clean file: exit 0, trailer", rc == 0 and out.strip() == "oracle: rows=1 violations=0")
    rc, out, _ = run_cli(O.HEADER + "\n" + good + "\n" + badrow + "\n")
    lines = out.strip().split("\n")
    expect("one violating row: exit 1, VIOLATION line, rows counted",
           rc == 1 and lines[0].startswith("VIOLATION 1 s entry ") and lines[-1] == "oracle: rows=2 violations=1")
    return bad


if __name__ == "__main__":
    bad = check_cases() + check_cli()
    print("selftest: %s (%d failing)" % ("PASS" if bad == 0 else "FAIL", bad))
    sys.exit(1 if bad else 0)
