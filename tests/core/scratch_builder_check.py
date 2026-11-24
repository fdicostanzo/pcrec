#!/usr/bin/env python3
"""[K155] no heap builder lives across a refusal: the compile path's builder census as a gate.

THE RULE (src/core/CLAUDE.md): a builder that can be interrupted by
`pcrec_ctx_fail`/`pcrec_ctx_nomem` is arena-backed, because a refusal
longjmps to compile_driver's one setjmp and only the compile's arena and the
Job's own buffers are freed there (job_cleanup). A heap builder live at that
moment is stranded (K155: 32 KB per refused compile in target_headers_render).

WHAT THIS SCANS. Every .c file in the COMPILE-PATH layers (src/core, src/enc,
src/parse, src/ir, src/facts, src/opt, src/gen; src/dump renders after the
pipeline, outside any compile), comments and literals blanked, for three
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

WHAT IT DOES NOT SEE (said, not implied): a heap block reached through
another function's return value (a callee's malloc'd result, e.g. a part
compile's `pcrec_output`), and whether an allowlisted heap call is in fact
freed before every refusal. The INDEPENDENT control for both is dynamic and
shares nothing with this scan: tests/core/alloc_check.c fails every
allocation of its witnesses in turn and fails a refusal that leaves the
injected tree's live heap above zero (`make test-alloc`).

CONTROLS (learnings.md section 3): self-test fixtures (lines that MUST be
flagged and MUST NOT be) run through the same detector first; every
allowlist row must be REACHED (a row that stops matching is stale and
FAILS); population floors on the files scanned and the scratch builders
seen make a scan that silently saw nothing a failure (K35).

Usage: scratch_builder_check.py ROOT   (exit 0 clean, 1 findings, 2 setup error)
"""
import os
import re
import sys

LAYERS = ("core", "enc", "parse", "ir", "facts", "opt", "gen")
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
    ("src/core/compile.c", "compile_driver", "heap", "the Job itself, freed by job_cleanup"),
    # -- heap arrays the Job owns from birth (job_cleanup frees them) ----
    ("src/ir/nfa.c", "nst", "heap", "the Job's NFA state array, realloc'd in place"),
    ("src/ir/dfa.c", "tab_grow", "heap", "the Job DFA's intern table (old one freed and NULLed first)"),
    ("src/ir/dfa.c", "intern", "heap", "the Job DFA's state array, realloc'd in place"),
    ("src/opt/dfamemo.c", "pcrec_build_min_dfa", "heap", "the restored machine's state array, attached to the Job's Dfa before any further allocation (dfa_copy)"),
    # -- hand-freed temporaries never live across a refusal --------------
    ("src/opt/scanedge.c", "pcrec_scanedge_dfa", "heap", "ten temporaries freed on every exit; the only refusals while live are their own allocation failures, which free them first (coding.md 1.6)"),
    ("src/opt/minimize.c", "pcrec_minimize_dfa", "heap", "FILED [MINIMIZE-ARENA-LEAK]: its tables are live across arena allocations (OOM only); alloc_check.c's known_stranded row"),
    # -- outside a compile: no Ctx, so no longjmp can strand anything ------
    ("src/core/compile.c", "pcrec_subst_compile", "arena", "the subst compile: a detached arena, freed on return, no Ctx"),
    ("src/gen/emit_subst.c", "support_unit", "strbuf", "the subst support unit: no Ctx"),
    ("src/gen/emit_subst.c", "pcrec_emit_subst", "strbuf", "the subst emitter: no Ctx"),
    ("src/gen/emit_subst.c", "pcrec_emit_subst", "arena", "the subst emitter: a detached arena, no Ctx"),
    ("src/gen/clskit.c", "pcrec_clskit_emit_kit", "arena:own", "the no-Ctx fallback only; a compile's text uses the compile's arena"),
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

STRBUF = re.compile(r"(?<![\w*])StrBuf\s+(?!\*)(\w+)\s*(\[[^\]]*\])?\s*(=\s*(.*?))?[;,]")
ARENA = re.compile(r"(?<![\w*])Arena\s+(?!\*)(\w+)\s*(=|;)")
HEAP = re.compile(r"(?<![\w.>])(malloc|calloc|realloc|strdup|strndup|realpath)\s*\(")
SCRATCH = re.compile(r"\bpcrec_sb_scratch\s*\(")

def classify(line):
    """-> list of (shape, object name or '') a (noise-stripped) line holds."""
    shapes = []
    for m in STRBUF.finditer(line):
        if not (m.group(4) or "").lstrip().startswith("pcrec_sb_scratch("):
            shapes.append(("strbuf", m.group(1)))
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
    ("StrBuf u = { 0 }, all = { 0 };", "strbuf"),
    ("Arena a = { NULL, c->cx };", "arena"),
    ("char *np = realloc(sb->p, cap);", "heap"),
    ("int *t = malloc(n * sizeof *t);", "heap"),
    ("char *s = strdup(x);", "heap"),
]
MUST_PASS = [
    "StrBuf nb = pcrec_sb_scratch(&cx->arena);",
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

def scan(root):
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
                        row = next((k for k, a in enumerate(ALLOW)
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

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    for l, shape in MUST_FLAG:
        if shape not in [k for k, _ in classify(strip_noise(l))]:
            print(f"FAIL: self-test: detector missed a {shape} builder: {l}")
            return 2
    for l in MUST_PASS:
        if classify(strip_noise(l)):
            print(f"FAIL: self-test: detector flagged a clean line: {l}")
            return 2
    findings, reached, nfiles, nscratch = scan(root)
    rc = 0
    for rel, ln, fn, shape, text in findings:
        print(f"FAIL: a {shape} builder on the compile path outside the allowlist: {rel}:{ln} in {fn}: {text}\n"
              f"      (a builder live across a refusal is stranded by its longjmp: use pcrec_sb_scratch(&cx->arena), "
              f"the Job's rewrite buffer for a whole-buffer rewrite, or a Job-owned field job_cleanup frees; "
              f"an ALLOW row needs the reason it can never be live across a refusal)")
        rc = 1
    for k, a in enumerate(ALLOW):
        if k not in reached:
            print(f"FAIL: stale allowlist row (nothing matches it any more): {a[0]} {a[1]} {a[2]} -- remove it")
            rc = 1
    fields, freed = job_fields(root)
    if fields is None or freed is None:
        print("FAIL: could not find struct Job in src/core/internal.h or job_cleanup in src/core/compile.c")
        return 2
    if len(fields) < 6:
        print(f"FAIL: found only {len(fields)} StrBuf fields of Job (floor 6): the parse is not reaching the struct")
        return 2
    for f in sorted(fields - freed):
        print(f"FAIL: Job's StrBuf field `{f}` is not freed in job_cleanup (src/core/compile.c): a Job-owned builder must be")
        rc = 1
    if nfiles < MIN_FILES:
        print(f"FAIL: scanned only {nfiles} compile-path .c files (floor {MIN_FILES})")
        return 2
    if nscratch < MIN_SCRATCH:
        print(f"FAIL: saw only {nscratch} pcrec_sb_scratch builders (floor {MIN_SCRATCH}): the scan is not reaching the tree")
        return 2
    if rc == 0:
        print(f"PASS: scratch_builder_check: {nfiles} compile-path files, {nscratch} scratch builders, "
              f"{len(reached)} allowlisted sites, {len(fields)} Job buffers all freed by job_cleanup, 0 heap builders")
    return rc

sys.exit(main())
