# REAL (searched) mode: a program `P & C` accepts a subject iff SOME span s[i:j] is matched whole by P and C holds
# on that span's one reading (§2.2 D196: the right operand filters which spans are admitted; §11 searched program).
import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec17/simulate')
from emu import *
def searched(P,C,subj):
    for i in range(len(subj)):
        for j in range(i+1,len(subj)+1):
            m=re.fullmatch(P,subj[i:j])
            if m and C(m.groupdict()): return subj[i:j]
    return None
H,M,S3=sec('h'),sec('m'),sec('sec'); MA,MI,PA=sec('major'),sec('minor'),sec('patch')
TIME=r'(?P<h>\d{1,2}):(?P<m>\d\d)'; PAST=r'(?P<m>\d\d) past (?P<h>\d{1,2})'
HMS=r'(?P<h>\d{1,2}):(?P<m>\d\d):(?P<sec>\d\d)'
VER=r'(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)'
SEMVER=r'(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)'
rows=[
 ('time',TIME,lex_between2([H,M],[9,0],[10,0]),['10:01','8:59','11:00','9:5','19:30','10:001']),
 ('past',PAST,lex_between2([H,M],[9,0],[10,0]),['01 past 10','59 past 8','30 past 19']),
 ('hms',HMS,lex_between3([H,M,S3],[9,30,5],[10,0,0]),['9:30:04','10:00:01','8:59:59','9:30','19:30:05']),
 ('ver',VER,lex_between2([MA,MI],[1,4],[1,10]),['1.3','1.11','2.0','0.9','1.04','1x4','1.40','11.4','1.100']),
 ('semver',SEMVER,lex_ge3([MA,MI,PA],[1,4,0]),['1.3.99','0.9.9','1.04.0','0.1.4.0']),
]
for name,P,C,rej in rows:
    for s in rej:
        sp=searched(P,C,s)
        print('%-7s %-12r whole:%-6s searched:%s' % (name,s,'accept' if whole(P,C,s) else 'reject', ('accept via span %r'%sp) if sp else 'reject'))
