#!/usr/bin/env python3
"""[OPT-REVEND] hand-twin generator (STUDY, not a build path).

    mktwin.py IN.c OUT.c PREFIX EOL

Takes an UNMODIFIED pcrec artifact (a DFA artifact, `RX_DFA_SCAN
"unanchored"`, `RX_DFA_START "reverse-pass"`, emitted with `-p PREFIX`) and
writes its twin: the artifact's OWN reverse block (copied verbatim, not
re-written) is run from the subject end -- seeded at `n`, and at `n-1` when
EOL is 1 and `s[n-1] == '\\n'` -- and the smallest accepting position `s*`
over the seeds is the leftmost-first START. Three forms (TWIN_FORM):

  exact  (form A) the forward pass is deleted; the end comes from the
         artifact's OWN anchored entry `<PREFIX>_match`, run once at `s*`.
  lower  (form B) `s*` becomes the unchanged body's search_from; the forward
         and reverse passes then run over [s*, n).
  walk   (form C, revision 2's primary design) NO forward pass at all: the
         walk records WHICH seed(s) reach `s*`. Exactly one seed => that seed
         is the end. Both seeds => leftmost-first priority decides n vs n-1,
         resolved by one anchored forward run (`<PREFIX>_match`) from `s*`.

Revision 2 (lane revrev) changes, applied to every form:
  - the walk sits at the HEAD of the search (panel X7): any PRESENCE
    pre-check (`<p>_reqrun(...)`, a REQ handoff) is DELETED under forms A/C
    (nothing runs after the walk for it to filter) and MOVED after the walk
    under form B (it then scans [s*, n));
  - a seed whose reverse start state is DEAD is skipped before the first
    view lookup (panel X1: `view[row(dead)]` is an out-of-bounds read).

EOL is 1 for a `$`/`\\Z` pattern (the end_window fact's eps), 0 for `\\z`.

Every marker is asserted: an artifact whose text does not have the shape
this script was written against is refused, never half-transformed.

CONTROLS (TWIN_SABOTAGE; the sweep must be able to fail):
  noeol      drops the n-1 seed;
  firstseed  keeps the first seed that accepts instead of the minimum;
  nodead     drops the X1 dead-seed check (run under ASan: an OOB read);
  tien       form C: a tie takes end n without the anchored run;
  tien1      form C: a tie takes end n-1 without the anchored run.
"""
import os, re, sys

src, dst, p, eol = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
sab = os.environ.get("TWIN_SABOTAGE", "")
if sab == "noeol": eol = 0
form = os.environ.get("TWIN_FORM", "exact")
t = open(src).read()

def need(cond, what):
    if not cond:
        sys.exit(f"mktwin: {src}: {what}")

need(form in ("exact", "lower", "walk"), f"unknown TWIN_FORM {form}")
need(sab in ("", "noeol", "firstseed", "nodead", "tien", "tien1"), f"unknown TWIN_SABOTAGE {sab}")
need(sab not in ("tien", "tien1") or form == "walk", "tie controls are form C only")
for stamp, val in (("DFA_SCAN", "unanchored"), ("DFA_START", "reverse-pass")):
    need(f'#define {p.upper()}_{stamp} "{val}"' in t, f"not a {stamp}={val} artifact")

# the search function's body
m = re.search(r"^int %s_search\(.*?^\}\n" % re.escape(p), t, re.S | re.M)
need(m, "no <p>_search definition")
body = m.group(0)

# (0) the head of the body: every line between the opening brace and the
#     first table declaration. It holds (a) the K50 startpos guard under utf8
#     (an ENTRY guard: it stays first in every form), (b) a REQ handoff, and
#     (c) PRESENCE pre-checks (`if (<p>_reqrun(...) >= subject_length)
#     return 0;`, or a necessary-byte `memchr`), each `if (...) return 0;`.
open_txt = body[:body.index("{\n") + 2]
first_decl = body.find("    static const ")
need(first_decl > 0, "no table declarations")
head = body[len(open_txt):first_decl]
# (a) is kept at the head, (b)/(c) are separated out below.
# (1) the forward pass: from its first declaration to its no-match return.
#     An artifact with a REQ handoff starts its scan at the handoff position.
ho_txt = ("    size_t handoff_position = %s_reqrun(subject, subject_length, search_from);\n"
          "    if (handoff_position >= subject_length) return 0;\n") % p
