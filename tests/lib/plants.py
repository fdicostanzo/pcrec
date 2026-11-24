#!/usr/bin/env python3
"""tests/lib/plants.py -- THE ONE APPLIER of the runner-embedded source plants
(FUW-12's class fix, lane plantfix, 2026-11-24; triage docs/dev/lanes/plantri_report.md;
review r94's fixes, lane plantfix2).

The four shell runners carry a `plant_spec` case function and a `PLANTS` id list for their
`--plant ID` / `--plants` modes (memfn/tests/run_g2_win.sh, memfn/tests/run_g2_pres.sh,
tests/memfn/run_proof.sh, tests/memfn/run_wreply.sh). They apply through THIS file, and
scripts/m6read_check_sab_anchors.py's plant pass reads them through THIS file (each runner's
`--plant-check [check|dump]` mode), so the checker's question ("will the runner's applier
apply this?") is answered by the applier itself, never by a second decoder.

ONE DECODER (`decode`) and ONE APPLY LOOP (`run_edits`), three entries:

  plants.py apply DIALECT BASE [C0DIR] -- EDIT...
      run_edits over the files on disk: EDIT... in order (cumulative: edit 2 sees edit 1),
      each FROM exactly once or exit 1 at that edit, the file untouched by it.
  plants.py check DIALECT BASE [C0DIR] RUNNER OPTIONS -- (--plant ID N EDIT1..EDITN)...
      run_edits, plant by plant, over an IN-MEMORY copy (each plant a fresh copy of the
      tree): the same loop, only its file store differs. One TSV row per edit it reached
      (the loop stops at the first edit that does not apply, as apply does):
          ID  K/N  STATUS  COUNT  PATH(relative to the repo root where it is under it)
      STATUS: OK (exactly once), STALE (0), AMBIGUOUS (>1), MISSING FILE, UNDECODABLE,
      NO SPEC (K/N = 0/0: the runner's plant_spec has no case for a PLANTS id), and per
      plant_spec case label (read from `--labels`): `ID - ORPHAN 0 RUNNER` for an id PLANTS
      does not list (a plant no --plants run ever applies), `LABEL - BAD LABEL 0 RUNNER` for
      a label that is not an S<digits> id or `*`. Then `plant-check: P plants, E edits, B bad`
      (E counts the edits NAMED). Exit 0 iff B = 0.
  plants.py dump DIALECT BASE [C0DIR] RUNNER OPTIONS -- (--plant ID N EDIT...)...
      decode only: one row per edit, `ID K/N TWIN PATH FROM TO`, FROM and TO JSON strings,
      TWIN `twin` if `--twins` declares ID a twin of a tests/mech/sabotages row, else `-`
      (a declared id PLANTS does not list: `ID - twin - - -`). The plant pass's twin
      equality reads this, so it never decodes a plant itself.

OPTIONS (check, dump):
  --labels FILE        `declare -f plant_spec`'s text (bash's own normal form of the case
                       labels; required by check).
  --files base|c0 FILE THE COPY'S FILE SET: the relative paths (newline- or NUL-separated)
                       the runner's --plant copy of BASE / C0DIR holds. A path outside the
                       set reads as MISSING FILE, as it does in the copy. Read from the SAME
                       variable/function the --plant mode copies by (review r94 CA-1).
  --twins "IDS"        dump: the runner's declared twins (PLANT_TWINS).

THE DIALECTS (each the runner's own pre-plantfix rule, kept BIT FOR BIT; the self-test of
scripts/m6read_check_sab_anchors.py pins one row per rule below):

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
import json, os, re, sys

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


class DiskStore:
    """apply's file store: the files on disk, read fresh at every edit."""
    def read(self, p):
        return open(p).read() if os.path.isfile(p) else None

    def write(self, p, s):
        open(p, 'w').write(s)


