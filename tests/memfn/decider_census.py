#!/usr/bin/env python3
"""tests/memfn/decider_census.py -- THE DECIDER CENSUS (span_pick.md rev 5.2
§The tables, "The decider census"; Goal 3's check, written by unit 1a).

  decider_census.py --root ROOT [--src DIR] [--map TSV] [--no-plants]

Holds tests/memfn/decider_census.tsv, the DECLARED map of every kit function
(or part, or data definition) that decides a "find the span" question to its
question table or named exception, against the kit's sources:

  A  every member exists: a `fn` member is a top-level definition WITH A BODY
     of that name in its file (a prototype is not one), a `data` member a
     top-level definition; a `part` is its function's definition holding
     the part's anchor; an `excluded` member names a definition or prototype
     that exists. A member's own namespace line in its file
     (`#define NAME MF_NS(NAME)`, exactly its name) belongs to it.
  B  THE BACKSTOP: a grep of memfn/src/*.{c,h,def} for the decider shapes
     (BACKSTOP below) is RED on any hit line that lies in no listed member
     (excluded members included). The hits are COUNTED (K35): fewer than
     HIT_FLOOR is red, so a grep that silently read nothing cannot pass.
  C  THE PLANTS (the check's failing direction; skipped by --no-plants):
     two byte-identical copies of a member's decider loop, each pasted into
     an UNLISTED function of a scratch copy of the sources -- the first loop
     holding a_mass_choose's pick (window.c's `kit_pick_takes(&best,
     p->mass`), the run decision's window loop (presence.c's
     `kit_pick_takes(&bw, wm`, kit_pres_picks' until K38-1) and kit_run_member's own (window.c's
     `kit_pick_takes(&b, c.v`); since unit 1d every argmin asks the one
     before-relation kit_pick_takes, so its call `pick_takes(` is a LIVE
     backstop shape -- must each turn B red; and THREE BYPASS plants, each an
     unlisted function holding a twin argmin that holds NO `pick_takes(` text
     (it compares the best-so-far of a `kit_pick` by `.v`, `<= b.v` and
     `< b.v`, as S1095's SABOTAGE line does): the backstop must see a twin that
     does not ask the relation. A plant that held the call's text would show
     only that a conforming twin is flagged (sp1dfix, review 2026-11-05 F2).
     Since plan_frame.md 3.0a (S2985, its row (D)): a second renderer list,
     a BYTE COPY of the one accessor's loop under a new name, called over the
     search renderer table through REN_ROWS (the spelling every reader
     uses), in unlisted functions, must turn B red too (review 2026-11-09 r1
     s30a F13: the earlier plant indexed `ren_search[i]`, a spelling no
     reader uses).

  D  THE RUN CALLERS (R-38 K38-1, span_runs_sheet.md rev 1.2 §1 Goal 2, §5):
     the map above lists deciders, not who CALLS them, so a reader that asked
     kit_run_member directly would pass A-C. D counts every USE of the
     identifiers of the run member and of the run decision in memfn/src, call
     or not (comment- and string-stripped text, each use attributed to its
     enclosing definition; a definition, prototype or `#define` is no use)
     against RUN_CALLERS, exactly: kit_run_member from kit_run_decide and the
     verify-NO prefilter member (run_member) only; kit_run_decide from P3's
     ports (kit_pres_picks: scan, window, the twin's mass), run_member
     (verify YES), translate (the RQ-2 ranking) and a_mass_choose (Table A's
     in-run stop inside a verify-YES run, R-38 K38-2a: the kit ruling [r1.3
     K7]); and P3's window pick
     (`T_WINDOW` read as a pick row) in kit_run_decide only. Its plants
     (skipped by --no-plants): an unlisted function calling kit_run_member
     directly, one holding it as a non-call (an alias), and one asking the
     window's row, each must turn D red. LIMIT: D counts the USE of
     kit_run_decide, not what a caller does with it: a_mass_choose's in-run
     filter (the `continue` that leaves R's positions to the decision's one
     stop) can be deleted with D green, the call still standing. Its control
     is behavioural, G2's presence family's run-tie-left pass (mech row S3012,
     detector g2pres; review 2026-11-10 r2 k382a FAM-5).

Independent control: the map is hand-written (a declaration), the backstop is
a grep over the raw text and the definition finder a brace count over the
comment- and string-stripped text; neither reads the map to find a hit. What
it cannot see: a decider spelled in no BACKSTOP shape (the list is a NAME-
style filter, coding.md §5 item 4) -- members are added by declaration, the
backstop only catches new copies of the shapes the members use.
"""
import argparse
import os
import re
import shutil
import sys
import tempfile