handoff = ho_txt in body
if handoff:
    ho_adj = re.search(r"    if \(handoff_position - search_from > \d+\) \{\n        handoff_position -= \d+;\n    \} else\n        handoff_position = search_from;\n", body)
    if ho_adj and body.find(ho_txt) + len(ho_txt) == ho_adj.start():
        ho_txt += ho_adj.group(0)
head_rest = head.replace(ho_txt, "", 1) if handoff else head
pre_re = re.compile(r"    if \((?:[^;])*?\)\s*return 0;\n")
head_pre = "".join(pre_re.findall(head_rest))
keep_head = pre_re.sub("", head_rest)
# what stays is the ENTRY guard (K50's refusal, K75's alignment): comments
# and statements that read only search_from/subject_length/the subject
for l in keep_head.splitlines():
    need(l.lstrip().startswith(("/*", "*")) or "search_from" in l,
         f"unrecognised head line: {l!r}")
fwd_a = body.find("    size_t scan_position = %s;\n" % ("handoff_position" if handoff else "search_from"))
fwd_z_txt = "    if (last_accept_position == (size_t)-1) return 0;\n"
fwd_z = body.find(fwd_z_txt)
need(fwd_a >= 0 and fwd_z > fwd_a, "forward-pass markers")
need(body.count(fwd_z_txt) == 1, "forward no-match return not unique")
need("if (search_from > subject_length) return 0;\n" in body[fwd_a:fwd_z],
     "forward pass lost its search_from guard")

# (2) the reverse block, verbatim: from its start declaration to the
#     no-match return that follows it
rev_head = ("    {\n        size_t match_end_position = last_accept_position;\n")
need(body[fwd_z + len(fwd_z_txt):].startswith(rev_head), "reverse block head")
r_a = fwd_z + len(fwd_z_txt) + len(rev_head)
r_z_txt = "        if (match_start_position == (size_t)-1) return 0;\n"
r_z = body.find(r_z_txt, r_a)
need(r_z > r_a, "reverse block tail")
rev = body[r_a:r_z]
need(rev.startswith("        size_t match_start_position = (size_t)-1;\n"),
     "reverse block does not open with its start variable")
need("size_t rewind_position = match_end_position;" in rev, "reverse seed line")
need("return" not in rev, "the reverse block returns from inside (the seed loop would be bypassed)")
tail = body[r_z + len(r_z_txt):]
need(tail.startswith("        if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)match_start_position; capture_spans[0][1] = (ptrdiff_t)match_end_position; }\n        return 1;\n    }\n}\n"),
     "unexpected success tail (captures beyond group 0?)")

# X1: the seed state may be DEAD (a trailing lookaround's seed table, or a
# constant seed under a view that cannot hold); skip the seed before the
# first view lookup reads view[row(dead)].
sd = re.search(r"^        %s_reverse_state reverse_state = [^\n]*;\n" % re.escape(p), rev, re.M)
need(sd, "reverse seed-state declaration")
need("%s_reverse_is_dead(" % p in t, "no <p>_reverse_is_dead helper")
dead_chk = "        if (%s_reverse_is_dead(reverse_state)) continue;   /* [r2 X1] dead seed */\n" % p
if sab != "nodead":
    rev = rev[:sd.end()] + dead_chk + rev[sd.end():]

# the reverse block, indented one level deeper inside the seed loop
rev_in = "".join("    " + l if l.strip() else l for l in rev.splitlines(True))
# the walk is a COPY of the block; form B keeps the original too, so the
# copy's label is renamed (the emitted label is `<p>_reverse_scan_views`)
rev_in = rev_in.replace("%s_reverse_scan_views" % p, "%s_revend_scan_views" % p)

nseed = 1 + eol
seed_open = (
    "    if (search_from > subject_length) return 0;\n"
    "    /* [OPT-REVEND] HAND-TWIN: the artifact's own reverse block runs from\n"
    "     * each possible match END (n; n-1 under $/\\Z when the last byte is\n"
    "     * the newline); the smallest accepting position over the seeds is the\n"
    "     * leftmost-first START. */\n"
    "    size_t revend_start = (size_t)-1, revend_end = 0;\n"
    "    int revend_tie = 0;\n"
    "    for (int revend_seed = 0; revend_seed < %d; revend_seed++) {\n"
    "        size_t match_end_position = subject_length;\n"
    "        if (revend_seed == 1) {\n"
    "            if (subject_length == 0 || subject[subject_length - 1] != '\\n') break;\n"
    "            match_end_position = subject_length - 1;\n"
    "        }\n"
    "        if (match_end_position < search_from) break;\n") % nseed
