#!/usr/bin/env python3
"""docs/dev/optloop/nullanch/pcre2_cells.py -- [NULLABLE-ANCH] BUILD (lane
nullanch1): the libpcre2 10.46 transcript for the five movers, and the
`.rxt` blocks written FROM it (oracle first: every m/n/g line below is the
oracle's answer, never pcrec's). tests/base/nullable_anch.rxt is this
script's `--rxt` output plus its hand-written header.

Usage: pcre2_cells.py ORACLE_BIN SCRATCH_DIR [--rxt]
ORACLE_BIN is tests/fuzz/pcre2_oracle.c built against libpcre2-8 10.46."""
import os, subprocess, sys

# (pattern, features, python-verifiable, comment, [(startpos, subject)]).
# A GIVE-UP block's pattern is libpcre2-inconclusive (-47, U4); its answer is
# read off the LANGUAGE-EQUAL pattern in `EQUAL` instead (and python's, below).
EQUAL = {r"^(([a-z]+)*)+$": r"^[a-z]*$", r"^(\s+)*$": r"^\s*$"}
NEAR17 = "a" * 17 + "!"
SP32 = " " * 32 + "x"
CELLS = [
    (r"^(([a-z]+)*)+$", None, True,
     "bench capability evil-alt-nested: short hits, a near-miss, the final-newline arm of `$`, and a start past 0",
     [(0, ""), (0, "abc"), (0, "abc\n"), (0, "\n"), (0, "ab!"), (0, "a b"),
      (0, "aaaaaaaa!"), (0, "x\ny"), (1, "abc")]),
    (r"^(([a-z]+)*)+$", None, False,
     "THE GIVE-UP CELL: 17 letters and a non-letter. Before this row the default artifact had no prefilter and its VM gave up (PCREC_ERR_STEPS, ~2.2 s); the exact hybrid prefilter now dismisses it. python's backtracking `re` takes seconds here, hence pcre2-only",
     [(0, NEAR17)]),
    (r"^(\s+)*$", None, True,
     "bench capability trim-nested-star",
     [(0, ""), (0, "    "), (0, "  x"), (0, "\n"), (0, " \t \n"), (0, "x"), (2, "    ")]),
    (r"^(\s+)*$", None, False,
     "THE GIVE-UP CELL: 32 blanks and a non-blank (the default VM gave up before this row); pcre2-only for python's cost",
     [(0, SP32)]),
    (r"^(a{2,4})?$", None, True,
     "corpus d27_edge mover",
     [(0, ""), (0, "aa"), (0, "aaaaa"), (0, "\n"), (0, "aa\n"), (0, "aab"), (1, "aa")]),
    (r"^(a?)(?1)*$", "recursion", False,
     "corpus sr_define/k69/quantified mover (a subroutine call: python has none)",
     [(0, ""), (0, "aaaa"), (0, "aaab"), (0, "\n"), (0, "aa\n"), (0, "b"), (1, "aa")]),
    (r"^(?:(?<g>a?)){0}(?&g)*+$", "recursion,named-groups,atomic-groups", False,
     "corpus quantified mover (a subroutine call under a possessive star)",
     [(0, ""), (0, "aaa"), (0, "aab"), (0, "\n"), (0, "aa\n"), (1, "aa")]),
]


def esc(b):
    out = []
    for ch in b:
        if ch == "\n": out.append("\\n")
        elif ch == "\t": out.append("\\t")
        elif ch == '"': out.append('\\"')
        elif ch == "\\": out.append("\\\\")
        else: out.append(ch)
    return "".join(out)


def oracle(binp, scratch, pat, subj, sp):
    f = os.path.join(scratch, "subj")
    with open(f, "wb") as h:
        h.write(subj.encode())
    r = subprocess.run([binp, pat, f, str(sp)], capture_output=True, timeout=120)
    return r.stdout.decode().strip()


def main():
    binp, scratch = sys.argv[1:3]
    rxt = "--rxt" in sys.argv[3:]
    os.makedirs(scratch, exist_ok=True)
    for pat, feats, py, note, subs in CELLS:
        if rxt:
            print("# " + note)
            if not py:
                print("# pcre2-only")
            print("pattern " + pat)
            if feats:
                print("features " + feats)
        for sp, s in subs:
            ans = oracle(binp, scratch, pat, s, sp)
            if rxt and ans.startswith("inconclusive") and pat in EQUAL:
                ans = oracle(binp, scratch, EQUAL[pat], s, sp)
            if not rxt:
                print(f"{pat}\tstart={sp}\t\"{esc(s)}\"\t{ans}")
                continue
            f = ans.split()
            if f[0] == "match":
                pre = f"ms {sp} " if sp else "m "
                print(f"{pre}\"{esc(s)}\" {f[1]} {f[2]}")
                for k in range(1, (len(f) - 1) // 2):
                    print(f"g {k} {f[1 + 2 * k]} {f[2 + 2 * k]}")
            elif f[0] == "nomatch":
                print((f"ns {sp} " if sp else "n ") + f"\"{esc(s)}\"")
            else:
                sys.exit(f"oracle gave no verdict for {pat!r} on {s!r}: {ans}")
        if rxt:
            print()
    if rxt:
        return
    # THE GIVE-UP CELLS' ORACLE. libpcre2 10.46 answers -47 (match limit,
    # docs/dev/upstream_issues.md U4) on both, so each is checked two other
    # ways: libpcre2 on the LANGUAGE-EQUAL pattern (a nested run of a class
    # under `^...$` is that class starred), and python `re` on the pattern
    # itself, which answers in seconds (U19).
    import re, time
    for pat, s in ((r"^(([a-z]+)*)+$", NEAR17), (r"^(\s+)*$", SP32)):
        eqv = EQUAL[pat]
        t = time.time()
        py = re.search(pat, s)
        dt = time.time() - t
        print(f"{pat}\t\"{esc(s)}\"\tlibpcre2 on {eqv}: "
              f"{oracle(binp, scratch, eqv, s, 0)}\tpython re: "
              f"{'nomatch' if py is None else py.span()} ({dt:.1f} s)")


if __name__ == "__main__":
    main()
