import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec17/simulate')
from emu import *
H,M=sec('h'),sec('m')
OPT=r'(?P<h>\d{1,2})(?::(?P<m>\d\d))?'
subs=[str(h) for h in range(0,13)]+[f'{h}:{m:02d}' for h in range(0,13) for m in (0,15,29,30,31,59)]
both=[s for s in subs if whole(OPT,NOT(lex_le2([H,M],(9,30))),s) and whole(OPT,NOT(lex_ge2([H,M],(9,30))),s)]
print('strictly above AND strictly below 9:30:', both)
acc_unset=[s for s in subs if ':' not in s and whole(OPT,lex_between2([H,M],(9,30),(11,0)),s)]
print('lex_between2 [9,30]..[11,0] accepts with m UNSET:', acc_unset)
# wrong-length by §3.2 (out of range entry absent -> tests false)
F=lambda gd: False
def ge3_short(lo):  # s = [(h:),(m:)], s[3] absent
    return ANY([H(padded('>',lo[0])), AND(H(padded('==',lo[0])), M(padded('>',lo[1]))), AND(H(padded('==',lo[0])), M(padded('==',lo[1])), F)])
TIME=r'(?P<h>\d{1,2}):(?P<m>\d\d)'
print('lex_ge3([(h:),(m:)],[9,0,0]) by §3.2 on 9:00 / 9:01:', whole(TIME,ge3_short((9,0,0)),'9:00'), whole(TIME,ge3_short((9,0,0)),'9:01'))
