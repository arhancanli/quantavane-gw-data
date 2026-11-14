# Separate checker: no rainbow 3-AP and no monochromatic l-AP; reports colours used.
import sys
def check(s, l):
    c = [int(x) for x in s]; n = len(c); rain = mono = 0
    for a in range(n):
        for d in range(1, n):
            if a + 2 * d < n and len({c[a], c[a + d], c[a + 2 * d]}) == 3: rain += 1
            if a + (l - 1) * d < n and len({c[a + j * d] for j in range(l)}) == 1: mono += 1
    return n, sorted(set(c)), [c.count(x) for x in sorted(set(c))], rain, mono
for s in sys.argv[2:]: print(check(s, int(sys.argv[1])))
