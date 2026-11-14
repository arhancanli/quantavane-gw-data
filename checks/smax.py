# s_k(l): the largest number of colours of a colouring of {0,...,l-1} with no rainbow k-AP (exhaustive search over
# colourings in first-occurrence form). Written for papers/gw-2026 (independent of k5/smax_k.py).
# Also prints one extremal colouring for each (k, l).
import sys, itertools
def rainbow_free(z, k):
    l = len(z)
    for a in range(l):
        for d in range(1, l):
            if a + (k - 1) * d >= l: break
            if len({z[a + j * d] for j in range(k)}) == k: return False
    return True
def search(k, l):
    best, ex = 0, None
    def rec(z, r):
        nonlocal best, ex
        if len(z) == l:
            if r > best: best, ex = r, list(z)
            return
        if r + (l - len(z)) <= best: return
        for col in range(r + 1):
            z.append(col)
            if rainbow_free(z, k): rec(z, max(r, col + 1))
            z.pop()
    rec([0], 1); return best, ex
for k in (3, 4, 5, 6):
    print(f'k={k}: ' + '; '.join(f's({l})={b} e.g. {"".join(map(str, e))}' for l in range(3, 13) for b, e in [search(k, l)]))
