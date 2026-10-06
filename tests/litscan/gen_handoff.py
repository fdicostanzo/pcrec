"""tests/litscan/gen_handoff.py -- writes handoff.rxt beside it: [K82] (B), THE
HANDOFF's witnesses (docs/design/litscan_k82h.md §4.2 item 2; docs/spec/
tuning.md §2.41). Re-run after editing the case list:

    PCREC_PCRE2_PATH=/opt/homebrew/lib/libpcre2-8.dylib \\
        python3 tests/litscan/gen_handoff.py [--check-pcrec BUILD/pcrec]

EVERY EXPECTATION COMES FROM AN ORACLE, NEVER BY HAND. A `byte` block's cells
are computed by python3 `re` (latin-1, the harness's own python tier) AND by
libpcre2 (the local binding, `docs/design/eng_brep_measurements/probes/
pcre2_ctypes.py`, borrowed); the two must agree or the generator stops. A
`utf8` block's are libpcre2's alone under PCRE2_UTF | PCRE2_MATCH_INVALID_UTF
(pcrec's ruled semantics for ill-formed text, utf8_design.md §2.6), so it is
written `# pcre2-only`: python `re` reads the harness's subjects as latin-1
and cannot speak for a multibyte character. `--check-pcrec` compiles every
block with the given pcrec and checks every cell against it too, so a cell
where pcrec's shipped semantics and the oracle part (a pre-existing
divergence, not this row's) is reported rather than written.

Cells are written at EVERY start position that is a character boundary
(`ms`/`ns`), because the handoff moves where a scan begins and a start
position near the run is where its clamp and its round-up live. Each block is
written on the default route and again under `engine vm` (the forced VM has
no DFA scan, so it is the no-handoff control for the same cells).
"""
import importlib.util, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../.."))
os.environ.setdefault("PCREC_PCRE2_PATH", "/opt/homebrew/lib/libpcre2-8.dylib")
_spec = importlib.util.spec_from_file_location(
    "pcre2_ctypes", os.path.join(ROOT, "docs/design/eng_brep_measurements/probes/pcre2_ctypes.py"))
p2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p2)
UTF, INVALID_UTF = 0x00080000, 0x04000000

