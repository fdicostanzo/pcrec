#!/usr/bin/env python3
"""sr_perl.py -- THE PERL ARM (D71 item 5): a second oracle, RECORDED.

Subroutine calls are Perl's own construct and PCRE2's feature was modeled on
them, so perl 5.40.1 is a legitimate second oracle for this module -- but
D26 rules that PCRE2 is the sole source of truth for what pcrec matches. So
this program never writes an expectation. It:

  1. runs every corpus cell through perl 5.40.1 as well as libpcre2;
  2. records which SPELLINGS perl refuses outright;
  3. records every case where perl and libpcre2 DISAGREE, in
     d27/PERL_DIVERGENCES.md, with a one-line reading of each;
  4. writes d27/perl_diverges.txt, which sr_gen.py reads on its next run to
     stamp `# perl-diverges` on the affected blocks.

The design predicts ONE divergence class -- the atomicity of a call, since
PCRE2 was atomic here before 10.30 and perl may still be. That prediction is
MEASURED below, not assumed: if it does not appear, the table says so.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)
_s = importlib.util.spec_from_file_location(
    "sr_oracle", os.path.join(CELL, "docs", "design",
                              "subroutines_measurements", "probes",
                              "sr_oracle.py"))
sr = importlib.util.module_from_spec(_s)
_s.loader.exec_module(sr)

ESC = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t', 'r': '\r',
       'f': '\f', 'v': '\v'}


def unquote(field):
    out, i = [], 1
    while i < len(field):
        ch = field[i]
        if ch == '"':
            return "".join(out), field[i + 1:]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        i += 1
        e = field[i]
        if e in ESC:
            out.append(ESC[e])
            i += 1
        elif e == "x":
            out.append(chr(int(field[i + 1:i + 3], 16)))
            i += 3
        else:
            raise ValueError("bad escape %r" % e)
    raise ValueError("unterminated subject")


def read_cells():
    """[(file, lineno, pattern, kind, subject, startpos)] over every m/n/ms/ns
    case in the corpus, plus [(file, lineno, pattern)] for each perr block."""
    cells, perrs = [], []
    for f in sorted(x for x in os.listdir(HERE) if x.endswith(".rxt")):
        pat = None
        for lineno, raw in enumerate(open(os.path.join(HERE, f)), 1):
            line = raw.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            head, _, rest = line.partition(" ")
            if head == "pattern":
                pat = rest
            elif head == "perr":
                perrs.append((f, lineno, pat))
            elif head in ("m", "n", "ms", "ns"):
                if head in ("ms", "ns"):
                    sp, _, rest = rest.partition(" ")
                    start = int(sp)
                else:
                    start = 0
                subj, _tail = unquote(rest)
                cells.append((f, lineno, pat, head, subj, start))
            elif head == "gu":
                code, _, rest = rest.partition(" ")
                subj, _tail = unquote(rest)
                cells.append((f, lineno, pat, "gu", subj, 0))
    return cells, perrs


def run_perl(jobs):
    """jobs: [(id, pattern, startpos, subject)] -> {id: ('ERR',msg) |
    ('nomatch',) | ('match', [(s,e), ...])}"""
    with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False) as fh:
        for jid, pat, start, subj in jobs:
            fh.write("%s\t%s\t%d\t%s\n"
                     % (jid, pat.encode("latin-1").hex(), start,
                        subj.encode("latin-1").hex()))
        path = fh.name
    try:
        r = subprocess.run(["perl", os.path.join(HERE, "sr_perl.pl"), path],
                           capture_output=True, text=True, timeout=600)
    finally:
        os.unlink(path)
    out = {}
    for line in r.stdout.splitlines():
        f = line.split("\t")
        if len(f) >= 3 and f[1] in ("ERRC", "ERRM"):
            out[f[0]] = (f[1], f[2])
        elif len(f) >= 2 and f[1] == "nomatch":
            out[f[0]] = ("nomatch",)
        elif len(f) >= 3 and f[1] == "match":
            pairs = []
            for p in f[2].split():
                a, b = p.split(",")
                pairs.append((int(a), int(b)))
            out[f[0]] = ("match", pairs)
    if r.stderr.strip():
        sys.stderr.write("perl stderr: %s\n" % r.stderr.strip()[:400])
    return out


def norm_pcre2(r, ncap):
    if r is None:
        return ("nomatch",)
    (s, e), groups = r
    pairs = [(s, e)]
    for g in groups[:ncap]:
        pairs.append((-1, -1) if g is None else g)
    return ("match", pairs)


def reading(pat, pcre2, perl):
    """One line saying what the disagreement IS. Deliberately mechanical --
    a category from the shapes, never a story about either engine."""
    if perl[0] in ("ERRC", "ERRM"):
        return "perl refuses this spelling"
    if pcre2[0] != perl[0]:
        if pcre2[0] == "match":
            return ("libpcre2 matches, perl does not"
                    + (" -- a call that gave back on libpcre2 and did not "
                       "on perl (the design's predicted atomicity class)"
                       if ("(?&" in pat or "(?1" in pat or "(?R" in pat)
                       and "|" in pat else ""))
        return "perl matches, libpcre2 does not"
    if pcre2[1][0] != perl[1][0]:
        return "same verdict, DIFFERENT whole-match span"
    return "same span, DIFFERENT group spans"


def main():
    cells, perrs = read_cells()
    jobs, meta = [], {}
    for i, (f, lineno, pat, kind, subj, start) in enumerate(cells):
        jid = "c%d" % i
        jobs.append((jid, pat, start, subj))
        meta[jid] = (f, lineno, pat, kind, subj, start)
    for i, (f, lineno, pat) in enumerate(perrs):
        jid = "e%d" % i
        jobs.append((jid, pat, 0, "a"))
        meta[jid] = (f, lineno, pat, "perr", "a", 0)

    print("running %d cells through perl 5.40.1 …" % len(jobs))
    res = run_perl(jobs)

    refused = {}          # pattern -> perl's COMPILE-time message
    gaveup = {}           # pattern -> perl's MATCH-time die
    diverge = []          # rows for the table
    ran = 0
    agreed = 0
    gu_seen = 0
    pcrec_only_perr = set()

    for jid, (f, lineno, pat, kind, subj, start) in sorted(meta.items()):
        p = res.get(jid)
        if p is None:
            refused.setdefault(pat, "perl produced no answer at all")
            continue
        if p[0] == "ERRC":
            refused.setdefault(pat, trim(p[1]))
            continue
        if p[0] == "ERRM":
            gaveup.setdefault(pat, trim(p[1]))
            if kind in ("m", "ms"):
                ran += 1
                diverge.append((f, lineno, pat, subj, start,
                                fmt(norm_pcre2(sr.search(pat, subj, start, 0),
                                               sr.ngroups(pat, 0) or 0)),
                                "DIED at match time: " + trim(p[1]),
                                "libpcre2 answers; perl gives up at match "
                                "time"))
            continue
        ran += 1
        if kind == "perr":
            # A perr block is refused by libpcre2 OR (for the [DD-14.LB]
            # amendment's one case) by pcrec alone. Perl agreeing with
            # libpcre2 is not a divergence, so ask libpcre2 first.
            if sr.compile_err(pat, 0) is None:
                pcrec_only_perr.add(pat)
                continue
            diverge.append((f, lineno, pat, subj, start,
                            "REFUSED (libpcre2 compile error)", fmt(p),
                            "perl COMPILES a pattern libpcre2 refuses"))
            continue
        if kind == "gu":
            gu_seen += 1
            continue
        ncap = sr.ngroups(pat, 0) or 0
        want = norm_pcre2(sr.search(pat, subj, start, 0), ncap)
        got = p
        if got[0] == "match":
            # PAD, do not truncate. perl's @-/@+ stop at the highest group
            # that PARTICIPATED, while libpcre2's ovector reports every
            # declared group with UNSET for the ones that did not. That is a
            # REPORTING CONVENTION, not a semantic disagreement, and comparing
            # the raw lists put ~90 false rows in this table on the first
            # run. la_oracle's own _pad() normalises the PCRE2 side the same
            # way for the same reason.
            pairs = list(got[1][:ncap + 1])
            while len(pairs) < ncap + 1:
                pairs.append((-1, -1))
            got = ("match", pairs)
        if want == got:
            agreed += 1
            continue
        diverge.append((f, lineno, pat, subj, start, fmt(want), fmt(got),
                        reading(pat, want, got)))

    write_md(refused, gaveup, diverge, ran, agreed, gu_seen, len(jobs),
             pcrec_only_perr)

    pats = sorted({d[2] for d in diverge})
    with open(os.path.join(HERE, "perl_diverges.txt"), "w") as fh:
        for pt in pats:
            fh.write(pt.encode("latin-1").hex() + "\n")

    print("  perl ran      : %d cells (%d agreed with libpcre2)"
          % (ran, agreed))
    print("  perl refused  : %d distinct spellings (compile time)"
          % len(refused))
    print("  perl died     : %d distinct patterns (match time)" % len(gaveup))
    print("  divergences   : %d rows over %d distinct patterns"
          % (len(diverge), len(pats)))
    print("  gu cells      : %d (a pcrec capacity fact; perl has no "
          "counterpart, not counted as agreement)" % gu_seen)
    print("  wrote PERL_DIVERGENCES.md and perl_diverges.txt")
    return 0


def fmt(x):
    if x[0] == "nomatch":
        return "nomatch"
    if x[0] == "ERR":
        return "ERR: " + x[1][:70]
    return " ".join("(%d,%d)" % (a, b) for a, b in x[1])


def write_md(refused, gaveup, diverge, ran, agreed, gu_seen, njobs,
             pcrec_only_perr=()):
    L = []
    L.append("# PERL_DIVERGENCES.md — the [DD-14.D27] corpus's second oracle")
    L.append("")
    L.append("Perl 5.40.1 against libpcre2 10.46, over every cell of the "
             "d27/ corpus.")
    L.append("")
    L.append("**D26 rules: libpcre2 is the source of truth for what pcrec "
             "matches.** Nothing in this file is an expectation. Perl is "
             "here because subroutine calls are Perl's own construct and "
             "PCRE2's feature was modeled on them, so a disagreement is "
             "worth knowing about — it is RECORDED, never RESOLVED, and no "
             "`.rxt` line was written from perl's answer. Blocks whose "
             "pattern appears below carry a `# perl-diverges` marker in "
             "the corpus.")
    L.append("")
    L.append("Generated by `d27/sr_perl.py`; regenerate rather than edit.")
    L.append("")
    L.append("## Coverage")
    L.append("")
    L.append("| | count |")
    L.append("|---|---|")
    L.append("| cells offered to perl | %d |" % njobs)
    L.append("| cells perl RAN | %d |" % ran)
    L.append("| …of which perl and libpcre2 AGREED exactly (span and every "
             "group) | %d |" % agreed)
    L.append("| give-up (`gu`) cells — a pcrec capacity fact with no perl "
             "counterpart | %d |" % gu_seen)
    L.append("| distinct spellings perl REFUSED at COMPILE time | %d |"
             % len(refused))
    L.append("| distinct patterns perl COMPILED and then DIED on at MATCH "
             "time | %d |" % len(gaveup))
    L.append("| divergence rows | %d |" % len(diverge))
    L.append("")

    L.append("## The spellings perl 5.40.1 REFUSES")
    L.append("")
    if not refused:
        L.append("None — perl compiled every pattern in this corpus.")
    else:
        L.append("| pattern | perl's message |")
        L.append("|---|---|")
        for pat in sorted(refused):
            L.append("| `%s` | %s |" % (md(pat), md(refused[pat][:110])))
    L.append("")

    L.append("## Patterns perl COMPILES and then DIES on at MATCH time")
    L.append("")
    L.append("A different fact from a refused spelling, and the one worth "
             "reading beside PCRE2's own `rc -52`: perl accepts the "
             "pattern and then declines to answer when it runs. pcrec's "
             "counterpart is the `PCREC_ERR_FRAMES` give-up the `gu` cells "
             "in `sr_depth.rxt` expect.")
    L.append("")
    if not gaveup:
        L.append("None.")
    else:
        L.append("| pattern | perl's message |")
        L.append("|---|---|")
        for pat in sorted(gaveup):
            L.append("| `%s` | %s |" % (md(pat), md(gaveup[pat][:100])))
    L.append("")
    if pcrec_only_perr:
        L.append("## Blocks pcrec refuses that BOTH libpcre2 and perl accept")
        L.append("")
        L.append("Not a perl divergence — recorded so the row below is not "
                 "mistaken for one. These are the [DD-14.LB] amendment's "
                 "pcrec-only refusals: pcrec declines a lookbehind branch "
                 "whose width is variable even though both reference "
                 "engines accept it.")
        L.append("")
        for pt in sorted(pcrec_only_perr):
            L.append("- `%s`" % md(pt))
        L.append("")
    L.append("## Where perl and libpcre2 DISAGREE")
    L.append("")
    if not diverge:
        L.append("**No divergence was measured.** The design predicted one "
                 "class — the atomicity of a call, since PCRE2 was atomic "
                 "here before 10.30 and perl might still be. It did not "
                 "appear: on every backtracking cell in "
                 "`sr_atomicity.rxt`, including the four atomic controls "
                 "and the retry-across-a-return cell, perl 5.40.1 answers "
                 "exactly what libpcre2 10.46 answers. The prediction was "
                 "measured, not assumed, and it is negative.")
    else:
        L.append("| # | cell | pattern | subject | startpos | libpcre2 "
                 "10.46 | perl 5.40.1 | reading |")
        L.append("|---|---|---|---|---|---|---|---|")
        for i, (f, lineno, pat, subj, start, want, got, why) in \
                enumerate(diverge, 1):
            L.append("| %d | %s:%d | `%s` | `%s` | %d | %s | %s | %s |"
                     % (i, f, lineno, md(pat), md(repr(subj)[1:-1]), start,
                        md(want), md(got), why))
    L.append("")
    with open(os.path.join(HERE, "PERL_DIVERGENCES.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")


def trim(msg):
    """Drop perl's " at <script> line N, <$fh> line N" tail -- it names THIS
    harness, not the pattern, and would date the table to a file layout."""
    for cut in (" at /", " in regex; marked by"):
        i = msg.find(cut)
        if i > 0:
            return msg[:i] + ("" if cut == " at /" else " …")
    return msg


def md(s):
    return s.replace("|", "\\|")


if __name__ == "__main__":
    sys.exit(main())
