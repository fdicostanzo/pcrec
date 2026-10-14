"""gridread: loaders for the grid1 timing slot's outputs (no clock, no build).

Inputs (all read-only, under the slot directory OUT = worktrees/memfn-slot/grid1/):
  time_F1.log, time_F3.log, time_EXT.log   the per-row tables time.sh printed
  time/raw_F1.tsv, raw_F3.tsv, raw_EXT.tsv every launch's value (round, position, load1)
  counts.tsv                               the no-clock counters, one row per
                                           (cell, arm, subject, mode); streamed rows are
                                           SUMMED over nbuf buffers
  subj_facts.tsv                           the planted counts per subject (streamed: summed)
  arms.tsv, slot.status, check.log, plants.log   provenance only

The per-input sha256 list is SHA256SUMS beside this file; `gridread.py --check OUT`
verifies it before anything is read.
"""
import collections, csv, hashlib, os, statistics

INPUTS = ['time_F1.log', 'time_F3.log', 'time_EXT.log', 'time/raw_F1.tsv', 'time/raw_F3.tsv',
          'time/raw_EXT.tsv', 'counts.tsv', 'subj_facts.tsv', 'subjects.tsv', 'arms.tsv',
          'slot.status', 'check.log', 'plants.log', 'oracle.tsv']

# compile-time facts per own cell (grid1_report.md §1.1; costmodel cmload.py TERMS/KIND)
TERMS = {'dig': 1, 'bounded': 1, 'dfa-hat': 2,
         'f3-dig': 1, 'f3-hex-run': 2, 'f3-word-eq': 3, 'f3-quad': 4}
KIND = {'dig': 'PF', 'bounded': 'PF', 'dfa-hat': 'HAT'}
# bytes of a planted match token the DFA consumes after the find's landing byte
# (grid.py CELLS: dig "Nx" -> 'x'; dfa-hat " true "/" null "/" false " -> 3/3/4 letters
# after the hat's landing on the first letter; bounded "c " -> the one letter is the
# landing itself).  ADV = bytes the find advances = n - matches * TOKC (all mode).
TOKC = {'dig': 1.0, 'dfa-hat': 10.0 / 3.0, 'bounded': 0.0}
TOKLEN = {'dig': 2.0, 'dfa-hat': 5.0 + 1.0 / 3.0, 'bounded': 2.0}
WIDTH = {'walk': 1, 'V1': 8, 'V2': 8, 'V3': 8, 'S1': 64, 'S2': 64, 'S3': 64, 'Sn': 64,
         'A1': 64, 'A2': 64, 'A3': 64, 'An': 64, 'G1': 8}
KEPT = {'V3', 'S3', 'A3'}
STATELESS = {'Sn', 'An'}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def load_table(path):
    """time.sh's printed table: one dict per row (A/A rows included)."""
    rows = []
    for ln in open(path):
        if ln.startswith('#') or not ln.strip():
            continue
        p = ln.split()
        if len(p) != 11 or p[0] == 'cell' or p[2] not in ('first', 'all'):
            continue
        try:
            ns = float(p[4])
        except ValueError:
            continue
        rows.append(dict(cell=p[0], subj=p[1], mode=p[2], arm=p[3], ns=ns, base=float(p[5]),
                         delta=float(p[6]), floor=float(p[7]), spread=p[8], verdict=p[10]))
    return rows


def load_groupnotes(path):
    """`# group N done: CELL SUBJ MODE load1-at-start=X waits=W` lines."""
    notes = []
    for ln in open(path):
        if ln.startswith('# group'):
            p = ln.split()
            d = {k: v for k, v in (x.split('=') for x in p if '=' in x)}
            notes.append(dict(cell=p[4], subj=p[5], mode=p[6], load1=float(d['load1-at-start']),
                              waits=int(d['waits'])))
    return notes


def load_raw(path):
    """every launch: key (cell, subj, mode) -> arm -> {round: ns}; plus the load1 list."""
    R = collections.defaultdict(lambda: collections.defaultdict(dict))
    loads, ans = [], collections.defaultdict(set)
    for d in csv.DictReader(open(path), delimiter='\t'):
        k = (d['cell'], d['subject'], d['mode'])
        R[k][d['arm']][int(d['round'])] = float(d['ns'])
        loads.append(float(d['load1']))
        ans[k].add(d['answer'])
    return R, loads, ans


def parse_kv(s):
    return {k: int(v) for k, v in (x.split('=') for x in s.split())}


def load_counts(path):
    C = {}
    for d in csv.DictReader(open(path), delimiter='\t'):
        C[(d['cell'], d['arm'], d['subject'], d['mode'])] = parse_kv(d['counters'])
    return C


def load_facts(path):
    F = {}
    for d in csv.DictReader(open(path), delimiter='\t'):
        F[d['name']] = dict(fam=d['family'], n=int(d['n']), g=int(d['g']), L=int(d['L']),
                            shape=d['shape'], reuse=d['reuse'], nbuf=int(d['nbuf']),
                            pm=int(d['planted_matches']), pl=int(d['planted_landings']))
    return F


def base_name(subj):
    return subj.split('@')[0]


def offset(subj):
    return int(subj.split('@')[1]) if '@' in subj else 0


def groups(rows):
    g = collections.OrderedDict()
    for r in rows:
        g.setdefault((r['cell'], r['subj'], r['mode']), {})[r['arm']] = r
    return g


def med(xs):
    return statistics.median(xs) if xs else float('nan')
