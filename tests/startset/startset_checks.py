#!/usr/bin/env python3
"""tests/startset/startset_checks.py -- the `start_set` FACT's checks
([START-SET] stage 1, D148; docs/design/startset.md §6.2, review r4).

Every check reads the SHIPPED fact: the `start_set` row of `pcrec
--emit-facts` for the block's own compile, rendered by the fact's one
renderer. Never a probe that rebuilds the pipeline prefix (checks-F2; the
c2prep F5 hazard): a probe can drift from the compile it claims to describe,
and the r3 census's probe did -- it ignored `-i`/`--ucp` (sound-F4).

[ss-ctrl] C-SS*, THE FACT'S CONTROL ON EVERY MACHINE, SEEDED INCLUDED.
    For every corpus block (its own options, startset_lib.corpus_blocks) whose
    artifact carries a forward DFA (a DFA artifact or a VM hybrid's inlined
    prefilter) and whose start set is NECESSARY (not nullable, fewer than 256
    members): X is a subset of S, where X is read off the EMITTED tables --
      seeded machine:   Tdfa, the bytes that begin a live thread from SOME
                        seed state (read where the emitted can_begin_match,
                        if any, is s0's escape set);
      unseeded machine: the emitted can_begin_match table.
    INDEPENDENT BECAUSE X comes from the subset construction's tables and the
    walk shares no code with it. THE FAILING DIRECTION IS IN THE WALK, not in
    set arithmetic: sabotage S501 (a zero-width node read as consuming) and
    S502 (A_CAT drops `null(l) ? F(r)`) plant walk defects, and this check is
    their stage-1 detector. What it CANNOT see (startset.md §6.4.3 item 2): a
    too-SMALL derived set that still contains Tdfa -- Tdfa is not a sound
    floor; the start-byte oracle and the answer cells are that detector
    (stage 2/3). Rows the tables do not let it read (no forward table, the
    attempt engine's label tables, a seeded table that is not s0's escape
    set) are COUNTED as unread, never dropped silently (K35).

[ss-null] NULLABLE => start_set.nullable, on every compiled block.
    `nullable` (E1, owner widths.c) answers "can L match empty"; the walk's
    bit answers it for L+, the zero-width-erased language, and L is a subset
    of L+ (sound-F9/checks-F9). Two owners of two questions; a walk that
    under-approximates nullability fails here.

[ss-flag] THE COMPILE'S OWN OPTIONS REACH THE FACT (sound-F4): hand-written
    witnesses whose expected set is written HERE from the pattern and the
    flag (never read off the compiler): `-i`, `--ucp` with a Latin-1 fold,
    `-e utf8` caseless with the KELVIN SIGN's lead byte, and the conservative
    arms (a call, a backreference, a variable, a nullable pattern).

Env: PCREC (default <tree>/build/pcrec), JOBS (default 6).
Prints PASS:/FAIL: lines and the `checks passed:`/`checks failed:` trailers.
"""
import os, subprocess, sys, tempfile, concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import startset_lib as L

PCREC = os.environ.get("PCREC", os.path.join(TREE, "build", "pcrec"))
JOBS = int(os.environ.get("JOBS", "6"))
TMO = 120
# K35 floors: HALF the population measured at landing (D110's shape), so a
# collapsed population fails rather than reading clean. Measured at landing
# (lane ssbuild01): see docs/dev/lanes/ssbuild01_report.md §2.
FLOOR_BLOCKS = 1700        # compiled blocks
FLOOR_CTRL = 450           # C-SS* rows checked (necessary S, readable machine)
FLOOR_SEEDED = 60          # ... of them on a SEEDED machine
FLOOR_NULLABLE = 200       # blocks whose `nullable` fact reads yes

passed = failed = 0


def ok(m):
    global passed; passed += 1; print("PASS: " + m)


def bad(m):
    global failed; failed += 1; print("FAIL: " + m)


def compile_block(b, td):
    """(facts, decisions, emitted C text or None) for one block, or None."""
    try:
        r = subprocess.run([PCREC, *b["args"], "--emit-facts", "--pattern", b["pattern"]],
                           capture_output=True, timeout=TMO)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode:
        return None
    fct, dec = L.facts(r.stdout.decode("utf-8", "replace"))
    src = None
    if "RX_DFA_SCAN" in dec:
        o = os.path.join(td, "%d.c" % abs(hash((b["id"], tuple(b["args"])))))
        try:
            c = subprocess.run([PCREC, *b["args"], "-p", "rx", "-o", o, "--pattern", b["pattern"]],
                               capture_output=True, timeout=TMO)
            if c.returncode == 0:
                src = open(o, errors="replace").read()
        except subprocess.TimeoutExpired:
            pass
        for f in (o, o[:-2] + ".h"):
            try: os.remove(f)
            except OSError: pass
    return fct, dec, src