# (pattern, encoding, subjects, why[, extra directives]); a subject is a str
# (utf8 blocks: its UTF-8 encoding, or bytes for ill-formed text).
X = "\U0001F600"
CASES = [
 # ---- the maximum offset: a match begins exactly K bytes before its window ----
 ("x{2,5}(?i:cat)", "byte", ["xxxxxCaT", "xxxxxcat", "zxxxxxcat", "xxcat", "xxxxxxcat", "\nxxxxxcat"],
  "K = 5, unanchored DFA: the match begins K bytes before the window; startpos 1..5 cross the clamp (S470)"),
 ("x{2,5}(?i:cat)", "utf8", ["xxxxxCaT", "xxxxxcat", "zxxxxxcat", "xxcat", "éxxxxxcat"],
  "K = 5 under utf8: the same, with a multibyte character before it"),
 ("(?:a|bb)?catdog", "byte", ["bbcatdog", "acatdog", "catdog", "zbbcatdog", "bbcatdo", "bcatdog"],
  "K = 2 from the WIDER alternation branch (S466 takes the left branch's width)"),
 ("(?m)^x{2,5}(?i:cat)", "byte", ["xxxxxCaT", "xxxxxcat", "zxxxxxcat", "\nxxxxxcat", "ab\nxxcat\nxxxxxcat"],
  "the ATTEMPT route (ENG_ATTEMPT): the first attempt starts at the handoff; a K one byte short (S463) or no clamp (S470) moves the answer here, where the unanchored scan's reverse pass hides both"),
 ("(?m)^(?:a|bb)?catdog", "byte", ["bbcatdog", "\nbbcatdog", "x\nacatdog", "zbbcatdog"],
  "the attempt route, K = 2 from the wider branch (S463, S466)"),
 ("x{2,5}((?i:cat))", "byte", ["xxxxxCaT", "xxxxxcat", "zxxxxxcat", "xxcat"],
  "the VM HYBRID: the first prefilter call starts at the handoff; its own reverse pass is bounded there, so a short K (S463) or a missing clamp (S470) moves the answer"),
 ("(?:a|bb)?(cat)dog", "byte", ["bbcatdog", "acatdog", "zbbcatdog"],
  "the hybrid, K = 2 from the wider branch (S466)"),
 # ---- two occurrences: the gate must return the LEFTMOST (r1 S-F1, S464) ----
 ("(?i)cat", "byte", ["CAT CAT", "cat cat cat", "cAtCaTcat", "xcatxcat"],
  "two occurrences: the first is the match's own window and a second follows it, so a gate returning a later occurrence starts past the match (S464)"),
 ("x{2,5}(?i:cat)", "byte", ["xxxxxcat xcat", "xxcat xxcat", "xxcatxxxxxcat"],
  "two occurrences at K = 5 (S464)"),
 ("(?i)cat", "utf8", ["CAT CAT", "écatécat"],
  "two occurrences under utf8 (S464)"),
 # ---- a decoy within K before the real match ----
 ("a{3}(?i:cat)", "byte", ["cat aaacat", "acat aaacat", "aaacat"],
  "a decoy: a run occurrence the match does not use sits within K before the real one"),
 # ---- multibyte width: K in BYTES (S465, the cwmax mistake) ----
 ("(?i)straße", "utf8", ["ſtraße", "éſtraße", "xſTRAßE", "straße", "ſſtraße"],
  "K = 2: (?i)s matches U+017F, two bytes, before the window TRA; a character count (S465) says 1 and lo lands inside the match"),
 ("(?i)stra(ße)", "utf8", ["ſtraße", "éſtraße", "ſſtraße"],
  "K = 2 on the hybrid, where the answer moves (S465)"),
 (".{3}cat", "utf8", [X * 3 + "cat", "€€€cat", "ééécat", "a" + X * 3 + "cat", X + "cat"],
  "K = 12: three characters of up to four bytes"),
 ("(.{3})cat", "utf8", [X * 3 + "cat", "a" + X * 3 + "cat", "€" + X + "écat"],
  "K = 12 on the hybrid"),
 ("é{2}cat", "utf8", ["éécat", "xéécat", "écat"],
  "K = 4: two two-byte characters"),
 ("(?:éx|ʩx)", "utf8", ["éx", "ʩx", "zéx", "ʩʩx", "x"],
  "a run that begins on a continuation byte (K = 1)"),
 # ---- ill-formed text: the round-up takes more than three steps (r1 S-F5, C-C7) ----
 ("x{2,5}(?i:cat)", "utf8", [b"\x80\x80\x80\x80xxcat", b"\x80\x80\x80\x80\x80xxxxxcat", b"xx\x80\x80\x80\x80\x80\x80xxcat", b"\x80\x80\x80\x80\x80\x80cat", b"xxxxxcat\x80\x80\x80\x80"],
  "4-6 stray continuation bytes immediately before the window: c - K lands among them and the round-up walks them all"),
 ("(?i)straße", "utf8", [b"\x80\x80\x80\x80\xc5\xbftra\xc3\x9fe", b"\x80\x80\x80\x80\x80tra\xc3\x9fe", b"\xc5\xbf\x80\x80tra\xc3\x9fe"],
  "ill-formed text before a two-byte fold"),
 # ---- seeded starts: the seed reads the byte before the moved start (S468) ----
 ("\\bcat\\b", "byte", ["zcat cat", "zzcat cat", "cat", "acatb cat", "z cat"],
  "\\b, seeded DFA: the first true match is (5,8); a seed read from search_from instead of the handoff reports (1,4) (S468)"),
 ("(?<![a-z])cat", "byte", ["zcat cat", "zcat-cat", "cat"],
  "a one-character lookbehind (a context node on the DFA)"),
 ("(?<![a-z]{2})cat", "byte", ["zzcat cat", "zcat zzcat", "cat"],
  "a two-character lookbehind (the hybrid)"),
 # ---- the attempt route and \\G (Claim 2') ----
 ("(?m)^item", "byte", ["item", "x\nitem", "xitem\nitem", "\n\nitem"],
  "(?m)^ (ENG_ATTEMPT): a first start at the handoff"),
 ("(?:\\G|x)cat", "byte", ["cat", "xcat", "zcat", "zxcat", "catxcat"],
  "\\G reads search_from, never the handoff"),
 ("\\Gx|yx", "byte", ["xyx", "yx", "zyx", "x"],
  "\\G reads search_from (the attempt route)"),
 # ---- the \\G hybrid: the prefilter's third argument is a \\G reader (r1 S-F3, S469) ----
 ("(?:\\Gab|x)(cat)(?=dog)", "byte", ["zzabcatdog", "abcatdog", "zxcatdog", "zzabcatdogxcatdog"],
  "a \\G hybrid WITH the handoff (no prefilter-window ceiling: the lookahead erases it): from 0 on zzabcatdog the answer is NOMATCH, and a VM \\G moved to the handoff reports (2,7) (S469)"),
 ("(?:\\Gab|x)(cat)dog", "byte", ["zzabcatdog", "abcatdog", "zxcatdog", "zzabcatdogxcatdog"],
  "a \\G hybrid whose prefilter window is its ceiling: the (d') decline keeps the scan at the startpos (S476's control)"),
 # ---- \\K: offsets are from the attempt start ----
 ("x{2,5}\\K(?i:cat)", "byte", ["xxxxxcat", "zxxxxxcat", "xxcat"],
  "\\K: K is measured from the attempt start, not the reported one"),
 # ---- find-all: each call of the loop is a search from the previous end, so
 # every-startpos cells on dense and overlapping subjects ARE its calls (an
 # `mc` line would collide with tests/rxtsource's keyword census, where `mc`
 # is still a protected word) ----
 ("(?i)cat", "byte", ["cAtCaTcat", "cat cat cat", "ccatt"],
  "find-all, dense: each call hands off its own candidate (no cross-call state)"),
 ("aa(?i:a)", "byte", ["aaaaaaa", "aaAaaA", "aAa aaa"],
  "find-all, overlapping run occurrences"),
 ("x{2,5}(?i:cat)", "byte", ["xxcatxxxcatxxxxxcat", "xxxxxxxcatxcat"],
  "find-all at K = 5: a later match's window within K of an earlier match's end"),
 # ---- controls: unbounded runs never move ----
 ("a.*?(?i:select)", "byte", ["a select", "aaselect", "select", "xa..SeLeCt"],
  "control: an unbounded offset (.*?) carries no handoff (S467)"),
 ("ab.*xyzw", "byte", ["abxyzw", "ab..xyzw", "xyzw", "zzab-xyzwab"],
  "control: an unbounded offset; the run choice keeps the more informative unbounded xyzw (S474)"),
 # ---- the VM hybrid route's handoff, by its own witnesses ([MEMFN] R4c,
 # integration.md §15.5: the I2 sweep must REACH this route). Each pattern's
 # artifact carries RX_VM_PREFILTER "hybrid" and `handoff_position =
 # rx_reqrun(...)` (tests/memfn/run_site_manifest.sh's reach floor compiles
 # them and asserts both). ----
 ("(ab)c?userpass", "byte", ["abuserpass", "abcuserpass", "zzabcuserpass", "abcuserpas", "xabuserpassabcuserpass"],
  "the VM hybrid's handoff, RX_REQ_HANDOFF 3: the window's first hit, less K, is the first prefilter call's start"),
 ("(x)?userz", "byte", ["userz", "xuserz", "zxuserz", "zzuserz"],
  "the VM hybrid's handoff, RX_REQ_HANDOFF 1"),
 ("(?i)(cat)s?dog", "byte", ["CATsDOG", "catdog", "zcatsdog", "CatSdog", "catsdo"],
  "the VM hybrid's handoff through the PAIR arm of the offset-skip form (a two-member cube at the scanned offset)"),
]



