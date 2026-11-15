"""Dijkstra vs BMSSP on random directed graphs (avg degree 4). Run: python3 bench.py"""
import random, time, heapq, statistics, sys, platform
from bmssp import dijkstra, BMSSP

def rand_graph(n, avg_deg, seed):
    r = random.Random(seed)
    g = {i: [] for i in range(n)}
    for _ in range(n * avg_deg):
        g[r.randrange(n)].append((r.randrange(n), r.random()))
    return g

def dijkstra_counted(graph, start):
    dist = {node: float('inf') for node in graph}; dist[start] = 0.0
    pq = [(0.0, start)]; visited = set(); relax = 0; pushes = 1
    while pq:
        d, u = heapq.heappop(pq)
        if u in visited: continue
        visited.add(u)
        for v, w in graph[u]:
            relax += 1
            if d + w < dist[v]:
                dist[v] = d + w; heapq.heappush(pq, (dist[v], v)); pushes += 1
    return dist, relax, pushes

def best_of(f, reps):
    ts = []
    for _ in range(reps):
        t = time.perf_counter(); out = f(); ts.append(time.perf_counter() - t)
    return min(ts), out

if __name__ == "__main__":
    print(platform.python_version(), platform.machine())
    print(f"{'n':>8} {'m':>9} {'k':>2} {'t':>2} {'L':>2} {'dij s':>7} {'bmssp s':>8} {'ratio':>6} {'dij relax':>10} {'bmssp relax':>12}")
    for n in [1_000, 10_000, 100_000, 1_000_000]:
        g = rand_graph(n, 4, n)
        reps = 3 if n <= 100_000 else 1
        td, (dd, rd, _) = best_of(lambda: dijkstra_counted(g, 0), reps)
        def run_b():
            b = BMSSP(g, 0); return b.run(), b
        tb, (db, b) = best_of(run_b, reps)
        assert dd == db
        print(f"{n:>8} {4*n:>9} {b.k:>2} {b.t:>2} {b.levels:>2} {td:>7.3f} {tb:>8.3f} {tb/td:>6.1f} {rd:>10} {b.relaxations:>12}", flush=True)