def corpus_checks():
    blocks, cnt = L.corpus_blocks(PCREC, TREE)
    print("REACH: %d .rxt files, %d pattern rows, %d NUL-bearing out, %d (text, options) duplicates, %d blocks"
          % (cnt["files"], cnt["rows"], cnt["nul"], cnt["dup"], len(blocks)))
    with tempfile.TemporaryDirectory() as td, cf.ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(lambda b: compile_block(b, td), blocks))
    comp = [(b, r) for b, r in zip(blocks, res) if r is not None]
    nnull = 0; null_bad = []
    nctrl = nseed = 0; unread = {}; viol = []
    for b, (fct, dec, src) in comp:
        ss = fct.get("start_set"); nl = fct.get("nullable")
        if not ss or not nl or ss.get("status") != "derived":
            null_bad.append("%s: no derived start_set row" % b["id"]); continue
        snull, S = L.set_of(ss["value"])
        if nl["value"] == "yes":
            nnull += 1
            if not snull: null_bad.append(b["id"])
        if src is None:
            continue
        if snull or len(S) >= 256:
            continue
        m = L.machine_sets(src)
        if m["status"] != "ok":
            unread[m["status"]] = unread.get(m["status"], 0) + 1; continue
        if m["nseeds"] > 1:
            if not m["cbm_agrees"]:
                unread["seeded-table-not-s0"] = unread.get("seeded-table-not-s0", 0) + 1; continue
            X = m["Tdfa"]; nseed += 1
        elif m["Ecbm"] is not None:
            X = m["Ecbm"]
        else:
            unread["unseeded-no-table"] = unread.get("unseeded-no-table", 0) + 1; continue
        nctrl += 1
        if not X <= S:
            viol.append("%s %r %s: %d byte(s) begin a live thread outside S (e.g. %s)"
                        % (b["id"], b["pattern"][:40], " ".join(b["args"]), len(X - S), sorted(X - S)[:4]))
    print("REACH: %d blocks compiled; %d read `nullable yes`" % (len(comp), nnull))
    print("REACH: C-SS* rows checked %d (seeded %d); unread %s"
          % (nctrl, nseed, ", ".join("%s %d" % kv for kv in sorted(unread.items())) or "0"))
    if len(comp) < FLOOR_BLOCKS or nnull < FLOOR_NULLABLE:
        bad("[ss-null] the population collapsed: %d compiled (floor %d), %d nullable (floor %d)"
            % (len(comp), FLOOR_BLOCKS, nnull, FLOOR_NULLABLE))
    elif null_bad:
        bad("[ss-null] NULLABLE yes but start_set not nullable (the walk under-approximates), or no row: "
            + "; ".join(null_bad[:8]) + (" ..." if len(null_bad) > 8 else ""))
    else:
        ok("[ss-null] on all %d compiled blocks, nullable => start_set.nullable (%d nullable)" % (len(comp), nnull))
    if nctrl < FLOOR_CTRL or nseed < FLOOR_SEEDED:
        bad("[ss-ctrl] the population collapsed: %d rows (floor %d), %d seeded (floor %d)"
            % (nctrl, FLOOR_CTRL, nseed, FLOOR_SEEDED))
    elif viol:
        bad("[ss-ctrl] C-SS*: %d machine(s) where a byte that begins a live thread is outside the start set: "
            % len(viol) + "; ".join(viol[:6]) + (" ..." if len(viol) > 6 else ""))
    else:
        ok("[ss-ctrl] C-SS*: on all %d readable machines (%d seeded) the emitted start bytes are a subset of start_set"
           % (nctrl, nseed))


# (options, pattern, expected): `nullable`, or the set as written by hand.
A = lambda s: {ord(c) for c in s}
WITNESSES = [
    (["-i"], b"ab", A("aA")),
    (["--features", "all", "-e", "byte", "--ucp"], b"(?i)\\xe9x", {0xC9, 0xE9}),
    (["--features", "all", "-e", "byte"], b"(?i)\\xe9x", {0xE9}),
    (["--features", "all", "-e", "utf8"], b"(?i)k", A("kK") | {0xE2}),
    (["--features", "all", "-e", "utf8"], b"\\x{3b1}|b", {0xCE, ord("b")}),
    (["--features", "all"], b"(?=x)ab|c", A("ac")),
    (["--features", "all"], b"\\bfoo", A("f")),
    (["--features", "all"], b"x*(a)\\1", A("xa")),
    (["--features", "all"], b"a*b?", "nullable"),
    (["--features", "all"], b"(?1)x(y)", "nullable"),
    (["--features", "all"], b"(a)\\1|z", A("az")),
    (["--features", "all"], b"${v}x", "nullable"),
    (["--features", "all"], b"(?<=a)z|w", A("zw")),
]


def witness_checks():
    bad_w = []
    for args, pat, want in WITNESSES:
        r = subprocess.run([PCREC, *args, "--emit-facts", "--pattern", pat], capture_output=True, timeout=TMO)
        if r.returncode:
            bad_w.append("%s %r: refused" % (" ".join(args), pat)); continue
        fct, _ = L.facts(r.stdout.decode("utf-8", "replace"))
        snull, S = L.set_of(fct["start_set"]["value"])
        got = "nullable" if snull else S
        if got != want:
            bad_w.append("%s %r: start_set %s, by hand %s" % (" ".join(args), pat,
                          got if got == "nullable" else sorted(got),
                          want if want == "nullable" else sorted(want)))
    print("REACH: %d hand-written witnesses (-i, --ucp, utf8 caseless, the conservative arms)" % len(WITNESSES))
    if bad_w:
        bad("[ss-flag] " + "; ".join(bad_w))
    else:
        ok("[ss-flag] all %d witnesses list the start set written by hand from the pattern and its options"
           % len(WITNESSES))


if not os.access(PCREC, os.X_OK):
    bad("no pcrec at %s" % PCREC)
else:
    witness_checks()
    corpus_checks()
print("checks passed: %d" % passed)
print("checks failed: %d" % failed)
sys.exit(1 if failed else 0)