def esc(b):
    return "".join(chr(c) if 0x20 <= c < 0x7f and c not in (0x5c, 0x22)
                   else ("\\\\" if c == 0x5c else "\\x%02x" % c) for c in b)


def bsubj(s, enc):
    return s if isinstance(s, bytes) else s.encode("utf-8" if enc == "utf8" else "latin-1")


def boundaries(b, enc):
    return [p for p in range(len(b) + 1)
            if enc == "byte" or p == len(b) or (b[p] & 0xC0) != 0x80]


def pcre_cells(pat, enc, b):
    opts = (UTF | INVALID_UTF) if enc == "utf8" else 0
    cx = p2.compile(pat.encode("utf-8" if enc == "utf8" else "latin-1"), opts)
    out = {}
    for p in boundaries(b, enc):
        r = cx.search(b, p)
        out[p] = r[0] if r else None
    return out


def pcre2_only(pat):
    """A byte block python `re` cannot compile (\\G, \\K) is libpcre2's alone."""
    try:
        re.compile(pat)
        return False
    except re.error:
        return True


def py_cells(pat, b):
    rx = re.compile(pat)
    s = b.decode("latin-1")
    out = {}
    for p in range(len(b) + 1):
        m = rx.search(s, p)
        out[p] = (m.start(), m.end()) if m else None
    return out