class MemStore:
    """check's file store: an in-memory copy of the tree, keyed by realpath (two spellings
    of one file are one file, as on disk), admitting only the copy's file set."""
    def __init__(self, admit):
        self.mem, self.admit = {}, admit

    def read(self, p):
        if not self.admit(p):
            return None
        k = os.path.realpath(p)
        if k not in self.mem:
            self.mem[k] = open(p).read() if os.path.isfile(p) else None
        return self.mem[k]

    def write(self, p, s):
        self.mem[os.path.realpath(p)] = s


def run_edits(dialect, base, c0, edits, store):
    """THE APPLY LOOP, both modes: yields (k, path, STATUS, count, refusal) per edit and
    stops after the first edit that does not apply."""
    for k, spec in enumerate(edits, 1):
        try:
            p, a, b = decode(dialect, spec, base, c0)
        except Undecodable as e:
            yield k, None, 'UNDECODABLE', 0, 'undecodable plant edit: %s' % e
            return
        s = store.read(p)
        if s is None:
            yield k, p, 'MISSING FILE', 0, '%s: no such file' % p
            return
        c = s.count(a)
        if c != 1:
            yield k, p, 'STALE' if c == 0 else 'AMBIGUOUS', c, refusal(dialect, spec, c)
            return
        store.write(p, s.replace(a, b))
        yield k, p, 'OK', 1, None


def cmd_apply(dialect, base, c0, edits):
    for k, p, st, c, why in run_edits(dialect, base, c0, edits, DiskStore()):
        if st != 'OK':
            sys.exit(why)
    return 0


def case_labels(text):
    """The labels of plant_spec's top-level `case` in `declare -f plant_spec`'s text (bash's
    normal form: a label line is the first line after the case line, or the line after a
    `;;` at the labels' own indent; alternatives ` | `-separated, quotes kept)."""
    lines = text.split('\n')
    top = next((i for i, ln in enumerate(lines) if re.match(r'\s*case\b.*\bin\s*$', ln)), None)
    if top is None or top + 1 >= len(lines):
        return []
    cind = len(lines[top]) - len(lines[top].lstrip(' '))
    ind = len(lines[top + 1]) - len(lines[top + 1].lstrip(' '))
    out, want = [], True
    for ln in lines[top + 1:]:
        if re.fullmatch(' ' * cind + r'esac;?\s*', ln):
            break
        if want and ln.startswith(' ' * ind) and ln.rstrip().endswith(')'):
            out += [x.strip() for x in ln.strip()[:-1].split(' | ')]
        want = ln.rstrip() in (' ' * ind + ';;', ' ' * ind + ';&', ' ' * ind + ';;&')
    return [x[1:-1] if len(x) > 1 and x[0] == x[-1] and x[0] in '\'"' else x for x in out]


def read_set(path):
    s = open(path).read()
    return {os.path.normpath(x) for x in (s.split('\0') if '\0' in s else s.split('\n')) if x}


def parse_plants(args):
    """(--plant ID N EDIT1..EDITN)... -> [(id, [edits] or None for N = 0)]"""
    out, i = [], 0
    while i < len(args):
        if args[i] != '--plant' or i + 2 >= len(args):
            sys.exit('plants.py: malformed plant list at argument %d' % i)
        pid, n = args[i + 1], int(args[i + 2])
        edits = args[i + 3:i + 3 + n]
        if len(edits) != n:
            sys.exit('plants.py: %s names %d edits, %d given' % (pid, n, len(edits)))
        i += 3 + n
        out.append((pid, edits if n else None))
    return out


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rel(p):
    p = os.path.normpath(p)
    return os.path.relpath(p, ROOT) if p.startswith(ROOT + os.sep) else p


