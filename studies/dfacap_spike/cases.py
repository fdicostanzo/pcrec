#!/usr/bin/env python3
"""cases.py -- the named hard cases, each differenced three ways over
exhaustive subjects: Pike VM (the TNFA's semantics), TDFA, pcrec --engine=vm,
all against libpcre2. Usage: python3 cases.py [maxlen] > results/cases.txt"""
import itertools
import sys

import oracle
import tdfa

# (name, pattern, flags, alphabet) -- alphabet None = the pattern's letters + 'x'
CASES = [
    # re2c's 2022 doubt: greedy and lazy arms fused
    ("lazy-fuse", rb"(a*)|(a*?)", "", None),
    ("lazy-fuse-rev", rb"(a*?)|(a*)", "", None),
    ("lazy-fuse-tail", rb"(?:(a*)|(a*?))b", "", None),
    ("lazy-fuse-seq", rb"(a*?)(a*)", "", None),
    ("lazy-fuse-seq2", rb"(a*)(a*?)b", "", None),
    ("lazy-plus", rb"(a+?)(a*)", "", None),
    ("lazy-alt-star", rb"(?:(a)|(ab))*?b", "", None),
    ("lazy-both", rb"(a*?)(b*?)(a*)", "", None),
    ("lazy-count", rb"(a{1,3}?)(a*)", "", None),
    ("lazy-opt", rb"(a??)(a?)", "", None),
    # last-iteration / restore-vs-clear
    ("last-iter-alt", rb"(a|ab)*", "", None),
    ("last-iter-nested", rb"((a)|b)+", "", None),
    ("last-iter-nested2", rb"(?:(a)|b)*", "", None),
    ("last-iter-two", rb"(?:(a)|(b))*", "", None),
    ("last-iter-opt", rb"(?:(a)?b)+", "", None),
    ("restore-opt", rb"(?:(a)?)+", "", None),
    ("restore-cls", rb"(?:(a)|b|)*c", "", None),
    # empty-iteration rule (K18)
    ("empty-opt-star", rb"(a?)*", "", None),
    ("empty-alt-star", rb"(|a)*", "", None),
    ("empty-alt-star2", rb"(a|)*", "", None),
    ("empty-star-plus", rb"(a*)+", "", None),
    ("empty-star-star", rb"(a*)*", "", None),
    ("empty-star-star-b", rb"(a*)*b", "", None),
    ("empty-lazy-star", rb"(a?)*?b", "", None),
    ("empty-nested", rb"((a*)*)*", "", None),
    ("empty-twogroups", rb"(a*)*(b*)*", "", None),
    ("empty-alt-nested", rb"(?:(a)|(b)|())*c", "", None),
    ("empty-plus-alt", rb"(|a)+", "", None),
    ("empty-count-min", rb"(|a){2,}", "", None),
    ("empty-count", rb"(a?){2,3}", "", None),
    ("empty-count-lazy", rb"(a?){2,3}?b", "", None),
    # POSIX-vs-leftmost classics
    ("posix-classic", rb"(a|ab)(c|bcd)(d*)", "", "abcd"),
    ("posix-classic2", rb"(a*)(ab)*(b*)", "", None),
    ("posix-classic3", rb"(a|ab)(bc|c)", "", None),
    ("prio-alt", rb"(a|ab|abc)(c?)", "", None),
    # nested quantified groups
    ("nested-1", rb"((a+)b)*", "", None),
    ("nested-2", rb"((a)(b)?)+", "", None),
    ("nested-3", rb"(a(b(c)?)*)+", "", None),
    ("nested-4", rb"((a|b)*c)+", "", None),
    ("nested-5", rb"(?:(a)(?:(b)|c))*", "", None),
    # bounded repeats without desugared tags (shared tag ids across copies)
    ("bounded-1", rb"(a){2,3}", "", None),
    ("bounded-2", rb"(a|b){1,3}c", "", None),
    ("bounded-3", rb"((a)|(b)){2}", "", None),
    ("bounded-4", rb"(a(b)?){2,4}", "", None),
    ("bounded-5", rb"(?:(a)|b){0,2}?a", "", None),
    ("bounded-6", rb"(a){0}b", "", None),
    # anchors
    ("anchor-1", rb"^(a*)(b?)$", "", None),
    ("anchor-2", rb"(a|b)*?\z", "", None),
    ("anchor-3", rb"(a*)$", "", "a\n"),
    ("anchor-4", rb"(a|\n)*?$", "", "a\n"),
    ("anchor-5", rb"^(?:(a)|b)*\Z", "", "ab\n"),
    # unanchored search with start tags
    ("search-1", rb"(b+)", "", None),
    ("search-2", rb"a(b*)c|(a)", "", None),
    ("search-3", rb"x*(a|b)", "", "abx"),
    # flags
    ("caseless", rb"(a+)(B)", "i", "aAbB"),
]


def alphabet_of(pat):
    al = sorted(set(chr(c) for c in pat if chr(c).isalnum()))
    return "".join(al) + "x"


def subjects(alpha, maxlen):
    for n in range(maxlen + 1):
        for t in itertools.product(alpha, repeat=n):
            yield "".join(t).encode()


def run_case(name, pat, flags, alpha, maxlen):
    alpha = alpha or alphabet_of(pat)
    nfa = tdfa.compile_pattern(pat, flags)
    dfa = tdfa.TDFA(nfa)
    plain = tdfa.TDFA(nfa, tagged=False)
    ref = oracle.Pcre2(pat, flags, False, nfa.ncap)
    subs = list(subjects(alpha, maxlen))
    vm, why = oracle.pcrec_vm(pat, flags, False, subs, tag=name)
    bad = {"pike": [], "tdfa": [], "vm": []}
    for k, s in enumerate(subs):
        want = ref.search(s)
        got_p = tdfa.pike(nfa, s)
        got_d = dfa.run(s)
        if got_p != want:
            bad["pike"].append((s, want, got_p))
        if got_d != want:
            bad["tdfa"].append((s, want, got_d))
        if vm is not None and vm[k] != want:
            bad["vm"].append((s, want, vm[k]))
    st = dfa.stats()
    verdict = "PASS" if not bad["tdfa"] and not bad["pike"] else "FAIL"
    print("%-20s %-26s %s  subjects=%d  tdfa_mism=%d pike_mism=%d vm_mism=%s  "
          "states=%d(untagged %d) regs=%d sets=%d copies=%d copy_trans=%d/%d tmp_trans=%d"
          % (name, pat.decode(), verdict, len(subs), len(bad["tdfa"]), len(bad["pike"]),
             len(bad["vm"]) if vm is not None else "n/a(" + why + ")",
             st["states"], plain.stats()["states"], st["regs"], st["sets"], st["copies"],
             st["copy_trans"], st["trans"], st["tmp_trans"]))
    for kind in ("pike", "tdfa", "vm"):
        for s, w, g in bad[kind][:3]:
            print("    %s %r: pcre2=%s got=%s" % (kind, s, w, g))
    return verdict


def main():
    maxlen = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    only = sys.argv[2:] if len(sys.argv) > 2 else None
    print("# libpcre2", oracle.pcre2_version(), " maxlen", maxlen)
    n = f = 0
    for name, pat, flags, alpha in CASES:
        if only and name not in only:
            continue
        n += 1
        if run_case(name, pat, flags, alpha, maxlen) != "PASS":
            f += 1
    print("# cases %d  fail %d" % (n, f))


if __name__ == "__main__":
    main()
