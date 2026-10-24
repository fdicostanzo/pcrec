#!/usr/bin/env python3
"""docs/dev/lanes/s3_evidence/census.py -- lane s3's MOVER CENSUS for D172 S3 (abi 84 -> 85 since lane s3pair's merge of main 0d3765c87; was 83 -> 84,
PROVISIONAL), job 587's stand-in for emit_sweep's five streams (emit_sweep has no abi
normalization; corefix's census.py is the precedent): which corpus artifacts move, and does
anything move OUTSIDE the declared population?

    python3 -I census.py --base BIN --new BIN --tree DIR --out FILE [--jobs N] [--limit N]

BASE is main's pcrec (0d3765c87 from job 620; c3ea619c3 before), NEW the S3 commit's. Over every distinct corpus pattern
(scripts/emit_sweep.py's own enumeration), ten arms are compiled by both: the .c at the default
engine, under -e utf8 and at --engine=vm, the VM listing (--emit-ir), the facts listing, the
OFF ARM (NEW under --memfn=no-window-search,no-window-skip against BASE's default .c), and (the S3 review's
item D) the .c at the SIMD layer (-fmemfn-simd) and under norun (-fno-run-prefilter), each with
its own OFF arm (the same flag on both sides, NEW also under both denies). NEW's output has the
abi digits mapped back (85 -> 84) in the places they occur; nothing else is normalized; rc and
stderr are compared too.

THE DECLARED POPULATION is read from NEW's OWN ARTIFACT on that arm, a pcrec-side stamp, never
from the kit and never from the diff: a .c arm's pattern is class COVER iff NEW's artifact on that
arm reads `#define RX_DFA_SCAN "cover"` (D172 S3: the cover LOCATE row routed by default). The
judgment, BOTH WAYS, per arm:
  c-default, c-utf8   a COVER artifact MUST move; so must a PAIR artifact (below); nothing else
                      may (a cover or pair artifact that did not move, or a mover that is
                      neither, is UNEXPECTED)
  c-vm                no cover (a DFA-route row); a PAIR artifact must move, nothing else may
  ir                  nothing may move (the VM listing carries no C text)
  facts               THE TWIN RULE (job 606): the listing carries one row set per encoding E
                      (`--emit-facts=byte,utf8`), each mirroring that encoding's artifact: its
                      `RX_*` rows are the artifact's `#define RX_*` stamps one for one, and its
                      `used` cells say which facts the passes that built it asked. So E's rows
                      move iff the task's E-TWIN .c (its own options, then `-p rx --features all
                      -e E`; the last `-e` wins) moved its STAMPS (rc, or a `#define RX_` line),
                      judged BOTH WAYS per encoding: rows that moved with unmoved twin stamps are
                      UNEXPECTED, and so are twin stamps that moved with rows that did not. A
                      twin whose .c moved only in its text (stamps unchanged; code review r2's
                      `pair text` mover) predicts no row move and is counted (`text-only`). The
                      non-row lines, rc and stderr may not move. A listing REFUSED on both sides
                      (one encoding refuses the pattern, so it has no rows) has nothing to
                      mirror: counted (`refused`), not judged; its rc/stderr still may not move.
                      The control is a different artifact (the .c), compiled separately; the
                      tally line counts the judged population (tasks x 2 encodings)
  c-simd, c-norun     as c-default, at the SIMD layer and under -fno-run-prefilter: the cover
                      stamp is read from NEW's artifact on THAT arm
  off, off-simd,      nothing may move but a PAIR artifact, which must (the OFF arm renders the
  off-norun           parent's text but for the two-stream find's bounded look-ahead, at each
                      of the three flag settings)
THE PAIR CLASS (the S3 final review's EMIT-1 fix; the manager's ruling R-d): the two-stream find
(kit.h's ofs_pair, one renderer for fn-pair's body, the run pre-check's pair block and the window
search's B-pair) now bounds each stream's look-ahead, so every artifact carrying it moves, cover
or not. A non-cover artifact is class PAIR iff NEW's artifact carries the bounded form's
declaration (`size_t ha = 0, hb = 0, wa = ...`, any prefix); declared from NEW's own text, and
judged BOTH WAYS against BASE's own text: a PAIR artifact must move, carry exactly as many
two-stream declarations as BASE's carries of the unbounded form (`size_t ha = 0, hb = 0;`, the
`fresh` flag's), and keep every `#define RX_` stamp (the look-ahead moves no stamp); a non-PAIR
artifact whose BASE carries the unbounded form is UNEXPECTED (a two-stream find that vanished).
The tally counts `pair` per arm.
D-HORS (Table D's dense-stop resume) appears as a file-scope skip table `_sh[256]`; it may appear
only in a COVER artifact (counted: `hors`), never elsewhere (UNEXPECTED).
THE BLOCK'S OPTIONS (code review r1 C11): a corpus pattern is compiled under its own block's
options, read from `pcrec --list-source` (the .rxt as written): `flags` i -> `-i`, u -> `--ucp`,
`encoding` -> `-e ENC` (rxt_format.md §1.5¶4; the corpus states no per-block raw `pcrec` flags
and no `with`/`from` cascade on a pattern row, and a row stating one is counted and REFUSED, not
compiled without it). A pattern is one task per distinct (pattern, options); the options come
first on every arm's command line, so an arm's own `-e` overrides a block's. The tally line
`options:` counts the option-driven tasks and the cover artifacts among them.
Trailer: `== s3 census COMPLETE: patterns=P compiles=C movers=M unexpected=U`; exit 0 iff U == 0.
"""
import argparse
import concurrent.futures
import os
import re
import subprocess
import sys