def cmd_check(dialect, base, c0, runner, opt, plants):
    if 'labels' not in opt:
        sys.exit('plants.py check: --labels FILE (declare -f plant_spec) is required')
    sets = {k: read_set(v) for k, v in opt.get('files', {}).items()}
    roots = {'base': os.path.normpath(base), 'c0': os.path.normpath(c0) if c0 else None}

    def admit(p):
        """Is p a file of the --plant copy? Under BASE or C0DIR, and in its set if one is
        named; a path that leaves both roots is never the copy's."""
        p = os.path.normpath(p)
        for k, r in roots.items():
            if r is not None and p.startswith(r + os.sep):
                return k not in sets or os.path.relpath(p, r) in sets[k]
        return False

    nedit, nbad, listed = 0, 0, []
    for pid, edits in plants:
        listed.append(pid)
        if edits is None:
            print('%s\t0/0\tNO SPEC\t0\t%s' % (pid, rel(runner)))
            nbad += 1
            continue
        nedit += len(edits)
        for k, p, st, c, why in run_edits(dialect, base, c0, edits, MemStore(admit)):
            print('%s\t%d/%d\t%s\t%d\t%s' % (pid, k, len(edits), st, c,
                                             rel(p) if p else why[len('undecodable plant edit: '):]))
            nbad += st != 'OK'
    for lab in case_labels(open(opt['labels']).read()):
        if lab == '*':
            continue
        if not re.fullmatch(r'S[0-9]+', lab):
            print('%s\t-\tBAD LABEL\t0\t%s' % (lab, rel(runner)))
            nbad += 1
        elif lab not in listed:
            print('%s\t-\tORPHAN\t0\t%s' % (lab, rel(runner)))
            nbad += 1
    print('plant-check: %d plants, %d edits, %d bad' % (len(plants), nedit, nbad))
    return 1 if nbad else 0


def cmd_dump(dialect, base, c0, runner, opt, plants):
    twins = opt.get('twins', '').split()
    ids = [pid for pid, _ in plants]
    for pid, edits in plants:
        tw = 'twin' if pid in twins else '-'
        if edits is None:
            print('%s\t0/0\t%s\t-\t-\t-' % (pid, tw))
            continue
        for k, spec in enumerate(edits, 1):
            try:
                p, a, b = decode(dialect, spec, base, c0)
            except Undecodable as e:
                print('%s\t%d/%d\t%s\tUNDECODABLE\t%s\t-' % (pid, k, len(edits), tw, json.dumps(str(e))))
                continue
            print('%s\t%d/%d\t%s\t%s\t%s\t%s' % (pid, k, len(edits), tw, rel(p), json.dumps(a), json.dumps(b)))
    for t in twins:
        if t not in ids:
            print('%s\t-\ttwin\t-\t-\t-' % t)
    return 0


def main(argv):
    if len(argv) < 4 or argv[0] not in ('apply', 'check', 'dump') or argv[1] not in DIALECTS:
        sys.exit('usage: plants.py apply|check|dump win|pres|wreply BASE [C0DIR] [RUNNER] [OPTIONS] -- ...')
    if '--' not in argv:
        sys.exit('plants.py: no -- before the edits')
    k = argv.index('--')
    mode, dialect, head, rest = argv[0], argv[1], argv[2:k], argv[k + 1:]
    if mode == 'apply':
        if len(head) not in (1, 2):
            sys.exit('plants.py apply: BASE [C0DIR]')
        return cmd_apply(dialect, head[0], head[1] if len(head) > 1 else '', rest)
    pos, opt, i = [], {}, 0
    while i < len(head):
        a = head[i]
        if a in ('--labels', '--twins') and i + 1 < len(head):
            opt[a[2:]] = head[i + 1]
            i += 2
        elif a == '--files' and i + 2 < len(head) and head[i + 1] in ('base', 'c0'):
            opt.setdefault('files', {})[head[i + 1]] = head[i + 2]
            i += 3
        elif a.startswith('--'):
            sys.exit('plants.py %s: unknown option %s' % (mode, a))
        else:
            pos.append(a)
            i += 1
    if len(pos) not in (2, 3):
        sys.exit('plants.py %s: BASE [C0DIR] RUNNER' % mode)
    c0 = pos[1] if len(pos) == 3 else ''
    return (cmd_check if mode == 'check' else cmd_dump)(dialect, pos[0], c0, pos[-1], opt, parse_plants(rest))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
