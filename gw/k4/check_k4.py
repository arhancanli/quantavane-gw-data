# Separate checker (k4 agent, 12 Nov 2026; shares no code with the encoders): for each colouring string (one symbol per
# point of [1,n]) report n, the number of colours, the colour counts, the number of rainbow k-APs and of monochromatic
# l-APs (an AP is x, x+d, ..., d >= 1, inside [1,n]). Usage: check_k4.py k l STRING... (or @file with one per line)
import sys
k, l = int(sys.argv[1]), int(sys.argv[2])
items = []
for a in sys.argv[3:]:
    items += [s.strip() for s in open(a[1:]) if s.strip()] if a.startswith('@') else [a]
for s in items:
    n = len(s); rainbow = mono = 0
    for start in range(n):
        d = 1
        while start + (min(k, l) - 1) * d < n:
            if start + (k - 1) * d < n:
                terms = [s[start + j * d] for j in range(k)]
                if len(set(terms)) == k: rainbow += 1
            if start + (l - 1) * d < n:
                terms = [s[start + j * d] for j in range(l)]
                if len(set(terms)) == 1: mono += 1
            d += 1
    counts = {c: s.count(c) for c in sorted(set(s))}
    verdict = 'GOOD' if rainbow == 0 and mono == 0 else 'BAD'
    print(f'n={n} colours={len(counts)} counts={list(counts.values())} rainbow{k}={rainbow} mono{l}={mono} {verdict}')