ABI = [(b"(abi 85)", b"(abi 84)"), (b"(PCREC_RX_ABI_H + 0) != 85", b"(PCREC_RX_ABI_H + 0) != 84"),
       (b"#define PCREC_RX_ABI_H 85", b"#define PCREC_RX_ABI_H 84"), (b"    .abi = 85,", b"    .abi = 84,")]
COVER = b'#define RX_DFA_SCAN "cover"'
HORS = b"_sh[256]"
# the two-stream find's declaration: NEW's bounded form, BASE's unbounded one (the PAIR class)
PAIR_NEW = re.compile(rb"size_t (\w*)ha = 0, \1hb = 0, \1wa = ")
PAIR_OLD = re.compile(rb"size_t (\w*)ha = 0, \1hb = 0;")
OFF = "--memfn=no-window-search,no-window-skip"

# (arm, base argv, new argv, judged by the artifact's own stamp?)
ARMS = [
    ("c-default", ["-p", "rx", "--features", "all", "-o", "-"], None, True),
    ("c-utf8", ["-p", "rx", "--features", "all", "-e", "utf8", "-o", "-"], None, True),
    ("c-vm", ["-p", "rx", "--features", "all", "--engine=vm", "-o", "-"], None, False),
    ("ir", ["--features", "all", "--engine=vm", "--emit-ir"], None, False),
    ("facts", ["--features", "all", "--emit-facts=byte,utf8"], None, False),
    ("off", ["-p", "rx", "--features", "all", "-o", "-"],
     ["-p", "rx", "--features", "all", OFF, "-o", "-"], False),
    ("c-simd", ["-p", "rx", "--features", "all", "-fmemfn-simd", "-o", "-"], None, True),
    ("c-norun", ["-p", "rx", "--features", "all", "-fno-run-prefilter", "-o", "-"], None, True),
    ("off-simd", ["-p", "rx", "--features", "all", "-fmemfn-simd", "-o", "-"],
     ["-p", "rx", "--features", "all", "-fmemfn-simd", OFF, "-o", "-"], False),
    ("off-norun", ["-p", "rx", "--features", "all", "-fno-run-prefilter", "-o", "-"],
     ["-p", "rx", "--features", "all", "-fno-run-prefilter", OFF, "-o", "-"], False),
]


def norm(out):
    for a, b in ABI:
        out = out.replace(a, b)
    return out


