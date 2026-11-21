import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate')
from ev import *
src = open('/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate/run5.py').read().split("print('== H')")[0]
src = src.replace("I1 = lambda", "I1_old = lambda").replace("I2a = lambda", "I2a_old = lambda").replace("I2b = lambda", "I2b_old = lambda")
src = src.replace("R = prod(lt(10), lt(30))", """R = prod(lt(10), lt(30))
I1 = lambda t: all(m and R(h, m) for h, m in items(t))
I2a = lambda t: all((not m) or R(h, m) for h, m in items(t))
I2b = lambda t: all(lt(10)(h) and ((not m) or lt(30)(m)) for h, m in items(t))""")
src = src.replace("('m=00 R', J(('h','m'), R, {'m': '00'}))]", "('m=00 R', J(('h','m'), R, {'m': '00'})), ('h=0,m=0 R', J(('h','m'), R, {'h': '0', 'm': '0'})), ('none m=0 !R', None_(J(('h','m'), NR, {'m': '0'})))]")
exec(src)
