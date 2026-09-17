#!/usr/bin/env python3
"""lens10kit: THE MEASUREMENT lens 2 §2.4 step 4 named and did not build.

Counts runs of >= N consecutive sb_puts/sb_printf/sb_putc calls emitting a
CONTIGUOUS literal block with ONLY THE PREFIX VARYING -- i.e. exactly the
population that pcrec_enc_emit_text ($-template) could replace.

Method, stated so its blind spots are checkable:
  1. Lex the file with string/char-literal and comment awareness.
  2. Find every `sb_puts(`/`sb_printf(`/`sb_putc(` call; take its argument
     list to the matching close paren, then require a `;` (so a call used as
     an expression inside something else is NOT counted as a statement).
  3. CONTIGUITY: two calls are adjacent iff the text between the `;` of one
     and the start of the next is whitespace and/or comments ONLY. Any other
     token (an `if`, a loop, an assignment, a `}`) breaks the run.
  4. CLASSIFY each call:
       LIT       - sb_puts(sb, "..."), sb_putc(sb, 'c'): no varying data.
       PFX       - sb_printf(sb, "...", <prefix>...) where every conversion
                   in the format is %s and every vararg is a prefix
                   expression from PREFIX_EXPRS.
       OTHER     - anything else (varying data a $-template cannot carry).
  5. A TEMPLATE-CONVERTIBLE RUN is a maximal adjacency run of LIT|PFX calls.
     Report the run-length distribution and the >= N population.

Also reports, separately, PURE-LITERAL runs (LIT only) -- those need no
template at all, just concatenation into one sb_puts -- because they are a
different (cheaper) remedy for part of the same population.
"""
import re, sys, json, collections

CALLS = ("sb_printf", "sb_puts", "sb_putc")

# Prefix expressions, derived by inspection of the two emitters (reported and
# validated by --dump-args; see the report's blind-spot list).
PREFIX_EXPRS = {
    "p", "v->p", "v.p", "f->p", "prefix", "cx->opt->prefix", "e->p", "pfx",
}


def strip_map(src):
    """Return (kinds, ) a per-char classification: 'c'=code, 's'=string/char
    literal body, '/'=comment. Keeps indices aligned with src."""
    n = len(src)
    kind = ["c"] * n
    i = 0
    while i < n:
        ch = src[i]
        if ch == '/' and i + 1 < n and src[i+1] == '/':
            j = src.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                kind[k] = "/"
            i = j
        elif ch == '/' and i + 1 < n and src[i+1] == '*':
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                kind[k] = "/"
            i = j
        elif ch == '"' or ch == "'":
            q = ch
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == q:
                    j += 1
                    break
                j += 1
            for k in range(i, j):
                kind[k] = "s"
            i = j
        else:
            i += 1
    return kind


def find_calls(src, kind):
    """Yield dicts for each sb_* CALL STATEMENT."""
    out = []
    for m in re.finditer(r"\b(sb_printf|sb_puts|sb_putc)\s*\(", src):
        s = m.start()
        if kind[s] != "c":
            continue                      # inside a comment or string
        # STATEMENT POSITION. The preceding non-space/comment code char must be
        # one of ; { } : ) or the keyword `else`/`do`. A call after the `)` of
        # an if/for/while, or after `else`/`do`, is CONDITIONALLY reached:
        # counted as a call, marked `guarded`, and never allowed to join or
        # head a run (a $-template block is one unconditional text blob).
        k = s - 1
        while k >= 0 and (src[k].isspace() or kind[k] == "/"):
            k -= 1
        if k < 0:
            guarded = False
        elif src[k] in ";{}:":
            guarded = False
        elif src[k] == ")":
            guarded = True          # if (...) / for (...) / while (...)
        elif re.search(r"\b(else|do)$", src[max(0, k - 8):k + 1]):
            guarded = True
        else:
            continue                # an expression use, not a statement
        # find matching close paren
        depth = 0
        i = m.end() - 1
        while i < len(src):
            if kind[i] == "c":
                if src[i] == "(":
                    depth += 1
                elif src[i] == ")":
                    depth -= 1
                    if depth == 0:
                        break
            i += 1
        if i >= len(src):
            continue
        close = i
        # require a ';' after (whitespace/comments only between)
        j = close + 1
        while j < len(src) and (src[j].isspace() or kind[j] == "/"):
            j += 1
        if j >= len(src) or src[j] != ";":
            continue
        out.append({
            "fn": m.group(1),
            "guarded": guarded,
            "start": s,
            "argstart": m.end(),
            "close": close,
            "end": j,               # index of the ';'
            "line": src.count("\n", 0, s) + 1,
            "args": src[m.end():close],
            "argkind": kind[m.end():close],
        })
    return out


def split_args(text, kind):
    """Top-level comma split, string/paren aware."""
    parts, depth, cur, curk = [], 0, [], []
    for ch, kk in zip(text, kind):
        if kk == "c":
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append(("".join(cur), "".join(curk)))
                cur, curk = [], []
                continue
        cur.append(ch)
        curk.append(kk)
    parts.append(("".join(cur), "".join(curk)))
    return parts


def is_string_literal(text, kind):
    """True iff the arg is only (concatenated) string literals + whitespace."""
    saw = False
    for ch, kk in zip(text, kind):
        if kk == "s":
            saw = True
            continue
        if kk == "/":
            continue
        if ch == '"':
            saw = True
            continue
        if ch.isspace():
            continue
        return False
    return saw


def is_char_literal(text, kind):
    t = text.strip()
    return len(t) >= 3 and t[0] == "'" and t[-1] == "'"


