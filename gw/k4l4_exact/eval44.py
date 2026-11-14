# Soundness check of gw44_cnf.py on a concrete colouring (12 Nov 2026).  Reads a colouring of [1,n] (digit string),
# puts it into the canonical form the encoder promises to keep (reflect it if b > b', then rename colours in order of
# first appearance), computes the TRUE values of every auxiliary variable from their definitions, and evaluates every
# clause of the CNF.  A good colouring must satisfy all of them; a single falsified clause means the encoding is wrong.
# Usage: eval44.py colouring.txt n R k l [flags...]   (flags as for gw44_cnf.py; the CNF is rebuilt in memory)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gw44_cnf import build

def canon(c, R, mirror):
    def b(s):
        seen = set()
        for t, x in enumerate(s, 1):
            seen.add(x)
            if len(seen) == R: return t
        return None
    if mirror and b(c) > b(c[::-1]): c = c[::-1]
    names = {}
    for x in c: names.setdefault(x, len(names))
    return [names[x] for x in c]

a = sys.argv[1:]
c = [int(ch) for ch in open(a[0]).read() if ch.isdigit()]
n, R, k, l = map(int, a[1:5]); flags = a[5:]
assert len(c) == n, (len(c), n)
exact, amo, mirror = '--exact' in flags, '--no-amo' not in flags, '--mirror' in flags
rb = 'miss' if '--miss' in flags else 'perm'
build.strict = '--mirror-strict-RED' in flags
cc = canon(c, R, mirror)
top, cl = build(n, R, k, l, exact=exact, amo=amo, mirror=mirror, rainbow=rb, rgs='--no-rgs' not in flags)
val = {}
for i in range(n):
    for col in range(R): val[i * R + col + 1] = (cc[i] == col)
v = n * R
for col in range(1, R):
    for i in range(n):
        v += 1; val[v] = col in cc[:i + 1]
if mirror:
    for col in range(R):
        for i in range(n):
            v += 1; val[v] = col in cc[i:]
for var, (pts, col) in build.aux.items():
    val[var] = all(cc[p] != col for p in pts); v += 1
assert v == top and len(val) == top
bad = [cls for cls in cl if not any((lit > 0) == val[abs(lit)] for lit in cls)]
print(f'{a[0]}: n={n} R={R} k={k} l={l} flags={flags}: {len(cl)} clauses, {len(bad)} falsified',
      'OK' if not bad else f'FIRST BAD {bad[0][:8]}')
