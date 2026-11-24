#!/usr/bin/env python3
"""tests/lib/plants.py -- THE ONE APPLIER of the runner-embedded source plants
(FUW-12's class fix, lane plantfix, 2026-11-24; triage docs/dev/lanes/plantri_report.md).

Four runners carry a `plant_spec` case function and a `PLANTS` id list for their
`--plant ID` / `--plants` modes (memfn/tests/run_g2_win.sh, memfn/tests/run_g2_pres.sh,
tests/memfn/run_proof.sh, tests/memfn/run_wreply.sh). Each used to decode and apply its
own plants in a private python heredoc, and nothing re-read them: four FROM texts went
stale (0 occurrences) and stayed invisible until someone ran the mode by hand. Now the
runners apply through THIS file, and scripts/m6read_check_sab_anchors.py's plant pass
counts through THIS file (via each runner's `--plant-check` mode), so the checker's
question ("will the runner's applier apply this?") is answered by the applier itself,
never by a second decoder.

Two entries, one decoder:

  plants.py apply DIALECT BASE [C0DIR] -- EDIT...
      apply EDIT... in order to the files under BASE (cumulative: edit 2 sees edit 1),
      each FROM exactly once or exit 1 at that edit, the file untouched by it.
  plants.py check DIALECT BASE [C0DIR] RUNNER -- (--plant ID N EDIT1..EDITN)...
      count, never write: the same edits applied in memory, plant by plant, each
      against a fresh read of the tree. One TSV row per edit:
          ID  EDIT/N  STATUS  COUNT  PATH(relative to the repo root where it is under it)
      STATUS: OK (exactly once), STALE (0), AMBIGUOUS (>1), MISSING FILE, NO SPEC
      (N = 0: the runner's plant_spec has no case for a PLANTS id), and one row
      `ID - ORPHAN 0 RUNNER` per plant_spec case id that PLANTS does not list (a plant
      no --plants run ever applies). Then `plant-check: P plants, E edits, B bad`.
      Exit 0 iff B = 0.

THE DIALECTS (each the runner's own pre-plantfix rule, kept BIT FOR BIT; unifying them is a
separate decision, plantri_report.md "Fix shape" 3):

  win     run_g2_win.sh, run_proof.sh. Split as the shell did (`${spec%%@@*}`,
          `${rest%%@@*}`, `${rest#*@@}`): FILE up to the first `@@`, FROM up to the
          second, TO the rest (a later `@@` stays in TO). `\\n` -> newline, then
          `\\&` -> `&`. FILE under BASE.
  pres    run_g2_pres.sh. The same split; `\\\\n` stays the two-character C escape
          `\\n`, `\\n` -> newline, `\\&` -> `&`. FILE under BASE, or `@c0/X` = C0DIR/X.
  wreply  run_wreply.sh. `spec.split("@@")` into EXACTLY three fields (a fourth `@@`
          refuses); `\\n` -> newline only. FILE under BASE (the tree copy's root).

Refusal texts are each runner's old ones ("plant text found %d times"; wreply's
"%s: the text is found %d times"), on stderr, as before.

What this proves and what it does not: OK means the plant still APPLIES exactly once. An
applying plant is not a REACHING plant (it can apply and no longer go red: [MECH-REACH]);
that is the --plants run's question, not this file's.
"""
import os, re, sys

DIALECTS = ('win', 'pres', 'wreply')


def un_win(s):
    return s.replace('\\n', '\n').replace('\\&', '&')


def un_pres(s):
    return s.replace('\\\\n', '\x00').replace('\\n', '\n').replace('\x00', '\\n').replace('\\&', '&')


def un_wreply(s):
    return s.replace('\\n', '\n')


def shell_split(spec):
    """`file="${spec%%@@*}"; rest="${spec#*@@}"; from="${rest%%@@*}"; to="${rest#*@@}"`."""
    i = spec.find('@@')
    f, rest = (spec, spec) if i < 0 else (spec[:i], spec[i + 2:])
    j = rest.find('@@')
    a, b = (rest, rest) if j < 0 else (rest[:j], rest[j + 2:])
    return f, a, b


class Undecodable(Exception):
    pass


def decode(dialect, spec, base, c0):
    """One edit -> (path, FROM, TO), by the dialect's rule."""
    if dialect == 'wreply':
        parts = spec.split('@@')
        if len(parts) != 3:
            raise Undecodable('%d fields, not 3 (FILE@@FROM@@TO)' % len(parts))
        f, a, b = parts
        return base + '/' + f, un_wreply(a), un_wreply(b)
    f, a, b = shell_split(spec)
    if dialect == 'pres':
        path = (c0 + '/' + f[len('@c0/'):]) if f.startswith('@c0/') else base + '/' + f
        return path, un_pres(a), un_pres(b)
    return base + '/' + f, un_win(a), un_win(b)


