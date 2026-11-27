#!/usr/bin/env python3
"""[K155] no heap builder lives across a refusal: the compile path's builder census as a gate.

THE RULE (src/core/CLAUDE.md): a builder that can be interrupted by
`pcrec_ctx_fail`/`pcrec_ctx_nomem` is arena-backed, because a refusal
longjmps to compile_driver's one setjmp and only the compile's arena and the
Job's own buffers are freed there (job_cleanup). A heap builder live at that
moment is stranded (K155: 32 KB per refused compile in target_headers_render).

WHAT THIS SCANS. Every .c file in the COMPILE-PATH layers (src/core, src/enc,
src/parse, src/ir, src/facts, src/opt, src/gen), comments and literals
blanked, for three
shapes, each a finding unless an ALLOWLIST row below names its file and
function with the reason it is safe:
  1. a StrBuf OBJECT (not a pointer) defined without `= pcrec_sb_scratch(`:
     `StrBuf b = {0}`, `StrBuf b = { .cx = cx }`, `StrBuf b;` (a struct
     field in a .c file included);
  2. a private Arena object (`Arena a = ...` / `Arena a;`): its blocks are
     heap the compile's arena does not own;
  3. a raw heap call (malloc, calloc, realloc, strdup, strndup, realpath).
And the other half of the rule, the Job-owned builders: every StrBuf field
of `Job` (src/core/internal.h) must be freed in compile.c's job_cleanup.
Every src/ subdirectory is either a scanned layer or an EXCLUDED one with its
reason (EXCLUDED below), so a new layer cannot go unscanned.

src/dump IS NOT SCANNED, and not because it runs outside a compile: its two
hooks (facts_dump.c `fd_hook`, callouts_dump.c `lc_hook`) run INSIDE
compile_driver with heap StrBufs live. They are safe by the CALLER-OWNS rule
(src/core/CLAUDE.md): a hook's builders belong to the hook's caller, which
frees them when compile_driver returns nonzero, and the longjmp never leaves
compile_driver. The rest of src/dump renders after the pipeline returns.

WHAT IT DOES NOT SEE (said, not implied): a heap block reached through
another function's return value (a callee's malloc'd result, e.g. a part
compile's `pcrec_output`); whether an allowlisted heap call is in fact
freed before every refusal; non-memory RESOURCES (a FILE*, a DIR*, an fd)
live across a refusal; declarations whose type and first name sit on
different lines, or spelled through a macro or a typedef in a header;
.h/.inc files; heap calls spelled `(malloc)(`, `reallocarray`, `asprintf`,
`getline`, `open_memstream`, `aligned_alloc`, `posix_memalign`, `mmap`; a
StrBuf field inside a local struct type. The INDEPENDENT control is dynamic
and shares nothing with this scan: tests/core/alloc_check.c fails every
allocation of its witnesses in turn and fails a refusal that leaves the
injected tree's live heap above zero (`make test-alloc`) -- but ONLY for the
sites its witnesses W1-W6 reach. Rows no witness reaches are SINGLE-CONTROL
(this scan only): today S3570's landmark-move `round` and S3572's second
object beside `nb` (alloc_check's known_stranded row 2 excuses every sb.c
block allocated under target_headers_render, so it cannot tell them apart).

CONTROLS (learnings.md section 3): self-test fixtures (lines that MUST be
flagged and MUST NOT be) run through the same detector first; every
allowlist row must be REACHED (a row that stops matching is stale and
FAILS); population floors on the files scanned, the scratch builders seen
and the Job's StrBuf fields make a scan that silently saw nothing a failure
(K35); the layer census FAILS an unclassified or missing src/ subdirectory.
Each of those three rules has its own plant, run first (self_test_controls:
a sentinel row that must come back stale, an empty population that must
trip every floor, a listing with a new and a missing layer).

THE SCOPE RULES ([ARENA-SCOPES], docs/design/arena_scopes.md "Discipline and
checks"), on the same noise-stripped text, each with fixtures that must FAIL:
  L2-static  every `pcrec_scope_open` has a `pcrec_scope_close` in its
             function (a longjmp is not a return: the teardown releases);
  L4         a `pcrec_scope_*` result is stored only in a plain local (never
             through `->` or `.` into a longer-lived struct), and no
             `pcrec_scope_` call sits under src/parse/ outside SCOPE_PARSE_ALLOW
             (one row, unit F6's `uprops_produce`);
  D-7        in src/core/arena.c and sb.c every `pcrec_ctx_nomem(`/
             `pcrec_ctx_fail(` takes `pcrec_err_chan(` as its Ctx, and no
             arena.c function calls `pcrec_arena_alloc` (the test link wraps
             it; a call from inside arena.c would bypass the wrap);
  readers    `pcrec_arena_open_p` (W7's read-only accessor) is called by no
             file under src/, cli/ or lib/ (its reader is tests/core/alloc_check.c).
What they do NOT see: a scope handle passed to a callee that stores it; an
open and close paired in one function but on different paths (the runtime's
`pcrec_scope_check_closed` and the L1 stamp check are that control).

Usage: scratch_builder_check.py ROOT   (exit 0 clean, 1 findings, 2 setup error)
"""
import os
import re
import sys