# The backstop shapes (span_pick.md rev 5.2 §The tables, the census), in two
# kinds. LIVE shapes are the spellings the members use today; EACH must hit at
# least once (K35: a shape that matches nothing guards nothing, and six of
# the old ones had silently gone dead). BYPASS shapes are the spellings a
# decider must use to avoid asking `kit_pick_takes`: the best-so-far of a
# `kit_pick` is compared by `.v` / `->v`, so a twin argmin written beside the
# relation has to say `<= b.v` or `< b.v` (S1095's SABOTAGE line does). They
# match only inside the relation itself (a member) and hold no live hit of
# their own; each is shown by a PLANT whose text holds no `pick_takes(`.
# plan_frame.md 3.0a: the renderer tables' ONE accessor `ren_find(`, the
# table-walk argument `REN_ROWS(ren_` every renderer read passes, the key walk
# `keys &` (a renderer row's key test), and, per renderer table, the support
# table and Table S, its name followed by `[`; the row-walk idioms `.pick ==`
# / `].holds(` are not shapes (they hit non-member lines; these hit none,
# review 2026-11-09 r1 s30a F13).
LIVE = ["kit_walk(", "< best", "tie_takes", "TIE_", "pick_takes(", "ren_find(",
        "REN_ROWS(ren_", "keys &", "ren_search[", "ren_stream[", "ren_check[", "ren_skel[",
        "ren_fused[", "wf_support[", "wf_srows["]
BYPASS = ["< b.v", "<= b.v", "< b->v", "<= b->v", ".v <", "->v <"]
BACKSTOP = LIVE + BYPASS
# EXACT hit count (K35, like MEMBER_COUNT): lines holding any BACKSTOP shape.
# 36 at unit 1a's base; 1d changed the shapes, sp1dfix made the count exact;
# 36 at 1e (Table D's `kit_walk(&wf_dtable` gone: D-hors is T-FIND's row).
# 48 at plan_frame.md 3.0a commit 1 (the `ren_find(` calls and the renderer
# tables' definitions, each inside a member); 50 at 3.0a commit 2 (the
# renderable set's and the composer arm's ren_find( calls; fd_renderer's loop
# held none of the shapes); 60 at the r1 s30a review's fixes (F13's shapes
# `REN_ROWS(ren_`, `keys &`, `wf_support[`, `wf_srows[`; Table S's refusal text,
# the composer's search row and the tables' self-check); 61 at R-38 K38-2a
# (the TIE table's row T_RUN_LEFT, `TIE_LOWER`, inside wf_ties); 67 at
# plan_frame.md 3.0b (wf_arm_pick's E-stmt row walk, the frame part's fixed
# RF_FN / RS_CALLER rows read by wf_frame_of and by wf_agree).
HITS = 67
# EXACT, like row_floors.tsv's ROWS_FLOOR (a floor with slack lets rows vanish
# silently): a unit that moves a decider edits the map AND this number.
# 50 at 1a; 51 at 1b (tie_over gone; kit_tie_takes' prototype and
# kit_tie_member_key in); 50 at 1c (translate:run-rank and
# kit_pres_picks:run-scan gone into kit_run_member, which is in); 52 at 1d
# (mass_domain gone into the candidate builder cands, which is in, and
# kit_pick_takes in with its kit.h prototype); 52 at 1e (fd_route gone into
# fd_find, the one walk; window.c's d_hors_holds out, finder.c's hors_facts
# in; compose.c's fd_renderer, the composer's renderer rows, in); 60 at
# plan_frame.md 3.0a commit 1 (wf_prepare's row now the plan function
# wf_plan_site's; ren_find, the search/stream/check/skeleton/fused renderer
# tables, the support table and Table S in; fd_renderer stays until commit 2
# moves its rows into the search renderer table); 61 at 3.0a commit 2
# (fd_renderer out, its rows the search table's E-stmt rows; the renderable
# set wf_renders and the composer's accessor wf_stmt_arm in: the design's
# expected 59 counted no function for either, plan_frame.md §2.4 "re-derives
# both numbers from its map"); 64 at the r1 s30a review's fixes (wf_stmt_arm
# now wf_stmt_row; Table S's rows wf_srows, its refusal text
# wf_stream_refusal, and the excluded self-check wf_tables_check in); 65 at
# R-38 K38-1 (kit_pres_picks:run-window gone into the run decision
# kit_run_decide, which is in; translate:run-rank back in as the RQ-2 ranking's
# reader of it, span_runs_sheet.md §5); 66 at R-38 K38-2a (kit_run_opts_of
# in: the decision's TIE row, the test-only lever run-tie-left's one reader);
# 67 at R-38 K38-2 (precheck.c's implied_by out with the R-30 implied parts;
# the run decision's WINDOW stretch stretch_window and the route's mode table
# fd_run_modes in: K7 (b)'s mode table and U3's route as the input); 70 at
# plan_frame.md 3.0b (the frame part's wf_frame_of and wf_arm_pick in, the
# MF_TRACE agreement wf_agree excluded).
# R-38 Part D: translate:run-rank became the shared function run_rank (one
# member for one, part_d.md §2.1 item 3; RUN_CALLERS' `translate` with it).
MEMBER_COUNT = 70