def refusal(dialect, spec, n):
    if dialect == 'wreply':
        return '%s: the text is found %d times' % (spec.split('@@')[0], n)
    return 'plant text found %d times' % n


def cmd_apply(dialect, base, c0, edits):
    for spec in edits:
        try:
            p, a, b = decode(dialect, spec, base, c0)
        except Undecodable as e:
            sys.exit('undecodable plant edit: %s' % e)
        if not os.path.isfile(p):
            sys.exit('%s: no such file' % p)
        s = open(p).read()
        if s.count(a) != 1:
            sys.exit(refusal(dialect, spec, s.count(a)))
        open(p, 'w').write(s.replace(a, b))
    return 0


def case_ids(runner):
    """The ids plant_spec() has a case for: `<indent>S<digits>)` lines in its body."""
    ids, on = [], False
    for ln in open(runner).read().split('\n'):
        if ln.startswith('plant_spec() {'):
            on = True
            continue
        if on:
            if ln == '}':
                break
            m = re.match(r'\s*(S[0-9]+)\)', ln)
            if m:
                ids.append(m.group(1))
    return ids


def cmd_check(dialect, base, c0, runner, args):
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def rel(p):
        p = os.path.normpath(p)
        return os.path.relpath(p, root) if p.startswith(root + os.sep) else p

    plants, nedit, nbad, listed = 0, 0, 0, []
    i = 0
    while i < len(args):
        if args[i] != '--plant' or i + 2 >= len(args):
            sys.exit('plants.py check: malformed plant list at argument %d' % i)
        pid, n = args[i + 1], int(args[i + 2])
        edits = args[i + 3:i + 3 + n]
        if len(edits) != n:
            sys.exit('plants.py check: %s names %d edits, %d given' % (pid, n, len(edits)))
        i += 3 + n
        plants += 1
        listed.append(pid)
        if n == 0:
            print('%s\t0/0\tNO SPEC\t0\t%s' % (pid, rel(runner)))
            nbad += 1
            continue
        cur = {}
        for k, spec in enumerate(edits, 1):
            nedit += 1
            try:
                p, a, b = decode(dialect, spec, base, c0)
            except Undecodable as e:
                print('%s\t%d/%d\tUNDECODABLE\t0\t%s' % (pid, k, n, e))
                nbad += 1
                continue
            if p not in cur:
                cur[p] = open(p).read() if os.path.isfile(p) else None
            if cur[p] is None:
                print('%s\t%d/%d\tMISSING FILE\t0\t%s' % (pid, k, n, rel(p)))
                nbad += 1
                continue
            c = cur[p].count(a)
            st = 'OK' if c == 1 else 'STALE' if c == 0 else 'AMBIGUOUS'
            print('%s\t%d/%d\t%s\t%d\t%s' % (pid, k, n, st, c, rel(p)))
            if c == 1:
                cur[p] = cur[p].replace(a, b)   # cumulative, as the apply is
            else:
                nbad += 1
    for pid in case_ids(runner):
        if pid not in listed:
            print('%s\t-\tORPHAN\t0\t%s' % (pid, rel(runner)))
            nbad += 1
    print('plant-check: %d plants, %d edits, %d bad' % (plants, nedit, nbad))
    return 1 if nbad else 0


def main(argv):
    if len(argv) < 4 or argv[0] not in ('apply', 'check') or argv[1] not in DIALECTS:
        sys.exit('usage: plants.py apply|check win|pres|wreply BASE [C0DIR] [RUNNER] -- ...')
    if '--' not in argv:
        sys.exit('plants.py: no -- before the edits')
    k = argv.index('--')
    mode, dialect, head, rest = argv[0], argv[1], argv[2:k], argv[k + 1:]
    if mode == 'apply':
        if len(head) not in (1, 2):
            sys.exit('plants.py apply: BASE [C0DIR]')
        return cmd_apply(dialect, head[0], head[1] if len(head) > 1 else '', rest)
    if len(head) not in (2, 3):
        sys.exit('plants.py check: BASE [C0DIR] RUNNER')
    c0 = head[1] if len(head) == 3 else ''
    return cmd_check(dialect, head[0], c0, head[-1], rest)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