if sab == "firstseed":
    seed_take = ("            if (match_start_position != (size_t)-1 && revend_start == (size_t)-1) {\n"
                 "                revend_start = match_start_position; revend_end = match_end_position;\n"
                 "            }\n")
else:
    seed_take = ("            if (match_start_position == (size_t)-1) continue;\n"
                 "            if (match_start_position < revend_start) {\n"
                 "                revend_start = match_start_position; revend_end = match_end_position; revend_tie = 0;\n"
                 "            } else if (match_start_position == revend_start) revend_tie = 1;\n")
walk = seed_open + rev_in + seed_take + "    }\n" + "    (void)revend_end; (void)revend_tie;\n"

def anchored_end(var):
    return ("        rx_ctx revend_ctx = { subject, subject_length, revend_start, 0, NULL, NULL, NULL, 0 };\n"
            "        ptrdiff_t revend_len = %s_match(&revend_ctx);\n"
            "        if (revend_len < 0) return PCREC_ERR_INTERNAL;   /* the proof says unreachable */\n"
            "        %s = revend_start + (size_t)revend_len;\n") % (p, var)

hit = ("    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)revend_start; capture_spans[0][1] = (ptrdiff_t)revend_end; }\n"
       "    return 1;\n"
       "}\n")

pre = body[first_decl:fwd_a]   # the tables (head guard/pre-checks handled apart)
need(ho_txt not in pre and "return 0;" not in pre.replace("if (search_from > subject_length) return 0;", ""),
     "a pre-check between the tables and the forward pass")
pre = keep_head + pre
mm = re.search(r"^ptrdiff_t %s_match\(const rx_ctx \*ctx\)\n\{.*?^\}\n" % p, t, re.S | re.M)
need(mm, "no <p>_match definition")
anchored = "%s_search(" % p not in mm.group(0)   # False: `search-filter`, _match wraps _search
ho = ho_txt if handoff else ""
if form == "exact":
    need(anchored, "<p>_match calls <p>_search (form A needs its own anchored machine)")
    # FORM A: the anchored entry gives the end at s*, every call
    body2 = (open_txt + pre + walk +
             "    if (revend_start == (size_t)-1) return 0;\n"
             "    {\n" + anchored_end("revend_end") + "    }\n" + hit)
elif form == "walk":
    # FORM C: the walk's own seed record gives the end; a tie (both seeds
    # reach s*) is decided by one anchored run from s*
    if sab == "tien":
        tie = "    if (revend_tie) revend_end = subject_length;   /* CONTROL tien */\n"
    elif sab == "tien1":
        tie = "    if (revend_tie) revend_end = subject_length - 1;   /* CONTROL tien1 */\n"
    elif eol == 0:
        tie = ""   # one seed: no tie is possible, no tie arm is emitted
    elif anchored:
        tie = "    if (revend_tie) {\n" + anchored_end("revend_end") + "    }\n"
    else:
        tie = None   # no anchored machine: a tie hands s* to the body (form B's arm)
    if tie is not None:
        body2 = (open_txt + pre + walk +
                 "    if (revend_start == (size_t)-1) return 0;\n" + tie + hit)
    else:
        body2 = (open_txt + pre + walk +
                 "    if (revend_start == (size_t)-1) return 0;\n"
                 "    if (!revend_tie) {\n"
                 "        if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)revend_start; capture_spans[0][1] = (ptrdiff_t)revend_end; }\n"
                 "        return 1;\n"
                 "    }\n"
                 "    search_from = revend_start;   /* tie, no anchored machine: the body decides the end */\n" +
                 head_pre + ho + body[fwd_a:])
else:
    # FORM B: the walk's s* is handed to the UNCHANGED body as its lower
    # bound; the PRESENCE pre-check (and a REQ handoff) MOVES to after the
    # walk (design 4.1: it scans [s*, n), never [search_from, n)).
    body2 = (open_txt + pre + walk +
             "    if (revend_start == (size_t)-1) return 0;\n"
             "    search_from = revend_start;\n" + head_pre + ho + body[fwd_a:])


out = t[:m.start()] + body2 + t[m.end():]
# a prototype for the anchored entry ahead of the search's attribute block
proto = "ptrdiff_t %s_match(const rx_ctx *ctx);\n" % p
k = out.find("#ifndef __has_attribute\n")
need(0 <= k < out.find("int %s_search(" % p), "no attribute block ahead of _search")
out = out[:k] + proto + out[k:]
open(dst, "w").write(out)