# D: THE RUN CALLERS, EXACT (a call site added or lost is red): callee ->
# {enclosing definition: uses}: EVERY use of the identifier (a call, an alias, a
# function pointer), minus its definition, prototype and `#define` (review
# 2026-11-10 r1 k381, K5). `T_WINDOW,` is P3's window pick asking its
# TIE row, `T_WINDOW, key)` (kit.h's enum and window.c's `[T_WINDOW]` table
# row are no calls).
# K38-2: the verify-NO prefilter member asks the decision too (its
# EXACT_AROUND mode), so kit_run_member's one caller is the decision; fd_pres
# asks it for the class's run reply (mf_class.run); the window pick moved into
# the WINDOW mode's stretch, stretch_window.
RUN_CALLERS = {
    r"\bkit_run_member\b": {"kit_run_decide": 1},
    r"\bkit_run_decide\b": {"fd_pres": 1, "kit_pres_picks": 1, "run_member": 1,
                             "run_rank": 1, "a_mass_choose": 1},
    r"\bT_WINDOW\s*,\s*\w+\s*\)": {"stretch_window": 1},
}

passed = failed = 0
SHAPE_HITS = {}     # the last census()'s lines per BACKSTOP shape


def ok():
    global passed
    passed += 1


def bad(msg):
    global failed
    failed += 1
    print("FAIL: " + msg)


