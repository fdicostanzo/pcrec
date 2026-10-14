"""costmodel: loaders and the per-row join (no clock, no build).

Every input is read-only and passed by path through the environment-free
function arguments below; `costmodel.py` wires the default paths.

Populations:
  ALPHA   slot25c/time.log           R17-b new vs deny (the walk), 160 rows
  SPIKE   spike1/time.log            V0 walk vs V1..V4, S1..S4, A1..A4
  SPIKE2  spike1/v2/time2.log        dfa-hat P1/P2/P3/P4/P3W per width
  SLOT2   probes/r17/out/slot2/times.tsv   kernel-only density sweep
Counters:
  CNT9    costmodel/cnt/counts9.txt  r17loss's counting instrument, re-run
          over all nine subjects (uses, cold, skip bytes, masks); the 80
          slot25c lines reproduce lane r17loss's counts.txt byte for byte
  CV      spike1/counts.tsv          per-variant cold/hit/xcall/head/blocks
  CV2     spike1/v2/counts2.tsv      per-P-variant cands/blocks
  SUBJ    costmodel/subjstats.tsv    p, landings, gap stats per (cell, subject)
"""
import csv, re, collections

CELLS = "dig email word-eq hex-run bounded dfa-hat vm-hat vm-hat-1".split()
SUBS = "short prose64k digits64k prose1m mix64k docs64k docs1m code64k code1m".split()
# compile-time facts per cell (r17loss §1, read off the emitted __mask)
TERMS = {'dig': 1, 'email': 1, 'word-eq': 3, 'hex-run': 2, 'bounded': 1,
         'dfa-hat': 2, 'vm-hat': 1, 'vm-hat-1': 1}
SETSIZE = {'dig': 10, 'email': 26, 'word-eq': 53, 'hex-run': 16, 'bounded': 26,
           'dfa-hat': 3, 'vm-hat': 2, 'vm-hat-1': 1}
KIND = {'dig': 'PF', 'email': 'PF', 'word-eq': 'PF', 'hex-run': 'PF',
        'bounded': 'PF', 'dfa-hat': 'HAT', 'vm-hat': 'VM', 'vm-hat-1': 'VM'}
# shipped byte-rate prior summed over S (r17loss §1, src/findings/default.rxt)
PRIOR = {'dig': 74760, 'email': 663413, 'word-eq': 732246, 'hex-run': 284434,
         'bounded': 663413, 'dfa-hat': 119624, 'vm-hat': 64049, 'vm-hat-1': 665}
NBYTES = {'short': 40, 'prose64k': 65536, 'digits64k': 65536, 'prose1m': 1048576,
          'mix64k': 65536, 'docs64k': 65536, 'docs1m': 1048576, 'code64k': 65536,
          'code1m': 1048576}
REALTEXT = {'docs64k', 'docs1m', 'code64k', 'code1m'}


def load_alpha(path):
    rows = []
    for ln in open(path):
        if ln.startswith('#') or not ln.strip() or ln.startswith('cell'):
            continue
        p = ln.split()
        rows.append(dict(cell=p[0], layer=p[1], subj=p[2], mode=p[3],
                         base=float(p[4]), new=float(p[5]), deny=float(p[6]),
                         delta=float(p[7]), floor=float(p[8]), verdict=p[9]))
    return rows


def load_spike(path):
    rows = []
    for ln in open(path):
        if ln.startswith('#') or not ln.strip():
            continue
        p = ln.split()
        if len(p) != 10 or p[2] not in ('first', 'all'):
            continue
        try:
            ns = float(p[4])
        except ValueError:
            continue
        rows.append(dict(cell=p[0], subj=p[1], mode=p[2], var=p[3], ns=ns,
                         v0=float(p[5]), delta=float(p[6]), floor=float(p[7]),
                         verdict=p[9]))
    return rows


def groups(rows):
    g = collections.OrderedDict()
    for r in rows:
        g.setdefault((r['cell'], r['subj'], r['mode']), {})[r['var']] = r
    return g


def load_cnt9(path):
    C = {}
    for ln in open(path):
        p = ln.split()
        kv = dict(x.split('=') for x in p[3:])
        C[(p[0], p[1], p[2])] = {k: int(v) for k, v in kv.items()}
    return C


def load_cv(path):
    C = {}
    rd = csv.reader(open(path), delimiter='\t')
    hdr = next(rd)
    for p in rd:
        if len(p) < len(hdr):
            continue
        d = dict(zip(hdr, p))
        key = (d['cell'], d['var'], d['subject'], d['mode'])
        C[key] = {k: int(d[k] or 0) for k in hdr[4:]}
    return C


def load_cv2(path):
    C = {}
    rd = csv.reader(open(path), delimiter='\t')
    hdr = next(rd)
    for p in rd:
        if len(p) < len(hdr):
            continue
        d = dict(zip(hdr, p))
        C[(d['var'], d['subject'], d['mode'])] = {k: int(d[k] or 0) for k in hdr[3:]}
    return C


def load_subj(path):
    S = {}
    for d in csv.DictReader(open(path), delimiter='\t'):
        S[(d['cell'], d['subject'])] = dict(
            n=int(d['n']), ppm=int(d['ppm']), land=int(d['land']),
            gmean=float(d['gmean']), gcv=float(d['gcv']),
            g_lt8=float(d['g_lt8']), g_lt64=float(d['g_lt64']),
            runmean=float(d['runmean']), skmean=float(d['skmean']),
            skcv=float(d['skcv']), skmode=float(d['skmode']))
    return S


def load_slot2(path):
    return list(csv.DictReader(open(path), delimiter='\t'))
