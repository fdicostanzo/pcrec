import importlib.util, os, sys
W = sys.argv[1]
os.environ.setdefault("PCREC_PCRE2_PATH", "libpcre2-8.so.0")
sp = importlib.util.spec_from_file_location("gh", os.path.join(W, "tests/litscan/gen_handoff.py"))
gh = importlib.util.module_from_spec(sp); sp.loader.exec_module(gh)
A = "a"
W_ = [
 ("W-L1 (span_arms §5.7 and §14.4 L3, the kit's witness): the run `foobar` begins 3 bytes before every match (K -3); the kit scans from max(0, startpos - 3), so a search from 2 or 3 finds the run at 0 and the match at 3; a scan from the start offset misses it",
  "(?<=foo)bar", "byte", ["foobar", "xfoobarfoobar", "foobafoobar", "fobar", "barfoo"]),
 ("W-L3 (span_arms §5.7, L3): the lookbehind's -1 term is the UNION of its branches, so the run is `bc` at -1; a term taken from the first branch claims `abc` at -2 and deletes `xbc`. Also the hybrid prefilter's first ask (l3feat finding: a neutral `landmark_position = search_from` moved the scan past every match)",
  "(?<=ab|b)c", "byte", ["xbc", "abc", "ac", "bcbc", "c"]),
 ("W-L10 (span_arms §5.7, A3, the BACK move): K -2; the body starts at max(startpos, c + 2); rev 1's move (the body at the hit) reports (2,7) from 3, before the start offset",
  "(?<=ab)ab[a-z]*q", "byte", ["abababq", "ababq", "xabq", "abq"]),
 ("W-L13 (span_arms §5.7, A8 entry row at signed K): the VM attempt loop's first attempt at max(startpos, c + 2); today's entry text attempts at the raw hit and answers (2,7) from 3",
  "(?<=ab)ab[a-z]*q(\\w*)\\1", "byte", ["abababq", "ababq", "abababqxx"]),
 ("W-L14 (span_arms §5.7, A8 re-entry row): stale only when the kept hit lies more than 2 before the attempt; the unsigned `landmark_position - pos > K` text moves the attempt BACK and re-runs it forever (the gate's timeout reports it)",
  "(?<=ab)ab(\\w)\\1", "byte", ["xababab-", "ababcc", "xabababb", "abab"]),
 ("W-L15 (span_arms §14.4 L3, review r51 READYL3-1): the entry guard is `k != 0 || round.len > 0`; with `k > 0 || ...` kept no move is emitted at K -1 and the attempt starts at the raw hit: (2,5) from 3 where the oracle gives (3,6)",
  "(?<=a)a(\\w)\\1", "byte", ["-aaaaaq-b", "aaa", "-aab"]),
 ("W-L16 (span_arms §14.4 L3, review r51 READYL3-4, a SAFETY witness, run under make asan too): the kit verifies `Content-` at the run's left end, inside the 16-byte lookbehind; on a subject that ends inside the lookbehind the end clamp answers NOMATCH, where `hit += 16` alone starts past the subject's end",
  "(?<=Content-Length: )\\d", "byte", ["xx Content-Length:", "Content-Length:", "Content-Length: 5", "Content-Length: x", "Content-"]),
 ("W-L17 (span_arms §14.4 L3, review r51 READYL3-6): the consumed extent of `foobar` at -6 is EMPTY (`\\d*x` gives `head` no byte), so no run pick: `req_byte` the set's `x` (120), the pin states nothing; run under make asan/ubsan too",
  "(?<=foobar)\\d*x", "byte", ["foobarx", "foobar12x", "fooba12x", "xfoobar9xfoobarx", "x"]),
 ("W-L18 (span_arms §14.4 L3, review r51 READYL3-6): the run `foo` at -3 consumes nothing: `req_byte` none; on `foo` the match is (3,3)",
  "(?<=foo)", "byte", ["foo", "xfoo", "fo", "foofoo"]),
 ("W-L19 (span_arms §14.4 L3, review r51 READYL3-6): a 32-byte lookbehind, the run `a^32` at -32 (the bound) with an empty extent",
  "(?<=a{32})b", "byte", [A * 32 + "b", A * 31 + "b", "x" + A * 32 + "bb", A * 40]),
 ("W-T3a (span_arms §5.7, L3): the run `a^20 b^8 z b^3` at -20, the kit's member `z`; a TOP `++` keeping the LAST positions states `a^12 b^8 z b^11` at -20 (truly -12) and the body starts 8 bytes late: NOMATCH",
  "(?<=aaaaaaaaaaaaaaaaaaaa)bbbbbbbbzbbbbbbbbbbb", "byte", [A * 20 + "b" * 8 + "z" + "b" * 11, "x" + A * 20 + "b" * 8 + "z" + "b" * 11, A * 19 + "b" * 8 + "z" + "b" * 11]),
 ("span_arms L3 under utf8 (D-11): B counts the lookbehind's BYTES, `é` two and `a` one, K -3",
  "(?<=éa)bc", "utf8", ["éabc", "xéabcéabc", "eabc", "ébc", "ééabc"]),
 ("span_arms L3, bench 333 (`(?<=\\xc3\\xa9)x`) under byte: the two-byte lookbehind is two positions, K -2",
  "(?<=\\xc3\\xa9)x", "byte", ["éx", "xéxx", "Ãx"]),

 ("span_arms L3, bench 258 (`(?<=item )done`): the run narrows from `done` to `item done` at K -5",
  "(?<=item )done", "byte", ["item done", "x item doneitem done", "item  done", "itemdone", "item don"]),
 ("span_arms L3, census note (c): `\\K` is zero-width, the run `ab` at -1 holds across it",
  "(?<=a)\\Kb", "byte", ["ab", "xabab", "b", "aab"]),
 ("span_arms L3, census note (c): `\\G` is zero-width; the run `ab` at -1",
  "(?<=\\Ga)b", "byte", ["ab", "aab", "xab", "b"]),
 ("span_arms L3 (READYL2-5): `(?<=foo)bar(?=baz)` stays `foobar` at -3 at L3 (the `++ rg` clause is L2's)",
  "(?<=foo)bar(?=baz)", "byte", ["foobarbaz", "foobarbax", "xfoobarbazfoobarbaz"]),
 ("W-D2 at L3 (span_arms §5.7): a dead pattern, now with BACK's run `bc` at -1; it still never matches",
  "(?<=ab)(?<=cb)c", "byte", ["abc", "cbc", "bc", "abcbc"]),
 ("span_arms L3, K -10 (§14.4 L3 hand pin): `(?<=e{10})eeeeeqzx`",
  "(?<=e{10})eeeeeqzx", "byte", ["e"*15 + "qzx", "e"*14 + "qzx", "xx" + "e"*16 + "qzxqzx"]),
]
out = []
for why, pat, enc, subs in W_:
    cells = []
    for s in subs:
        b = gh.bsubj(s, enc) if enc == "utf8" else s.encode("latin-1") if all(ord(c) < 256 for c in s) and not any(ord(c) > 127 for c in s) else s.encode("utf-8")
        pc = gh.pcre_cells(pat, enc, b)
        if enc == "byte" and not gh.pcre2_only(pat):
            py = gh.py_cells(pat, b)
            for q, v in pc.items():
                if py.get(q) != v:
                    sys.exit(f"ORACLES DISAGREE: {pat!r} {b!r} @{q}: pcre2 {v} python {py.get(q)}")
        cells.append((b, pc))
    for route in ("", "vm"):
        if enc == "utf8" or gh.pcre2_only(pat):
            out.append("# pcre2-only")
        out.append("# " + why + (" [engine vm]" if route else ""))
        out.append("pattern " + pat)
        out.append("features all")
        out.append("encoding " + enc)
        if route: out.append("engine vm")
        for b, pc in cells:
            for p, v in sorted(pc.items()):
                out.append('ms %d "%s" %d %d' % (p, gh.esc(b), v[0], v[1]) if v else 'ns %d "%s"' % (p, gh.esc(b)))
        out.append("")
print("\n".join(out))
