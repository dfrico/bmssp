"""Compare BMSSP against Dijkstra on 3,000 random graphs (real and integer weights). Run: python3 stress.py"""
import random
from bmssp import dijkstra, bmssp
graph = {
    'A': [('B', 4), ('C', 2)],
    'B': [('A', 4), ('C', 1), ('D', 5)],
    'C': [('A', 2), ('B', 1), ('D', 8), ('E', 10)],
    'D': [('B', 5), ('C', 8), ('E', 2), ('F', 6)],
    'E': [('C', 10), ('D', 2), ('F', 3)],
    'F': [('D', 6), ('E', 3)]
}
print(dijkstra(graph,'A')); print(bmssp(graph,'A'))
fails=0; cases=0
for seed in range(3000):
    r=random.Random(seed); n=r.choice([1,2,4,8,16,64,256,1024,4096]); deg=r.choice([1,2,4,8])
    intw = r.random()<0.5
    g={i:[] for i in range(n)}
    for _ in range(n*deg):
        u,v=r.randrange(n),r.randrange(n)
        g[u].append((v, r.randint(0,3) if intw else r.random()*r.choice([1,100])))
    s=r.randrange(n)
    cases+=1
    if dijkstra(g,s)!=bmssp(g,s):
        fails+=1; print("FAIL",seed,n,deg,intw)
print(cases,"cases",fails,"fails")
