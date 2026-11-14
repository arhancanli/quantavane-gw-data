# Decode a CaDiCaL model of gw44_cnf.py: x(i,c) = i*R + c + 1.  Prints the colouring of [1,n] as a digit string.
# Usage: decode44.py solver_output n R
import sys
n, R = int(sys.argv[2]), int(sys.argv[3])
m = set()
for line in open(sys.argv[1]):
    if line.startswith('v'): m.update(int(t) for t in line.split()[1:] if int(t) > 0)
out = []
for i in range(n):
    cs = [c for c in range(R) if i * R + c + 1 in m]
    assert len(cs) >= 1, f'point {i + 1} has no colour'
    out.append(str(cs[0]))
print(''.join(out))
