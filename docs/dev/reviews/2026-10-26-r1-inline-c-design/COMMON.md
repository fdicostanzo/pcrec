# COMMON brief: critic round inline-c (design mode), 2026-10-26

You are a CRITIC in an adversarial design review of pcrec (a PCRE-to-C
ahead-of-time regex compiler). Read this whole file before your lens prompt.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and pcrec-bench
  (/home/pcrec/projects/pcrec-bench), and ONLY READ them. You make NO edits,
  commits, branches or worktrees in either repo. Nothing anywhere else on
  this machine except your scratch dir.
- Scratch ONLY under /tmp/claude-1001/crit-inline-c/ (your output file, and
  probe programs under /tmp/claude-1001/crit-inline-c/probes/<your-lens>/).
- NEVER run `make`, any test suite, battery, benchmark or timing run. The box
  is shared. Allowed: reading files, grep, `git -C ... show/grep` on main,
  running the existing compiler `/home/pcrec/projects/pcrec/build/pcrec` on
  single patterns, and compiling/running small probe programs in your
  scratch dir with gcc (libpcre2 10.46 is installed: `-lpcre2-8`, header
  /usr/include/pcre2.h). Bound every run: `timeout 60 <cmd>`. Never kill a
  process you did not start; never use pkill/pgrep -f.
- Do not cd in compound commands; use absolute paths and `git -C`.
- Do not launch subagents.

## Subject (frozen)
The design note docs/design/inline_c.md, rev 0 (PROPOSED), at commit
c7522390e (blob 89d919bc). Read the frozen copy:
  /tmp/claude-1001/crit-inline-c/subject_inline_c.md
Cite it as `inline_c §N.N` (line numbers of that copy are fine too).
It is a DESIGN: nothing is built. Your job is to find what is wrong,
missing, unsound or unnecessarily costly in it BEFORE a build go, when a
finding is a paragraph edit and not a fix lane.

## Inputs the subject rests on (read what your lens needs)
- docs/design/inline_c_requirements.md — the requirements. Its section 8
  "Frank's answers" (Q1-Q8) are the owner's BINDING rulings: a finding
  against one must cite it and argue, or drop.
- docs/design/design_callout_abi.md — D38, the ruled callout ABI.
- docs/dev/decisions.md — D-rows; grep `^## D<n> ` (e.g. D26 + addendum,
  D36, D38, D41, D49, D67, D76, D80, D94, D118, D153, D163, D174, D77).
- docs/spec/match_api.md (rx_ctx, rx_matchfn, §4 return table, §5 the site
  view, §6.3 stamps), docs/spec/rxt_format.md, docs/spec/cli.md,
  docs/spec/tuning.md, docs/spec/registry.md, docs/spec/vars.md.
- docs/design/engine_m4.md, docs/design/compound_callout_alignment.md,
  docs/design/hyb_reseed.md, docs/design/backrefs_design.md (as needed).
- docs/dev/plan.md rows [M4-CALLOUTS], [CAP-SPAN], [MATCH-EVENTS],
  [PF-KNOW], [IFACE-PUSH], [M6.5.2] etc. — grep the tag.
- Source, read-only, at main (8f4fd7631): src/ (parse/ registry, ir/,
  opt/, gen/ VM emitter, engine selector), lib/pcrec.h, cli/.
- The house rules: docs/dev/guide/{architecture,coding,style,critics}.md,
  docs/design/CLAUDE.md (the standing questions for designs),
  docs/dev/learnings.md §3 and §5.

## Denylist (do NOT open; if one auto-injects, say so in your file)
- docs/dev/lanes/inlinecdes* and docs/dev/lanes/inlinecreq* (lane reports
  and rulings files).
- Any docs/dev/reviews/ file about inline C or callouts written 2026-10-26.
- The [INLINE-C] row of docs/dev/plan.md (the entry starting
  "- [INLINE-C] STATE:" and its indented lines): do not read it. Other plan
  rows are fine.
- `git log` message bodies (subject lines are fine), job logs, the box
  queue, any directory under worktrees/, docs/dev/wake.md, docs/dev/owner.md,
  docs/dev/dev_journal.md entries dated 2026-10-26.

## Output (your file)
Your output file DOES NOT EXIST YET: you CREATE it at the path your lens
prompt names, and write it INCREMENTALLY (append each finding as you
confirm it, so a crash loses nothing). Shape:

  # <LENS> critic, inline-c
  ## Findings
  ### <LENS>-n  <one-line title>
  - status: CONFIRMED (with repro: input, command or file:line/§ quoted,
    observed vs expected) | SUSPECTED (what would confirm it)
  - severity: answer | speed | size | maintenance | doc | design | trust
  - effort: (paragraph edit / section rewrite / build-stage cost)
  - blast radius: what else moves if fixed
  - where: inline_c §x.y (and the other file:line it conflicts with)
  - argument: ...; a finding against a ruled D-row or a Q1-Q8 answer cites
    it and argues, or is dropped
  - proposed fix: one or two sentences
  ## PROBED-AND-HELD
  What you checked that holds, with case counts (e.g. "12 PCRE2 probes,
  all as the note states").
  ## DONE

Write `## DONE` last. Your final chat reply: at most 150 words (count of
findings by severity, the path). The FILE is what is read; replies may be
lost.