def strip_c(text):
    """The text with comments and string/char literals blanked (newlines
    kept), so braces and names inside them count for nothing."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", text[i:j]))
            i = j
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            j = min(j + 1, n)
            out.append(c + re.sub(r"[^\n]", " ", text[i + 1:j - 1]) + (c if j - 1 > i else ""))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def definitions(text):
    """Top-level items of a C file: (name, first line, last line, has_body),
    1-based (has_body: a `{` in the item, so a prototype has none).
    An item starts at a column-0 code line at brace depth 0 (not a
    preprocessor line) and ends at the line where depth is back at 0 and a
    `;` or `}` closes it, or a `)` the next line does not open a body after
    (a top-level macro call: finder.c's `FD_CT(...)` rows). Its name: a
    function's identifier before its first `(`; else the last identifier of
    its depth-0 text before the first `=` or `;`, subscripts dropped (a data
    definition, or a typedef's name)."""
    lines = strip_c(text).split("\n")
    items, depth, start, buf = [], 0, None, []
    for no, ln in enumerate(lines, 1):
        if start is None:
            if depth == 0 and ln[:1] not in ("", " ", "\t", "#", "}", "{"):
                start, buf = no, []
            else:
                depth += ln.count("{") - ln.count("}")
                continue
        buf.append(ln)
        depth += ln.count("{") - ln.count("}")
        nxt = lines[no] if no < len(lines) else ""
        if depth == 0 and (";" in ln or "}" in ln or
                           (ln.rstrip().endswith(")") and not nxt.startswith("{"))):
            text = "\n".join(buf)
            items.append((item_name(text), start, no, "{" in text))
            start = None
    return items


def item_name(src):
    flat, d = [], 0
    for ch in src:                       # the depth-0 text
        if ch == "{":
            d += 1
        elif ch == "}":
            d -= 1
        elif d == 0:
            flat.append(ch)
    flat = "".join(flat)
    head = re.split(r"[=;]", flat, maxsplit=1)[0]
    m = re.search(r"([A-Za-z_]\w*)\s*\(", head)
    if m:
        return m.group(1)
    m = re.findall(r"[A-Za-z_]\w*", re.sub(r"\[[^\]]*\]", "", head))
    return m[-1] if m else None


def read_map(path):
    rows = []
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("#") or not ln.strip():
                continue
            f = ln.rstrip("\n").split("\t")
            if len(f) != 6:
                bad("map line has %d columns, not 6: %r" % (len(f), ln))
                continue
            rows.append(dict(zip(("file", "member", "kind", "anchor", "answers", "retires"), f)))
    return rows


def census(src, rows, count=True):
    """Checks A and B over the sources in `src`; returns (hits, stray lines,
    check-A error messages)."""
    errs = []
    defs, raw = {}, {}
    for fn in sorted(os.listdir(src)):
        if fn.endswith((".c", ".h", ".def")):
            with open(os.path.join(src, fn)) as fh:
                raw[fn] = fh.read()
            defs[fn] = definitions(raw[fn])
    # A: every member exists; its line span
    spans = []
    for r in rows:
        name, _, part = r["member"].partition(":")
        hit = [d for d in defs.get(r["file"], []) if d[0] == name]
        if r["kind"] in ("fn", "part"):
            hit = [d for d in hit if d[3]]       # a prototype is not the decider
        if not hit:
            errs.append("%s: member %s is not defined there (with a body, for fn/part)" % (r["file"], r["member"]))
            continue
        if r["kind"] == "part":
            body = "\n".join(raw[r["file"]].split("\n")[hit[0][1] - 1:hit[0][2]])
            if r["anchor"] == "-" or r["anchor"] not in body:
                errs.append("%s: part %s's anchor %r is not inside %s" % (r["file"], r["member"], r["anchor"], name))
                continue
        elif r["kind"] not in ("fn", "data", "excluded"):
            errs.append("%s: member %s has kind %r" % (r["file"], r["member"], r["kind"]))
            continue
        if count:
            ok()
        spans += [(r["file"], d[1], d[2]) for d in hit]
        # its namespace line (`#define NAME MF_NS(NAME)`, kit.h) is the member's
        ns = re.compile(r"#define\s+%s\s+MF_NS\(%s\)\s*$" % (name, name))
        spans += [(r["file"], no, no) for no, ln in enumerate(raw[r["file"]].split("\n"), 1)
                  if ns.match(ln)]
    # B: every backstop hit lies in a member
    hits, stray = 0, []
    SHAPE_HITS.clear()
    for fn, text in raw.items():
        for no, ln in enumerate(text.split("\n"), 1):
            for p in BACKSTOP:
                if p in ln:
                    SHAPE_HITS[p] = SHAPE_HITS.get(p, 0) + 1
            if any(p in ln for p in BACKSTOP):
                hits += 1
                if not any(f == fn and a <= no <= b for f, a, b in spans):
                    stray.append("%s:%d: %s" % (fn, no, ln.strip()))
    return hits, stray, errs


def run_callers(src):
    """D: per RUN_CALLERS pattern, {enclosing definition: count} over the
    stripped sources; a call outside every definition body is keyed '?'. A
    match on the callee's own definition or prototype line is not a call."""
    got = {}
    for fn in sorted(os.listdir(src)):
        if not fn.endswith((".c", ".h")):
            continue
        with open(os.path.join(src, fn)) as fh:
            raw = fh.read()
        text = strip_c(raw)
        lines = text.split("\n")
        defs = definitions(raw)
        for pat in RUN_CALLERS:
            callee = re.match(r"\\b(\w+)", pat).group(1)
            for no, ln in enumerate(lines, 1):
                if ln.lstrip().startswith("#"):
                    continue            # #define / #include: no use
                for _ in re.finditer(pat, ln):
                    owner = [d for d in defs if d[1] <= no <= d[2]]
                    if owner and owner[0][0] == callee and (not owner[0][3] or no == owner[0][1]
                                                            or "{" not in "\n".join(lines[owner[0][1] - 1:no])):
                        continue        # its own definition head or prototype
                    key = owner[0][0] if owner and owner[0][3] else "?"
                    got.setdefault(pat, {})
                    got[pat][key] = got[pat].get(key, 0) + 1
    return got


def run_callers_check(src, quiet=False):
    """Errors of D over `src` (empty: RUN_CALLERS holds exactly)."""
    errs, got = [], run_callers(src)
    for pat, want in RUN_CALLERS.items():
        have = got.get(pat, {})
        if have != want:
            errs.append("run callers of %s: %s, not %s" % (pat, have, want))
        elif not quiet:
            print("run callers of %s: %s" % (pat, ", ".join("%s %d" % kv for kv in sorted(have.items()))))
    return errs


def plant(src, tmp, fname, anchor, opener):
    """A scratch copy of `src` whose `fname` gains an unlisted function
    holding a byte-identical copy of the loop that opens with `opener` and
    holds `anchor` (the loop's text up to its closing brace at its own
    indentation)."""
    shutil.copytree(src, tmp)
    path = os.path.join(tmp, fname)
    with open(path) as fh:
        lines = fh.read().split("\n")
    at = next((i for i, ln in enumerate(lines) if anchor in ln), None)
    if at is None:
        return None, "anchor %r is not in %s (respelled? re-aim the plant)" % (anchor, fname)
    tops = [i for i in range(at + 1) if lines[i].lstrip().startswith(opener)]
    if not tops:
        return None, "no %r opener at or above the anchor in %s" % (opener, fname)
    top = max(tops)
    ind = len(lines[top]) - len(lines[top].lstrip())
    end = next((i for i in range(top + 1, len(lines))
                if lines[i].startswith(" " * ind + "}") and len(lines[i]) - len(lines[i].lstrip()) == ind), None)
    if end is None:
        return None, "the loop opened at %s:%d has no closing brace" % (fname, top + 1)
    loop = lines[top:end + 1]
    with open(path, "a") as fh:
        fh.write("\nstatic void census_plant(void)\n{\n" + "\n".join(loop) + "\n}\n")
    return len(loop), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--src", help="the kit source dir (default ROOT/memfn/src)")
    ap.add_argument("--map", help="the census map (default ROOT/tests/memfn/decider_census.tsv)")
    ap.add_argument("--no-plants", action="store_true")
    a = ap.parse_args()
    src = a.src or os.path.join(a.root, "memfn/src")
    rows = read_map(a.map or os.path.join(a.root, "tests/memfn/decider_census.tsv"))
    (ok() if len(rows) == MEMBER_COUNT else
     bad("the map holds %d members, not MEMBER_COUNT %d (edit both together)" % (len(rows), MEMBER_COUNT)))
    hits, stray, errs = census(src, rows)
    for e in errs:
        bad(e)
    print("backstop hits: %d (expected %d), outside a member: %d" % (hits, HITS, len(stray)))
    (ok() if hits == HITS else bad("backstop hits %d, not HITS %d (edit both together)" % (hits, HITS)))
    for sh in LIVE:
        (ok() if SHAPE_HITS.get(sh) else bad("the live backstop shape %r matches no line (dead: respell or delete it)" % sh))
    for s in stray:
        bad("a decider shape outside every census member: " + s)
    if not stray:
        ok()
    # D: the run callers
    derrs = run_callers_check(src)
    for e in derrs:
        bad(e)
    if not derrs:
        ok()
    if not a.no_plants:
        # D's plants: a reader asking the run member directly; one asking the
        # window's row beside the run decision
        for label, body in (("kit_run_member", "    (void)kit_run_member(NULL, NULL, NULL, 0, 0, NULL, 0);\n"),
                            ("kit_run_member alias", "    void *census_alias = (void *)kit_run_member;\n"),
                            ("T_WINDOW", "    (void)kit_pick_takes(&b, 0, T_WINDOW, 0);\n")):
            text = ("\nstatic void census_reader(void)\n{\n    kit_pick b = KIT_PICK_NONE;\n" + body + "}\n")
            with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as t:
                shutil.copytree(src, os.path.join(t, "src"))
                with open(os.path.join(t, "src", "compose.c"), "a") as fh:
                    fh.write(text)
                perr = run_callers_check(os.path.join(t, "src"), quiet=True)
                (ok() if any("census_reader" in e for e in perr) else
                 bad("run-callers plant %s (a direct call in an unlisted function) did not turn D red" % label))
                print("run-callers plant %s: %d error(s)" % (label, len(perr)))
        for fname, anchor, opener in (("window.c", "kit_pick_takes(&best, p->mass", "for ("),
                                      ("presence.c", "kit_pick_takes(&bw, wm", "for (int w"),
                                      ("window.c", "kit_pick_takes(&b, c.v", "for (")):
            with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as t:
                n, why = plant(src, os.path.join(t, "src"), fname, anchor, opener)
                if why:
                    bad("plant %s: %s" % (fname, why))
                    continue
                _, pst, _ = census(os.path.join(t, "src"), rows, count=False)
                planted = [s for s in pst if s.startswith(fname + ":")]
                (ok() if planted else
                 bad("plant %s (%d lines, `%s`) did not turn the backstop red" % (fname, n, anchor)))
                print("plant %s `%s`: %d stray hit(s)" % (fname, anchor, len(planted)))
        # C2: the bypass plants (no `pick_takes(` text in any of them)
        for label, cmp_line in (("<= b.v", "if (b.pos < 0 || v[j] <= b.v)"),
                                ("< b.v", "if (b.pos < 0 || v[j] < b.v)"),
                                (".v <", "if (b.pos < 0 || b.v < v[j])")):
            text = ("\nstatic void census_bypass(const unsigned long long *v, unsigned n)\n{\n"
                    "    kit_pick b = KIT_PICK_NONE;\n"
                    "    for (unsigned j = 0; j < n; j++)\n"
                    "        " + cmp_line + "\n"
                    "            b = (kit_pick){ (int)j, (int32_t)j, v[j] };\n}\n")
            if "pick_takes(" in text:
                bad("bypass plant %s holds the relation's call text" % label)
                continue
            with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as t:
                shutil.copytree(src, os.path.join(t, "src"))
                with open(os.path.join(t, "src", "window.c"), "a") as fh:
                    fh.write(text)
                _, pst, _ = census(os.path.join(t, "src"), rows, count=False)
                planted = [x for x in pst if x.startswith("window.c:")]
                (ok() if planted else bad("bypass plant `%s` (no pick_takes( text) did not turn the backstop red" % label))
                print("bypass plant `%s`: %d stray hit(s)" % (label, len(planted)))
        # C2r (plan_frame.md 3.0a §5 row (D), S2985): a SECOND renderer list in
        # unlisted functions, a byte copy of the one accessor's loop under a new
        # name, called over the search renderer table through REN_ROWS (review
        # 2026-11-09 r1 s30a F13, its plant b1): the loop's key walk and the
        # call's table argument must each be a stray
        text = ("\nstatic const void *census_find2(const void *rows, size_t n, size_t size, "
                "wf_frame_row f, uint32_t key,\n                                const void *x)\n{\n"
                "    for (size_t i = 0; i < n; i++) {\n"
                "        const ren_key *k = (const void *)((const char *)rows + i * size);\n"
                "        if (k->frame == f && (k->keys & key) && (!k->holds || k->holds(x))) return k;\n"
                "    }\n    return NULL;\n}\n"
                "static const void *census_twin_b1(fd_form pick)\n{\n"
                "    return census_find2(REN_ROWS(ren_search), E_FIND, REN_PICK(pick), NULL);\n}\n")
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as t:
            shutil.copytree(src, os.path.join(t, "src"))
            with open(os.path.join(t, "src", "window.c"), "a") as fh:
                fh.write(text)
            _, pst, _ = census(os.path.join(t, "src"), rows, count=False)
            planted = [x for x in pst if x.startswith("window.c:")]
            (ok() if len(planted) == 2 else
             bad("renderer-list plant (S2985) turned %d line(s) stray, not its 2 (the copied key "
                 "walk and the REN_ROWS call)" % len(planted)))
            print("renderer-list plant (S2985): %d stray hit(s)" % len(planted))
        # C3: a decider reduced to a bare prototype must turn A red.
        fn_row = next(r for r in rows if r["kind"] == "fn")
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as t:
            shutil.copytree(src, os.path.join(t, "src"))
            path = os.path.join(t, "src", fn_row["file"])
            with open(path) as fh:
                text = fh.read()
            item = next((d for d in definitions(text) if d[0] == fn_row["member"] and d[3]), None)
            if item is None:
                bad("plant prototype: %s not found as a definition" % fn_row["member"])
            else:
                lines = text.split("\n")
                lines[item[1] - 1:item[2]] = ["static void %s(void);" % fn_row["member"]]
                with open(path, "w") as fh:
                    fh.write("\n".join(lines))
                _, _, perr = census(os.path.join(t, "src"), rows, count=False)
                hit = [e for e in perr if fn_row["member"] in e]
                (ok() if hit else bad("plant prototype: %s as a bare prototype kept its row green" % fn_row["member"]))
                print("plant prototype %s: %d error(s)" % (fn_row["member"], len(hit)))
    print("checks passed: %d" % passed)
    print("checks failed: %d" % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