def literal_body(text, kind):
    """Concatenate the bodies of the string literals in the arg."""
    body, i, n = [], 0, len(text)
    while i < n:
        if text[i] == '"' and (i == 0 or kind[i] != "s" or True):
            # walk the literal
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    body.append(text[j:j+2]); j += 2; continue
                if text[j] == '"':
                    break
                body.append(text[j]); j += 1
            i = j + 1
            continue
        i += 1
    return "".join(body)


CONV = re.compile(r"%(?:%|[-+ #0]*[0-9*]*(?:\.[0-9*]+)?(?:hh|h|ll|l|z|j|t|L)?([a-zA-Z]))")


def conversions(fmt):
    """Return list of conversion letters (skipping %%)."""
    out = []
    i = 0
    while i < len(fmt):
        if fmt[i] != "%":
            i += 1
            continue
        m = CONV.match(fmt, i)
        if not m:
            out.append("?")
            i += 1
            continue
        if m.group(0) == "%%":
            i = m.end()
            continue
        out.append(m.group(1))
        i = m.end()
    return out


def classify(call, arg_hist):
    args = split_args(call["args"], call["argkind"])
    if len(args) < 2:
        return "OTHER", None
    a1t, a1k = args[1]
    if call["fn"] == "sb_putc":
        return ("LIT" if is_char_literal(a1t, a1k) else "OTHER"), None
    if call["fn"] == "sb_puts":
        return ("LIT" if is_string_literal(a1t, a1k) else "OTHER"), None
    # sb_printf
    if not is_string_literal(a1t, a1k):
        return "OTHER", None
    fmt = literal_body(a1t, a1k)
    convs = conversions(fmt)
    rest = [a.strip() for a, _ in args[2:]]
    for r in rest:
        arg_hist[r] += 1
    if not convs and not rest:
        return "LIT", None          # a printf with no conversions
    if any(cv != "s" for cv in convs):
        return "OTHER", None
    if len(convs) != len(rest):
        return "OTHER", None
    if all(r in PREFIX_EXPRS for r in rest):
        return "PFX", None
    return "OTHER", None


def analyse(path, minlen, arg_hist, examples):
    src = open(path, encoding="utf-8", errors="replace").read()
    kind = strip_map(src)
    calls = find_calls(src, kind)
    for c in calls:
        c["cls"], _ = classify(c, arg_hist)
        c["buf"] = split_args(c["args"], c["argkind"])[0][0].strip()
    # adjacency: only whitespace/comments between the previous CALL's ';' and
    # this call's start. `prev` is the previous call whatever its class, so a
    # broken run's trailing ';' still anchors the next run's first member.
    runs = []
    cur = []
    prev = None
    for c in calls:
        adj = False
        if prev is not None:
            between = src[prev["end"] + 1:c["start"]]
            bk = kind[prev["end"] + 1:c["start"]]
            adj = all(ch.isspace() or kk == "/" for ch, kk in zip(between, bk))
        eligible = c["cls"] in ("LIT", "PFX") and not c["guarded"]
        joins = eligible and cur and adj and c["buf"] == cur[-1]["buf"]
        if joins:
            cur.append(c)
        else:
            if cur:
                runs.append(cur)
            cur = [c] if eligible else []
        prev = c
    if cur:
        runs.append(cur)
    # pure-literal sub-runs (LIT only, adjacency already guaranteed inside run)
    lit_runs = []
    for r in runs:
        sub = []
        for c in r:
            if c["cls"] == "LIT":
                sub.append(c)
            else:
                if sub:
                    lit_runs.append(sub)
                sub = []
        if sub:
            lit_runs.append(sub)
    for r in runs:
        if len(r) >= minlen:
            examples.append((path, r[0]["line"], r[-1]["line"], len(r),
                             sum(1 for c in r if c["cls"] == "PFX")))
    return calls, runs, lit_runs


def main():
    minlen = 5
    paths = [a for a in sys.argv[1:] if not a.startswith("-")]
    dump_args = "--dump-args" in sys.argv
    arg_hist = collections.Counter()
    examples = []
    total = {}
    for path in paths:
        calls, runs, lit_runs = analyse(path, minlen, arg_hist, examples)
        dist = collections.Counter(len(r) for r in runs)
        ldist = collections.Counter(len(r) for r in lit_runs)
        total[path] = {
            "calls": len(calls),
            "cls": dict(collections.Counter(c["cls"] for c in calls)),
            "runs_total": len(runs),
            "runs_ge_min": sum(n for L, n in dist.items() if L >= minlen),
            "calls_in_runs_ge_min": sum(L * n for L, n in dist.items() if L >= minlen),
            "run_len_dist": dict(sorted(dist.items())),
            "litruns_ge_min": sum(n for L, n in ldist.items() if L >= minlen),
            "calls_in_litruns_ge_min": sum(L * n for L, n in ldist.items() if L >= minlen),
            "litrun_len_dist": dict(sorted(ldist.items())),
        }
    print(json.dumps(total, indent=2))
    print("\n=== runs >= %d (file, firstline, lastline, len, #PFX) ===" % minlen)
    for e in sorted(examples, key=lambda x: -x[3]):
        print("%-24s %5d-%-5d len=%-3d pfx=%d" % (e[0].split("/")[-1], e[1], e[2], e[3], e[4]))
    if dump_args:
        print("\n=== printf vararg expressions (top 40) ===")
        for k, v in arg_hist.most_common(40):
            print("%5d  %s" % (v, k))


if __name__ == "__main__":
    main()
