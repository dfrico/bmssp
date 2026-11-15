import random, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from bmssp import dijkstra, bmssp
f=0
for seed in range(2000):
    r=random.Random(seed); n=r.choice([2,8,16,64,256,1024]); deg=r.choice([1,2,4,8])
    ws=r.choice([[0],[0,1],[0,0,0,1],[0,5]])
    g={i:[] for i in range(n)}
    for _ in range(n*deg):
        g[r.randrange(n)].append((r.randrange(n), r.choice(ws)))
    s=r.randrange(n)
    if dijkstra(g,s)!=bmssp(g,s): f+=1; print("FAIL",seed)
print("zero-heavy: 2000 cases", f, "fails")