LAYERS = ("core", "enc", "parse", "ir", "facts", "opt", "gen")
# src/ subdirectories NOT scanned, each with its reason (the layer census
# fails any subdirectory in neither tuple)
EXCLUDED = {
    "dump": "table surfaces after the pipeline; its in-compile hooks hold caller-owned builders (header)",
    "findings": "shipped analyses as .rxt text, no C source",
}
MIN_JOB_FIELDS = 6       # Job's StrBuf fields at this writing
MIN_FILES = 45           # half the compile-path .c files at this writing (91), D110 floor
MIN_SCRATCH = 12         # half the pcrec_sb_scratch constructions at this writing (23), D110 floor

# (file, function, shape, reason). shape: strbuf | arena | heap, or
# `shape:NAME` to admit only the object of that NAME (a row that must not
# also admit a second, leaking object of the same shape in its function).
ALLOW = [
    # -- the heap mechanisms themselves ---------------------------------
    ("src/core/sb.c", "sb_store", "heap", "the StrBuf storage primitive (heap side; job buffers and outside-a-compile buffers)"),
    ("src/core/sb.c", "sb_grow", "heap", "a heap StrBuf's realloc into a temporary (K7)"),
    ("src/core/sb.c", "pcrec_sb_take", "heap", "take hands the caller a heap string by contract"),
    ("src/core/arena.c", "pcrec_arena_alloc", "heap", "the arena's own blocks"),
    ("src/core/arena.c", "rec_take", "heap", "[ARENA-SCOPES] the registry's entry record: linked at once, released by its scope's close or the arena's teardown"),
    ("src/core/arena.c", "pcrec_scope_malloc", "heap", "[ARENA-SCOPES] a HEAP entry's block, stored into a record already linked (holding NULL until then)"),
    ("src/core/compile.c", "compile_driver", "heap", "the Job itself, freed by job_cleanup"),
    # -- heap arrays the Job owns from birth (job_cleanup frees them) ----
    ("src/ir/nfa.c", "nst", "heap", "the Job's NFA state array, realloc'd in place"),
    ("src/ir/dfa.c", "tab_grow", "heap", "the Job DFA's intern table (old one freed and NULLed first)"),
    ("src/ir/dfa.c", "intern", "heap", "the Job DFA's state array, realloc'd in place"),
    ("src/opt/dfamemo.c", "pcrec_build_min_dfa", "heap", "the restored machine's state array, attached to the Job's Dfa before any further allocation (dfa_copy)"),
    # -- hand-freed temporaries never live across a refusal --------------
    ("src/opt/scanedge.c", "pcrec_scanedge_dfa", "heap", "ten temporaries freed on every exit; the only refusals while live are their own allocation failures, which free them first (coding.md 1.6)"),
    # -- [ARENA-SCOPES] clients: LIVE across a refusal today, stranded on it (K155
    #    stays open until that row registers scoped arenas on the Ctx) --------
    ("src/gen/memfn_stamps.c", "target_headers_render", "strbuf:nb", "[ARENA-SCOPES] client: K155's own site, the whole-artifact rewrite of csb"),
    ("src/gen/memfn_stamps.c", "splice_mark", "strbuf:tail", "[ARENA-SCOPES] client: a whole-artifact tail rewrite"),
    ("src/gen/part_layout.c", "render_buf", "strbuf:o", "[ARENA-SCOPES] client: the whole-artifact layout-mark rewrite"),
    # -- outside a compile: no Ctx, so no longjmp can strand anything ------
    ("src/core/compile.c", "pcrec_subst_compile", "arena", "the subst compile: a detached arena, freed on return, no Ctx"),
    ("src/gen/emit_subst.c", "support_unit", "strbuf", "the subst support unit: no Ctx"),
    ("src/gen/emit_subst.c", "pcrec_emit_subst", "strbuf", "the subst emitter: no Ctx"),
    ("src/gen/emit_subst.c", "pcrec_emit_subst", "arena", "the subst emitter: a detached arena, no Ctx"),
    ("src/parse/ks_analysis.c", "analysis_write_canonical", "strbuf", "a knowledge-module view writer: no Ctx, errors by return"),
    ("src/parse/ks_analysis.c", "analysis_write_decoded", "strbuf", "a knowledge-module view writer: no Ctx, errors by return"),
    ("src/parse/rxt_source.c", "*", "strbuf", "the .rxt source reader: its own arena has no Ctx, errors by return (rxt_fail), no longjmp"),
    ("src/parse/rxt_source.c", "*", "heap", "the .rxt source reader: no Ctx, no longjmp; frees its own"),
    # -- not a builder -----------------------------------------------------
    ("src/gen/emit_compound.c", "part_splice", "strbuf", "a non-owning VIEW of a finished text for pcrec_sb_splice: never grown or freed"),
]