def run(argv, timeout=60):
    try:
        r = subprocess.run(argv, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -9, b"", b"TIMEOUT"


def first_diff(a, b):
    la, lb = a.split(b"\n"), b.split(b"\n")
    for i in range(max(len(la), len(lb))):
        x = la[i] if i < len(la) else b"<eof>"
        y = lb[i] if i < len(lb) else b"<eof>"
        if x != y:
            return "line %d: base=%r new=%r" % (i + 1, x[:100], y[:100])
    return ""


FACTS_ENCS = ("byte", "utf8")


def facts_split(b):
    """A facts listing as {encoding: its rows, "": every other line}: a row is `byte<TAB>...`
    or `utf8<TAB>...` (facts_listing.md); the rest (headers, anything else) must never move."""
    d = {"": [], "byte": [], "utf8": []}
    for ln in b.split(b"\n"):
        e = ln.split(b"\t", 1)[0].decode("ascii", "replace")
        d[e if e in FACTS_ENCS else ""].append(ln)
    return d


def stamps(out):
    """The `#define RX_*` stamp lines of a .c artifact (what a facts listing's `RX_*` rows
    mirror)."""
    return [ln for ln in out.split(b"\n") if ln.startswith(b"#define RX_")]


def facts_judge(base, new, opts, pat, b, n, norm_new=lambda x: x):
    """(problems, twins, text_only) of one task's facts listing, b/n = BASE's and NEW's run()
    triples: THE TWIN RULE (the docstring above), BOTH WAYS per encoding. twins = the
    encodings whose twin stamps moved, or None for a listing refused on both sides (not
    judged); text_only = the encodings whose twin .c moved with its stamps unchanged;
    problems = one string per broken expectation (empty = as declared)."""
    (rb, ob, eb), (rn, on, en) = b, n
    problems = [] if rb == rn and eb == norm_new(en) else ["rc or stderr moved"]
    if rb and rn:
        return problems, None, []
    sb, sn = facts_split(ob), facts_split(norm_new(on))
    twins, text_only = [], []
    if sb[""] != sn[""]:
        problems.append("non-row lines moved: " + first_diff(b"\n".join(sb[""]), b"\n".join(sn[""])))
    for e in FACTS_ENCS:
        tw = [run([x] + list(opts) + ["-p", "rx", "--features", "all", "-e", e, "-o", "-", "--pattern", pat])
              for x in (base, new)]
        twin = tw[0][0] != tw[1][0] or stamps(tw[0][1]) != stamps(norm_new(tw[1][1]))
        rows = sb[e] != sn[e]
        if twin:
            twins.append(e)
        elif tw[0][1] != norm_new(tw[1][1]):
            text_only.append(e)
        if rows and not twin:
            problems.append("%s rows moved, the %s twin's stamps did not: %s"
                            % (e, e, first_diff(b"\n".join(sb[e]), b"\n".join(sn[e]))))
        elif twin and not rows:
            problems.append("the %s twin's stamps moved, the %s rows did not" % (e, e))
    return problems, twins, text_only


FLAG_ARGV = {"i": "-i", "u": "--ucp"}


def block_options(row):
    """The pcrec options of one `--list-source` pattern row (its columns as written), or
    None where it states something this census does not pass (a raw `pcrec` flag, a
    `with`/`from` cascade, an unknown flag letter)."""
    flags, enc, cascade_with, cascade_from, raw = row[5], row[8], row[12], row[13], row[14]
    if raw or cascade_with or cascade_from or any(c not in FLAG_ARGV for c in flags):
        return None
    opts = [FLAG_ARGV[c] for c in flags]
    if enc:
        opts += ["-e", enc]
    return tuple(opts)


def corpus_tasks(es, pcrec_bin, tree):
    """(rows, tasks, refused): every corpus pattern row with its block's options; the
    distinct (pattern, options) tasks; the rows whose options this census cannot pass."""
    rows, refused = 0, []
    tasks = set()
    for f in es.find_files(tree, (".rxt",)):
        rc, out, _ = run([pcrec_bin, "--list-source", f], 60)
        if rc:
            continue
        for ln in out.decode("utf-8", errors="surrogateescape").splitlines():
            c = ln.split("\t")
            if ln.startswith("#") or len(c) < 15 or c[0] not in ("pattern", "pattern-esc"):
                continue
            rows += 1
            opts = block_options(c)
            if opts is None:
                refused.append((os.path.relpath(f, tree), c[1]))
                continue
            tasks.add((es.decode_escape(c[4]), opts))
    return rows, sorted(tasks), refused


def one(task):
    base, new, pat, opts = task
    opts = list(opts)
    res = []
    for arm, fb, fn, stamped in ARMS:
        rb, ob, eb = run([base] + opts + fb + ["--pattern", pat])
        rn, on, en = run([new] + opts + (fn or fb) + ["--pattern", pat])
        what = []
        if rb != rn:
            what.append("rc base=%d new=%d" % (rb, rn))
        if ob != norm(on):
            what.append("bytes " + first_diff(ob, norm(on)))
        if eb != norm(en):
            what.append("stderr " + first_diff(eb, norm(en)))
        cover = stamped and rn == 0 and COVER in on
        problems, twins, text_only = [], [], []
        npair = 0 if cover or arm in ("ir", "facts") else len(PAIR_NEW.findall(on))
        opair = 0 if cover or arm in ("ir", "facts") else len(PAIR_OLD.findall(ob))
        if npair or opair:
            if npair != opair:
                problems.append("two-stream finds: base %d unbounded, new %d bounded" % (opair, npair))
            if stamps(ob) != stamps(norm(on)):
                problems.append("a pair artifact moved a stamp: " + first_diff(
                    b"\n".join(stamps(ob)), b"\n".join(stamps(norm(on)))))
        if arm == "facts":
            # declared: the twin rule (facts_judge), both ways; rc and stderr unchanged
            problems, twins, text_only = facts_judge(base, new, opts, pat, (rb, ob, eb), (rn, on, en), norm)
        res.append((arm, "; ".join(what), cover, npair > 0, HORS in on, problems, twins, text_only))
    return pat, tuple(opts), res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    import emit_sweep  # noqa: E402  (the corpus enumeration, one implementation)
    nrows, tasks, refused = corpus_tasks(emit_sweep, a.new, a.tree)
    if a.limit:
        tasks = tasks[:a.limit]
    pats = tasks
    tally = {arm: {"cover": 0, "pair": 0, "moved": 0, "hors": 0, "twin": 0, "text": 0, "judged": 0, "refused": 0} for arm, _, _, _ in ARMS}
    optn = {"tasks": 0, "cover": 0}
    unexpected, rows = [], []
    for f, line in refused:
        unexpected.append(("-", "refused", "%s:%s" % (f, line),
                           "a block option this census does not pass (raw pcrec flags, a cascade)"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for pat, opts, res in ex.map(one, [(a.base, a.new, p, o) for p, o in tasks], chunksize=8):
            ep = emit_sweep.encode_escape(pat) + (" [" + " ".join(opts) + "]" if opts else "")
            if opts:
                optn["tasks"] += 1
                optn["cover"] += any(arm == "c-default" and cover for arm, _, cover, _, _, _, _, _ in res)
            for arm, what, cover, pair, hors, problems, twins, text_only in res:
                t = tally[arm]
                t["cover"] += cover
                t["pair"] += pair
                t["hors"] += hors and cover
                if what:
                    t["moved"] += 1
                    rows.append((arm, "TWIN" if arm == "facts" and twins else
                                 "COVER" if cover else "PAIR" if pair else "other", ep, what))
                if arm == "facts":
                    if twins is None:
                        t["refused"] += 1
                    else:
                        t["judged"] += len(FACTS_ENCS)
                        t["twin"] += len(twins)
                        t["text"] += len(text_only)
                    unexpected += [(arm, "twin", ep, p) for p in problems]
                else:
                    unexpected += [(arm, "PAIR", ep, p) for p in problems]
                    if cover and not what:
                        unexpected.append((arm, "COVER", ep, "a cover artifact did NOT move"))
                    elif pair and not what:
                        unexpected.append((arm, "PAIR", ep, "a pair artifact did NOT move"))
                    elif what and not (cover or pair):
                        unexpected.append((arm, "other", ep, what))
                if hors and not cover:
                    unexpected.append((arm, "other", ep, "a D-hors skip table outside a cover artifact"))
    with open(a.out, "w", encoding="utf-8", errors="backslashreplace") as f:
        f.write("# s3 census: base=%s new=%s patterns=%d\n#arm\tclass\tpattern\tmoved\n"
                % (a.base, a.new, len(pats)))
        for r in unexpected + rows:
            f.write("\t".join(x.replace("\t", "\\t").replace("\n", "\\n") for x in r) + "\n")
    print("census: corpus rows %d, distinct (pattern, options) tasks %d" % (nrows, len(pats)))
    print("  options: %d tasks under their block's options (flags i/u, encoding), %d of them "
          "cover at c-default; %d rows refused" % (optn["tasks"], optn["cover"], len(refused)))
    for arm, _, _, stamped in ARMS:
        t = tally[arm]
        print("  %-9s cover %5d (D-hors %4d)  pair %5d  movers %5d  declared: %s" % (
            arm, t["cover"], t["hors"], t["pair"], t["moved"],
            "movers == cover + pair artifacts" if stamped else
            "the twin rule, both ways: %d encodings judged, %d twin stamps moved, %d text-only, "
            "%d listings refused" % (t["judged"], t["twin"], t["text"], t["refused"])
            if arm == "facts"
            else "no mover" if arm == "ir" else "movers == pair artifacts"))
    for u in unexpected[:20]:
        print("  UNEXPECTED %s %s %s: %s" % u)
    print("== s3 census COMPLETE: patterns=%d compiles=%d movers=%d unexpected=%d"
          % (len(pats), 2 * len(pats) * (len(ARMS) + len(FACTS_ENCS)), len(rows), len(unexpected)))
    return 0 if not unexpected else 1


if __name__ == "__main__":
    sys.exit(main())