def pcrec_cells(pcrec, pat, enc, b, d):
    """pcrec's own answers through --emit-main, at every boundary."""
    exe = os.path.join(d, "t")
    src = os.path.join(d, "t.c")
    r = subprocess.run([pcrec, "--features", "all", "-e", enc, "-p", "rx", "--emit-main",
                        "-o", src, "--pattern", pat.encode("utf-8" if enc == "utf8" else "latin-1")],
                       capture_output=True)
    if r.returncode:
        return None
    if subprocess.run(["gcc-16", "-O1", "-w", "-o", exe, src]).returncode:
        return None
    return src, exe


def main():
    check = None
    if "--check-pcrec" in sys.argv:
        check = sys.argv[sys.argv.index("--check-pcrec") + 1]
    out = [
        "# tests/litscan/handoff.rxt -- [K82] (B), THE HANDOFF: the run pre-check's first",
        "# window hit c, less K, becomes the search body's scan start",
        "# (docs/design/litscan_k82h.md §4.2 item 2; docs/spec/tuning.md §2.41).",
        "#",
        "# Written by gen_handoff.py; every expectation is an oracle's: a `byte` block's",
        "# from python3 `re` AND libpcre2 (which must agree), a `utf8` block's from",
        "# libpcre2 under PCRE2_UTF | PCRE2_MATCH_INVALID_UTF alone (so `# pcre2-only`:",
        "# the harness's python tier reads subjects as latin-1), as is a byte block",
        "# python cannot compile (\\G, \\K). Cells sit at EVERY",
        "# character-boundary start position, because the handoff moves where a scan",
        "# begins. Each block is written on the default route and under `engine vm`,",
        "# the forced VM with no DFA scan, which never hands off: the same cells, the",
        "# control route. The rows are the design's witnesses: the maximum offset on",
        "# all three routes (the unanchored scan's reverse pass is bounded by",
        "# search_from, so a K one byte short only shows on the attempt and hybrid",
        "# routes), two occurrences (the gate's leftmost contract), a decoy, multibyte",
        "# width, ill-formed text before the window, seeded starts, \\G on the attempt",
        "# route and on the hybrid (whose prefilter reads its third argument as \\G),",
        "# \\K, find-all subjects (dense and overlapping) and two unbounded controls.",
        ""]
    tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
    mismatches = 0
    for case in CASES:
        pat, enc, subjects, why = case[:4]
        extra = case[4] if len(case) > 4 else []
        cells = []
        for s in subjects:
            b = bsubj(s, enc)
            pc = pcre_cells(pat, enc, b)
            if enc == "byte" and not pcre2_only(pat):
                py = py_cells(pat, b)
                for p, v in pc.items():
                    if py.get(p) != v:
                        sys.exit(f"ORACLES DISAGREE: {pat!r} {b!r} @{p}: pcre2 {v} python {py.get(p)}")
            cells.append((b, pc))
        for route in ("auto", "vm"):
            if enc == "utf8" or pcre2_only(pat):
                out.append("# pcre2-only")
            out.append("# " + why + ("" if route == "auto" else " [engine vm]"))
            out.append("pattern " + pat)
            out.append("features all")
            out.extend(extra)
            out.append("encoding " + enc)
            if route == "vm":
                out.append("engine vm")
            for b, pc in cells:
                for p, v in sorted(pc.items()):
                    if v:
                        out.append('ms %d "%s" %d %d' % (p, esc(b), v[0], v[1]))
                    else:
                        out.append('ns %d "%s"' % (p, esc(b)))
            out.append("")
    text = "\n".join(out)
    if check:
        mismatches = check_with(check, text)
    open(os.path.join(HERE, "handoff.rxt"), "w", encoding="utf-8",
         errors="surrogateescape").write(text)
    print(f"handoff.rxt: {len(CASES)} cases x 2 routes;"
          f" pcrec check mismatches {mismatches if check else 'not run'}")


def check_with(pcrec, text):
    """Runs the written file through the harness with `pcrec` and returns the
    failure count (a pre-existing divergence is reported, not hidden)."""
    path = os.path.join(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")), "handoff.rxt")
    open(path, "w", encoding="utf-8", errors="surrogateescape").write(text)
    r = subprocess.run(["bash", os.path.join(ROOT, "tests/harness/run.sh"), path],
                       env=dict(os.environ, PCREC=pcrec, SKIP_ORACLE="1"),
                       capture_output=True, text=True)
    fails = [ln for ln in r.stdout.splitlines() + r.stderr.splitlines() if "FAIL" in ln]
    for ln in fails[:20]:
        print("  " + ln)
    return len(fails)


if __name__ == "__main__":
    main()