def strip_noise(text):
    """Blank comments and string/char literals, keeping line structure."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join("\n" if ch == "\n" else " " for ch in text[i:j]))
            i = j
        elif text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == "\\" else 1
            j = min(j + 1, n)
            out.append("".join("\n" if ch == "\n" else " " for ch in text[i:j]))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)

STRBUF = re.compile(r"(?<![\w*])StrBuf\s+(?=[\w*])")
ARENA = re.compile(r"(?<![\w*])Arena\s+(?!\*)(\w+)\s*(=|;)")
HEAP = re.compile(r"(?<![\w.>])(malloc|calloc|realloc|strdup|strndup|realpath)\s*\(")
SCRATCH = re.compile(r"\bpcrec_sb_scratch\s*\(")

def strbuf_declarators(line):
    """-> (name, initializer) for EVERY declarator of each `StrBuf ...`
    declaration on the line (review r96 CHECK-1: `StrBuf nb = {..}, leak =
    {..};` declares two objects). The list runs to the `;` at bracket depth
    0, split at depth-0 commas; an initializer still open at the line's end
    is taken as written so far (so `StrBuf b = {` is seen). A parameter
    (`(StrBuf *a, ...`) contributes its first declarator only, and a pointer
    declarator is not an object."""
    out = []
    for m in STRBUF.finditer(line):
        before = line[:m.start()].rstrip()
        param = before.endswith(("(", ","))
        parts, cur, depth, i = [], "", 0, m.end()
        while i < len(line):
            c = line[i]
            if c in "({[":
                depth += 1
            elif c in ")}]":
                if depth == 0:
                    break
                depth -= 1
            elif c in ",;" and depth == 0:
                parts.append(cur)
                cur = ""
                if c == ";" or param:
                    break
                i += 1
                continue
            cur += c
            i += 1
        else:
            if cur.strip():
                parts.append(cur)
        if cur.strip() and not parts:
            parts.append(cur)
        for d in parts[:1] if param else parts:
            d = d.strip()
            nm = re.match(r"(\w+)", d)
            if not nm:
                continue   # a pointer declarator, or nothing
            _, eq, init = d.partition("=")
            out.append((nm.group(1), init.strip() if eq else ""))
    return out

def classify(line):
    """-> list of (shape, object name or '') a (noise-stripped) line holds."""
    shapes = []
    for name, init in strbuf_declarators(line):
        if not init.startswith("pcrec_sb_scratch("):
            shapes.append(("strbuf", name))
    for m in ARENA.finditer(line):
        shapes.append(("arena", m.group(1)))
    if HEAP.search(line):
        shapes.append(("heap", ""))
    return shapes

def admits(row, rel, fname, shape, name):
    kind, _, want = row[2].partition(":")
    return (row[0] == rel and kind == shape and row[1] in ("*", fname)
            and (not want or want == name))

MUST_FLAG = [
    ("StrBuf nb = { .cx = cx };", "strbuf"),
    ("    StrBuf sb = { 0 };", "strbuf"),
    ("StrBuf lit;", "strbuf"),
    ("StrBuf b[4] = {{0}};", "strbuf"),
    ("StrBuf u = { 0 }, all = { 0 };", "strbuf:all"),
    # a heap object in a SECOND declarator (review r96 CHECK-1)
    ("StrBuf nb = { .cx = cx }, leak = { .cx = cx };", "strbuf:leak"),
    ("StrBuf a = pcrec_sb_scratch(&cx->arena), b = { 0 };", "strbuf:b"),
    ("StrBuf b = {", "strbuf:b"),
    ("Arena a = { NULL, c->cx };", "arena"),
    ("char *np = realloc(sb->p, cap);", "heap"),
    ("int *t = malloc(n * sizeof *t);", "heap"),
    ("char *s = strdup(x);", "heap"),
]
MUST_PASS = [
    "StrBuf nb = pcrec_sb_scratch(&cx->arena);",
    "StrBuf a = pcrec_sb_scratch(&cx->arena), b = pcrec_sb_scratch(&cx->arena);",
    "void g(const StrBuf *a, StrBuf *b);",
    "StrBuf *c = &cx->job->csb;",
    "static void f(StrBuf *sb, const char *s)",
    "const StrBuf *src",
    "Arena *a = &cx->arena;",
    "void *p = pcrec_arena_alloc(&cx->arena, n);",
    "pcrec_sb_free(&lines);",
    "x->malloc_hint = 0;",
]

FUNC_HEAD = re.compile(r"\b(\w+)\s*\(")

def functions(clean_lines):
    """-> per line, the enclosing top-level function's name ('' outside one).
    House style opens a function body with `{` at column 0 and closes it
    with `}` at column 0; the name is the last `name(` before the brace."""
    names, cur, last = [], "", ""
    for l in clean_lines:
        if l.startswith("{") and not cur:
            cur = last
        names.append(cur)
        if l.startswith("}") and cur:
            cur = ""
        if not cur and l[:1] not in (" ", "\t", "#", "") :
            hs = FUNC_HEAD.findall(l)
            if hs:
                last = hs[0]
    return names

def layer_census(subdirs):
    """-> one message per src/ subdirectory neither scanned nor EXCLUDED,
    and per scanned layer that is not there."""
    out = [f"src/{d} is neither a scanned layer (LAYERS) nor EXCLUDED with a reason"
           for d in sorted(subdirs) if d not in LAYERS and d not in EXCLUDED]
    out += [f"scanned layer src/{d} does not exist" for d in LAYERS if d not in subdirs]
    return out

def stale_rows(allow, reached):
    """-> the allowlist rows nothing matched."""
    return [k for k in range(len(allow)) if k not in reached]

def floor_failures(nfiles, nscratch, nfields):
    """-> one message per population below its floor (K35)."""
    out = []
    if nfields < MIN_JOB_FIELDS:
        out.append(f"found only {nfields} StrBuf fields of Job (floor {MIN_JOB_FIELDS}): the parse is not reaching the struct")
    if nfiles < MIN_FILES:
        out.append(f"scanned only {nfiles} compile-path .c files (floor {MIN_FILES})")
    if nscratch < MIN_SCRATCH:
        out.append(f"saw only {nscratch} pcrec_sb_scratch builders (floor {MIN_SCRATCH}): the scan is not reaching the tree")
    return out

# a row no file can match: the stale-row rule's plant (self_test_controls)
SENTINEL = ("src/core/no_such_file.c", "no_such_fn", "heap", "the stale-row rule's own plant")

def self_test_controls(reached_with_sentinel, nallow):
    """-> a message per control whose plant it did NOT catch (review r96
    CHECK-4: mutants deleting these rules passed every suite)."""
    out = []
    if nallow not in stale_rows(ALLOW + [SENTINEL], reached_with_sentinel):
        out.append("the stale-row rule did not report a row nothing matches")
    if len(floor_failures(0, 0, 0)) != 3:
        out.append("an empty population did not trip all three floors")
    census = layer_census(set(LAYERS[1:]) | set(EXCLUDED) | {"newlayer"})
    if not any("src/newlayer" in m for m in census) or not any(f"src/{LAYERS[0]} " in m for m in census):
        out.append("the layer census missed a new or a missing src/ subdirectory")
    return out

def scan(root, allow):
    findings, reached, nfiles, nscratch = [], set(), 0, 0
    for layer in LAYERS:
        for dp, dn, fn in os.walk(os.path.join(root, "src", layer)):
            for f in sorted(fn):
                if not f.endswith(".c"):
                    continue
                path = os.path.join(dp, f)
                rel = os.path.relpath(path, root)
                raw = open(path, encoding="utf-8", errors="replace").read()
                lines = raw.split("\n")
                clean = strip_noise(raw).split("\n")
                fnames = functions(clean)
                nfiles += 1
                for i, l in enumerate(clean):
                    nscratch += len(SCRATCH.findall(l))
                    for shape, name in classify(l):
                        row = next((k for k, a in enumerate(allow)
                                    if admits(a, rel, fnames[i], shape, name)), None)
                        if row is None:
                            findings.append((rel, i + 1, fnames[i] or "<file scope>", shape, lines[i].strip()))
                        else:
                            reached.add(row)
    return findings, reached, nfiles, nscratch

def job_fields(root):
    """-> (StrBuf fields of Job, the set pcrec_sb_free'd in job_cleanup)."""
    h = strip_noise(open(os.path.join(root, "src/core/internal.h"), encoding="utf-8").read())
    end = re.search(r"\n\}\s*Job\s*;", h)
    start = h.rfind("\ntypedef struct", 0, end.start()) if end else -1
    if start < 0:
        return None, None
    body = h[start:end.start()]
    fields = set()
    for d in re.finditer(r"(?<![\w*])StrBuf\s+([^;]*);", body):
        for name in d.group(1).split(","):
            name = name.strip()
            if name and not name.startswith("*"):
                fields.add(re.match(r"\w+", name).group(0))
    c = strip_noise(open(os.path.join(root, "src/core/compile.c"), encoding="utf-8").read())
    j = re.search(r"\nstatic void job_cleanup\s*\(Ctx \*cx\)\n\{(.*?)\n\}", c, re.S)
    if not j:
        return fields, None
    freed = set(re.findall(r"pcrec_sb_free\s*\(\s*&cx->job->(\w+)\s*\)", j.group(1)))
    return fields, freed

# [ARENA-SCOPES] scope rules (L4, L2-static, D-7, readers). A LINE scanner over strip_noise'd text, so it does NOT see
# (r104 CHECKS-1/CHECKS-2; deliberate regex limits, listed so nobody assumes more):
#   - a scope result stored THROUGH A LOCAL (`char **pp = &x->t; *pp = pcrec_scope_malloc(..)`) or returned out;
#   - a call or name written in parentheses (`(pcrec_scope_malloc)(..)`), or hidden in a macro body;
#   - code in a `.h` (inline functions) or at file scope (initialisers): only .c function bodies are scanned;
#   - a Scope handle copied out by any form but a plain `field = name;` (a memcpy, a struct literal);
#   - a CHAN_CALL whose channel argument starts on the line after the one after the call's `(`.
# What it does see: a store `x->f = [cast] pcrec_scope_*(` and a handle copy `x->f = NAME;` for a `Scope NAME` of the file.
# [ARENA-SCOPES] L4: the src/parse functions allowed to use a scope
# (file, function, reason). The one row is S29 `uprops_produce` (unit F6, r103 C20): a scope opened and closed inside the
# parse, on the attempt arena, whose child holds the transient \p decode; no AST payload can capture it (D70 not met)
SCOPE_PARSE_ALLOW = [
    ("src/parse/mod_uprops.c", "uprops_produce",
     "S29: the transient \\p decode lives in a scope child, closed before the function returns (the compile arena costs +29% peak at 4,000 \\p{L}, refused)"),
]
SCOPE_CALL = re.compile(r"\bpcrec_scope_\w+\s*\(")
SCOPE_STORE = re.compile(r"(->|\.)\s*\w+(\s*\[[^]]*\])?\s*=\s*(\(\s*[\w\s*]+\)\s*)?pcrec_scope_\w+\s*\(")
SCOPE_DECL = re.compile(r"\bScope\s+(\w+)\s*[=;,]")
# `(?!\s|...)` after `\s*`: backtracking `\s*` shorter must not read the whitespace as "some other argument"
CHAN_CALL = re.compile(r"\bpcrec_ctx_(nomem|fail)\s*\(\s*(?!\s|pcrec_err_chan\s*\()")
CHAN_OPEN_EOL = re.compile(r"\bpcrec_ctx_(nomem|fail)\s*\(\s*$")
ARENA_ALLOC_CALL = re.compile(r"\bpcrec_arena_alloc\s*\(")
OPEN_P_CALL = re.compile(r"\bpcrec_arena_open_p\s*\(")
# [ARENA-SCOPES] D-11 (r103 C12): keyed on the TYPE `mf_arena`, so both spellings of a binder are seen: an assignment
# (`ma->u = X;`, `ma.u = X;`) and a brace initializer (`mf_arena ar = { X, ...};`, the kit's own idiom). The one allowed
# binder is pcrec_memfn_art's, and it must bind `&cx->arena`; a `mf_art_begin(` call outside that function is a finding.
MF_DECL = re.compile(r"(?<![\w*])mf_arena\s+(\*?)\s*(\w+)\s*(=\s*\{\s*([^,}]*))?")
MF_BEGIN = re.compile(r"\bmf_art_begin\s*\(")
D11_FILE, D11_FN, D11_VALUE = "src/gen/memfn_sites.c", "pcrec_memfn_art", "&cx->arena"

def d11_findings(rel, clean, fnames):
    """-> ((line, rule, message) findings, allowed binders seen) for one file."""
    out, seen = [], 0
    names = set()
    for l in clean:
        for m in MF_DECL.finditer(l):
            names.add(m.group(2))
    assign = re.compile(r"\b(%s)\s*(->|\.)\s*u\s*=\s*([^;]*);" % "|".join(sorted(names))) if names else None
    for i, l in enumerate(clean):
        fn = fnames[i]
        binds = [(m.group(4) or "").strip() for m in MF_DECL.finditer(l) if m.group(3)]
        if assign:
            binds += [m.group(3).strip() for m in assign.finditer(l)]
        for v in binds:
            if rel == D11_FILE and fn == D11_FN and v == D11_VALUE:
                seen += 1
            else:
                out.append((i + 1, "D-11", "an mf_arena binder outside pcrec_memfn_art, or one not binding &cx->arena"))
        if MF_BEGIN.search(l) and fn and not (rel == D11_FILE and fn == D11_FN):
            out.append((i + 1, "D-11", "mf_art_begin called outside pcrec_memfn_art (the art's mf_arena is the attempt's arena)"))
    return out, seen

def scope_rule_findings(rel, clean, fnames):
    """-> (line, rule, message) for one file's scope-rule violations."""
    out = []
    opens, closes = {}, set()
    scopes = {m.group(1) for l in clean for m in SCOPE_DECL.finditer(l)}
    handle_store = re.compile(r"(->|\.)\s*\w+(\s*\[[^]]*\])?\s*=\s*&?\s*(%s)\s*;" % "|".join(sorted(scopes))) if scopes else None
    for i, l in enumerate(clean):
        fn = fnames[i]
        if fn and re.search(r"\bpcrec_scope_open\s*\(", l):   # a call, not a definition line
            opens.setdefault(fn, i + 1)
        if fn and re.search(r"\bpcrec_scope_close\s*\(", l):
            closes.add(fn)
        if SCOPE_STORE.search(l):
            out.append((i + 1, "L4", "a pcrec_scope_ result stored into a struct field (a scope object never escapes its scope)"))
        if handle_store and handle_store.search(l):
            out.append((i + 1, "L4", "a Scope handle copied into a struct field (a scope object never escapes its scope)"))
        if rel.startswith("src/parse/") and SCOPE_CALL.search(l) and \
                not any(a[0] == rel and a[1] == fn for a in SCOPE_PARSE_ALLOW):
            out.append((i + 1, "L4", "a pcrec_scope_ call under src/parse/ outside SCOPE_PARSE_ALLOW"))
        chan = l + " " + clean[i + 1].strip() if CHAN_OPEN_EOL.search(l) and i + 1 < len(clean) else l
        if rel in ("src/core/arena.c", "src/core/sb.c") and CHAN_CALL.search(chan):
            out.append((i + 1, "D-7", "a refusal through a .cx channel that does not read pcrec_err_chan("))
        if rel == "src/core/arena.c" and ARENA_ALLOC_CALL.search(l) and fn and fn != "pcrec_arena_alloc":
            out.append((i + 1, "D-7", "an arena.c function calls pcrec_arena_alloc (it would bypass the test link's wrap)"))
        if OPEN_P_CALL.search(l) and fn and fn != "pcrec_arena_open_p":
            out.append((i + 1, "readers", "pcrec_arena_open_p is W7's read-only accessor: no caller under src/, cli/ or lib/"))
    for fn, ln in opens.items():
        if fn not in closes:
            out.append((ln, "L2-static", f"pcrec_scope_open in {fn or '<file scope>'} with no pcrec_scope_close in the same function"))
    out += d11_findings(rel, clean, fnames)[0]
    return out

# fixtures: (rel, text) that MUST produce the named rule, and one that must not
SCOPE_MUST_FAIL = [
    ("src/opt/x.c", "void f(Ctx *cx)\n{\n    Scope s = pcrec_scope_open(&cx->arena);\n}\n", "L2-static"),
    ("src/opt/x.c", "void f(Ctx *cx)\n{\n    Scope s = pcrec_scope_open(&cx->arena);\n    cx->job->t = pcrec_scope_malloc(&s, 8);\n    pcrec_scope_close(&s);\n}\n", "L4"),
    ("src/opt/x.c", "void f(Ctx *cx, Job *j)\n{\n    Scope s = pcrec_scope_open(&cx->arena);\n    j->sb[2] = pcrec_scope_sb(&s);\n    pcrec_scope_close(&s);\n}\n", "L4"),
    ("src/opt/x.c", "void f(Ctx *cx)\n{\n    Scope s = pcrec_scope_open(&cx->arena);\n    cx->job->t = (char *)pcrec_scope_malloc(&s, 8);\n    pcrec_scope_close(&s);\n}\n", "L4"),
    ("src/opt/x.c", "void f(Ctx *cx, Job *j)\n{\n    Scope s = pcrec_scope_open(&cx->arena);\n    j->keep = s;\n    pcrec_scope_close(&s);\n}\n", "L4"),
    ("src/core/sb.c", "void h(StrBuf *sb)\n{\n    if (sb->cx) pcrec_ctx_nomem(\n        sb->cx);\n}\n", "D-7"),
    ("src/parse/x.c", "void g(Ctx *cx)\n{\n    Scope s = pcrec_scope_open(&cx->arena);\n    pcrec_scope_close(&s);\n}\n", "L4"),
    ("src/core/sb.c", "void h(StrBuf *sb)\n{\n    if (sb->cx) pcrec_ctx_nomem(sb->cx);\n}\n", "D-7"),
    ("src/core/arena.c", "void k(Arena *a)\n{\n    (void)pcrec_arena_alloc(a, 8);\n}\n", "D-7"),
    ("src/gen/x.c", "void m(Arena *a)\n{\n    if (pcrec_arena_open_p(a)) return;\n}\n", "readers"),
]
SCOPE_MUST_FAIL += [
    # L4's one src/parse/ row admits uprops_produce only: another function of the same file must still FAIL
    ("src/parse/mod_uprops.c", "void other(Ctx *cx)\n{\n    Scope s = pcrec_scope_open(&cx->arena);\n    pcrec_scope_close(&s);\n}\n", "L4"),
    # D-11, both spellings (an assignment binder, an initializer binder) and a foreign mf_art_begin caller
    ("src/gen/x.c", "void b(Ctx *cx)\n{\n    mf_arena *ma = pcrec_arena_alloc(&cx->arena, 8);\n    ma->u = &other;\n}\n", "D-11"),
    ("src/gen/x.c", "void b(Ctx *cx)\n{\n    mf_arena ar = { &fa, fh_alloc };\n    (void)ar;\n}\n", "D-11"),
    ("src/gen/memfn_sites.c", "mf_arena *pcrec_memfn_art(Ctx *cx)\n{\n    mf_arena *ma = pcrec_arena_alloc(&cx->arena, 8);\n    ma->u = &sc_child;\n}\n", "D-11"),
    ("src/gen/x.c", "void b(Ctx *cx)\n{\n    job->mf = mf_art_begin(ma, p);\n}\n", "D-11"),
    # r105 CHECKS-1: the file/function half of D-11, each fixture CORRECT on the value (`&cx->arena`) and wrong on one place
    ("src/gen/x.c", "mf_arena *pcrec_memfn_art(Ctx *cx)\n{\n    mf_arena *ma = pcrec_arena_alloc(&cx->arena, 8);\n    ma->u = &cx->arena;\n}\n", "D-11"),
    ("src/gen/memfn_sites.c", "mf_arena *other(Ctx *cx)\n{\n    mf_arena *ma = pcrec_arena_alloc(&cx->arena, 8);\n    ma->u = &cx->arena;\n}\n", "D-11"),
    ("src/gen/x.c", "mf_arena *pcrec_memfn_art(Ctx *cx)\n{\n    return mf_art_begin(ma, p);\n}\n", "D-11"),
    ("src/gen/memfn_sites.c", "mf_arena *other(Ctx *cx)\n{\n    return mf_art_begin(ma, p);\n}\n", "D-11"),
    # r105 CHECKS-2: L4's allow row is (file AND function): the allowed function NAME in another src/parse file must FAIL
    ("src/parse/other.c", "void uprops_produce(Ctx *cx)\n{\n    Scope s = pcrec_scope_open(&cx->arena);\n    pcrec_scope_close(&s);\n}\n", "L4"),
    # r105 CHECKS-2: a parse function that only USES a passed scope (no open) is still a scope call
    ("src/parse/x.c", "void g(Scope *s)\n{\n    pcrec_scope_malloc(s, 8);\n}\n", "L4"),
]
SCOPE_MUST_PASS = [
    ("src/parse/mod_uprops.c", "void uprops_produce(Ctx *cx)\n{\n    Scope s = pcrec_scope_open(&cx->arena);\n    Arena *t = pcrec_scope_arena(&s);\n    (void)t;\n    pcrec_scope_close(&s);\n}\n"),
    ("src/gen/memfn_sites.c", "mf_arena *pcrec_memfn_art(Ctx *cx)\n{\n    mf_arena *ma = pcrec_arena_alloc(&cx->arena, 8);\n    ma->u = &cx->arena;\n    job->mf = mf_art_begin(ma, p);\n}\n"),
    ("src/core/sb.c", "void h(StrBuf *sb)\n{\n    if (sb->cx) pcrec_ctx_nomem( pcrec_err_chan(sb->cx));\n}\n"),
    ("src/core/sb.c", "void h(StrBuf *sb)\n{\n    if (sb->cx) pcrec_ctx_fail(\n        pcrec_err_chan(sb->cx), 0, \"x\");\n}\n"),
    ("src/opt/x.c", "void f(Ctx *cx)\n{\n    Scope s = pcrec_scope_open(&cx->arena);\n    int *t = pcrec_scope_malloc(&s, 8);\n    pcrec_scope_free(&s, t);\n    pcrec_scope_close(&s);\n}\n"),
    ("src/core/sb.c", "void h(StrBuf *sb)\n{\n    if (sb->cx) pcrec_ctx_nomem(pcrec_err_chan(sb->cx));\n}\n"),
]

def scope_self_test():
    """-> a message per scope-rule fixture the rules got wrong."""
    out = []
    for rel, text, rule in SCOPE_MUST_FAIL:
        clean = strip_noise(text).split("\n")
        if not any(r == rule for _, r, _ in scope_rule_findings(rel, clean, functions(clean))):
            out.append(f"the {rule} rule missed its fixture in {rel}")
    # floor plants (r105 CHECKS-1/2): one site seen is below the floor; an empty D-11 population trips its floor
    if not scope_floor_failures(1, D11_MIN_SEEN):
        out.append("the scope-open floor did not trip on a single site (floor is half of 3)")
    if not scope_floor_failures(MIN_SCOPE_OPENS, 0):
        out.append("the D-11 binder floor did not trip on an empty population")
    for rel, text in SCOPE_MUST_PASS:
        clean = strip_noise(text).split("\n")
        got = scope_rule_findings(rel, clean, functions(clean))
        if got:
            out.append(f"a clean fixture in {rel} was flagged: {got[0][2]}")
    return out

def scope_scan(root):
    """-> (findings, files scanned, pcrec_scope_open sites) over src/ cli/ lib/ .c files."""
    findings, nfiles, nopen = [], 0, 0
    global D11_SEEN
    D11_SEEN = 0
    for top in ("src", "cli", "lib"):
        for dp, dn, fn in os.walk(os.path.join(root, top)):
            for f in sorted(fn):
                if not f.endswith(".c"):
                    continue
                path = os.path.join(dp, f)
                rel = os.path.relpath(path, root)
                clean = strip_noise(open(path, encoding="utf-8", errors="replace").read()).split("\n")
                nfiles += 1
                fns = functions(clean)
                nopen += sum(len(re.findall(r"\bpcrec_scope_open\s*\(", l)) for k, l in enumerate(clean)
                             if fns[k] and rel != "src/core/arena.c")
                D11_SEEN += d11_findings(rel, clean, fns)[1]
                for ln, rule, msg in scope_rule_findings(rel, clean, functions(clean)):
                    findings.append((rel, ln, rule, msg))
    return findings, nfiles, nopen

# D110 floor: half of the 3 scope-opening sites at the F2/F6 subject (round up):
#   grep -rn --include=*.c 'pcrec_scope_open *(' src cli lib | grep -v '^src/core/arena.c'
# -> minimize.c:84, mod_uprops.c:295, clskit.c:1130 (arena.c's unwind builds no open)
MIN_SCOPE_OPENS = 2
D11_MIN_SEEN = 1      # the one allowed binder, pcrec_memfn_art's `ma->u = &cx->arena`

def scope_floor_failures(nopen, nseen):
    """-> one message per scope-scan population below its floor (K35); plants in scope_self_test."""
    out = []
    if nopen < MIN_SCOPE_OPENS:
        out.append(f"saw only {nopen} pcrec_scope_open sites (floor {MIN_SCOPE_OPENS}): the scope scan is not reaching the tree")
    if nseen < D11_MIN_SEEN:
        out.append("saw no allowed mf_arena binder (pcrec_memfn_art's `ma->u = &cx->arena`): the D-11 rule is not reaching its site")
    return out

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    for l, want in MUST_FLAG:
        shape, _, name = want.partition(":")
        if not any(k == shape and (not name or n == name) for k, n in classify(strip_noise(l))):
            print(f"FAIL: self-test: detector missed a {want} builder: {l}")
            return 2
    for l in MUST_PASS:
        if classify(strip_noise(l)):
            print(f"FAIL: self-test: detector flagged a clean line: {l}")
            return 2
    findings, reached, nfiles, nscratch = scan(root, ALLOW + [SENTINEL])
    for m in self_test_controls(reached, len(ALLOW)):
        print(f"FAIL: self-test: {m}")
        return 2
    srcdir = os.path.join(root, "src")
    census = layer_census({d for d in os.listdir(srcdir) if os.path.isdir(os.path.join(srcdir, d))})
    rc = 0
    for m in census:
        print(f"FAIL: layer census: {m}")
        rc = 1
    for rel, ln, fn, shape, text in findings:
        print(f"FAIL: a {shape} builder on the compile path outside the allowlist: {rel}:{ln} in {fn}: {text}\n"
              f"      (a builder live across a refusal is stranded by its longjmp: use pcrec_sb_scratch(&cx->arena) "
              f"or a Job-owned field job_cleanup frees; "
              f"an ALLOW row needs the reason it can never be live across a refusal)")
        rc = 1
    for k in stale_rows(ALLOW, reached):
        a = ALLOW[k]
        print(f"FAIL: stale allowlist row (nothing matches it any more): {a[0]} {a[1]} {a[2]} -- remove it")
        rc = 1
    for m in scope_self_test():
        print(f"FAIL: self-test: {m}")
        return 2
    sfind, _, nopen = scope_scan(root)
    for rel, ln, rule, msg in sfind:
        print(f"FAIL: scope rule {rule}: {rel}:{ln}: {msg}")
        rc = 1
    for m in scope_floor_failures(nopen, D11_SEEN):
        print(f"FAIL: {m}")
        return 2
    fields, freed = job_fields(root)
    if fields is None or freed is None:
        print("FAIL: could not find struct Job in src/core/internal.h or job_cleanup in src/core/compile.c")
        return 2
    for f in sorted(fields - freed):
        print(f"FAIL: Job's StrBuf field `{f}` is not freed in job_cleanup (src/core/compile.c): a Job-owned builder must be")
        rc = 1
    floors = floor_failures(nfiles, nscratch, len(fields))
    for m in floors:
        print(f"FAIL: {m}")
    if floors:
        return 2
    if rc == 0:
        print(f"PASS: scratch_builder_check: {nfiles} compile-path files, {nscratch} scratch builders, "
              f"{len(reached)} allowlisted sites, {len(fields)} Job buffers all freed by job_cleanup, 0 heap builders, "
              f"{nopen} scope sites under the scope rules")
    return rc

sys.exit(main())
