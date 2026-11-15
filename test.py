"""Quick check: 400 random real-weight graphs + 200 integer-weight graphs with ties. Run: python3 test.py"""
import random, sys
from bmssp import dijkstra, bmssp, BMSSP

def rand_graph(n, m, seed, directed=True, reach=True):
    rnd = random.Random(seed)
    g = {i: [] for i in range(n)}
    if reach:  # random spanning path so everything is reachable (optional)
        order = list(range(n)); rnd.shuffle(order)
        for a, b in zip(order, order[1:]):
            g[a].append((b, rnd.random()))
    while sum(len(v) for v in g.values()) < m:
        u, v = rnd.randrange(n), rnd.randrange(n)
        if u != v:
            g[u].append((v, rnd.random()))
    return g

fails = 0; cases = 0
for seed in range(400):
    rnd = random.Random(seed)
    n = rnd.choice([2, 3, 5, 10, 30, 100, 300, 1000])
    m = n * rnd.choice([1, 2, 3, 5])
    g = rand_graph(n, m, seed, reach=rnd.random() < 0.7)
    s = 0
    a = dijkstra(g, s); b = bmssp(g, s)
    cases += 1
    bad = [v for v in g if not (a[v] == b[v] or abs(a[v]-b[v]) < 1e-9)]
    if bad:
        fails += 1
        if fails < 5: print("FAIL seed", seed, "n", n, "m", m, "bad", len(bad))
# integer weights with ties
for seed in range(200):
    rnd = random.Random(10000+seed)
    n = rnd.choice([10, 50, 200, 1000]); g = {i: [] for i in range(n)}
    for _ in range(3*n):
        u, v = rnd.randrange(n), rnd.randrange(n)
        if u != v: g[u].append((v, rnd.randint(1, 5)))
    a = dijkstra(g, 0); b = bmssp(g, 0); cases += 1
    if a != b:
        fails += 1
        if fails < 10: print("TIE FAIL seed", seed, n, sum(a[v]!=b[v] for v in g))
print(cases, "cases,", fails, "failures")
