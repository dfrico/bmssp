import heapq
import math

INF = (float('inf'),)  # sorts after every (distance, hops, vertex) key


def dijkstra(graph, start):
    dist = {node: float('inf') for node in graph}
    dist[start] = 0.0
    pq = [(0.0, start)]
    visited = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        for v, w in graph[u]:
            if v not in visited and d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))

    return dist


class Frontier:
    """Stand-in for the paper's data structure D (Lemma 3.3), backed by a heap.

    Same interface, worse complexity: insert, batch_prepend and pull all cost
    O(log n) per element instead of the paper's amortized bounds.
    """

    def __init__(self, M, B):
        self.M, self.B = M, B
        self.heap = []
        self.best = {}  # vertex -> smallest key currently stored

    def insert(self, v, key):
        if key < self.best.get(v, INF):
            self.best[v] = key
            heapq.heappush(self.heap, (key, v))

    def batch_prepend(self, pairs):
        for v, key in pairs:
            self.insert(v, key)

    def _drop_stale(self):
        while self.heap and self.best.get(self.heap[0][1]) != self.heap[0][0]:
            heapq.heappop(self.heap)

    def pull(self):
        """Remove up to M vertices with the smallest keys.
        Returns (bound, vertices): every key pulled < bound <= every key left."""
        S = set()
        self._drop_stale()
        while self.heap and len(S) < self.M:
            key, v = heapq.heappop(self.heap)
            del self.best[v]
            S.add(v)
            self._drop_stale()
        bound = self.heap[0][0] if self.heap else self.B
        return bound, S

    def __bool__(self):
        return bool(self.best)


class BMSSP:
    def __init__(self, graph, start):
        self.graph = graph
        n = len(graph)
        log_n = math.log2(max(n, 2))
        self.k = max(1, int(log_n ** (1 / 3)))
        self.t = max(1, int(log_n ** (2 / 3)))
        self.levels = math.ceil(log_n / self.t)
        self.dist = {node: float('inf') for node in graph}
        self.dist[start] = 0.0
        self.hops = {node: 0 for node in graph}  # edges on the current best path
        self.start = start
        self.relaxations = 0

    def key(self, v):
        """Order vertices by (distance, hops, id) so no two keys are ever equal.

        Hops matter for zero-weight edges: following an edge must always give
        a bigger key, even when it adds nothing to the distance."""
        return (self.dist[v], self.hops[v], v)

    def better(self, u, v, w):
        """Is the path through u at least as good as v's current one?"""
        return (self.dist[u] + w, self.hops[u] + 1) <= (self.dist[v], self.hops[v])

    def update(self, u, v, w):
        self.dist[v] = self.dist[u] + w
        self.hops[v] = self.hops[u] + 1

    def run(self):
        self.bmssp(self.levels, INF, {self.start})
        return self.dist

    def relax(self, u, v, w):
        """The same rule as Dijkstra and Bellman-Ford, with <= so ties count."""
        self.relaxations += 1
        if self.better(u, v, w):
            self.update(u, v, w)
            return True
        return False

    def find_pivots(self, B, S):
        """k rounds of Bellman-Ford from S, capped at distance B."""
        dist, k = self.dist, self.k
        W = set(S)
        layer = set(S)
        for _ in range(k):
            next_layer = set()
            for u in layer:
                for v, w in self.graph[u]:
                    if self.relax(u, v, w) and self.key(v) < B:
                        next_layer.add(v)
            W |= next_layer
            if len(W) > k * len(S):
                return set(S), W  # frontier is already big: keep every source
            layer = next_layer

        # Shortest-path forest inside W, then keep roots of big trees.
        children = {u: [] for u in W}
        has_parent = set()
        for u in W:
            for v, w in self.graph[u]:
                if (v in W and v != u and dist[v] == dist[u] + w
                        and self.hops[v] == self.hops[u] + 1):
                    children[u].append(v)
                    has_parent.add(v)

        pivots = set()
        for root in S:
            if root in has_parent:
                continue
            size, stack, seen = 0, [root], {root}
            while stack and size < k:
                x = stack.pop()
                size += 1
                for c in children[x]:
                    if c not in seen:
                        seen.add(c)
                        stack.append(c)
            if size >= k:
                pivots.add(root)
        return pivots, W

    def base_case(self, B, S):
        """Mini Dijkstra from a single vertex: stop after k + 1 vertices."""
        (x,) = S
        k = self.k
        U0 = set()
        pq = [self.key(x)]
        while pq and len(U0) < k + 1:
            entry = heapq.heappop(pq)
            u = entry[-1]
            if u in U0 or entry != self.key(u):
                continue
            U0.add(u)
            for v, w in self.graph[u]:
                self.relaxations += 1
                if (self.better(u, v, w)
                        and (self.dist[u] + w, self.hops[u] + 1, v) < B):
                    self.update(u, v, w)
                    heapq.heappush(pq, self.key(v))
        if len(U0) <= k:
            return B, U0
        B_new = max(self.key(v) for v in U0)
        return B_new, {v for v in U0 if self.key(v) < B_new}

    def bmssp(self, level, B, S):
        if level == 0:
            return self.base_case(B, S)

        k, t = self.k, self.t
        P, W = self.find_pivots(B, S)

        D = Frontier(M=2 ** ((level - 1) * t), B=B)
        for x in P:
            D.insert(x, self.key(x))

        B_last = min((self.key(x) for x in P), default=B)
        U = set()
        limit = k * 2 ** (level * t)

        while len(U) < limit and D:
            B_i, S_i = D.pull()
            B_last, U_i = self.bmssp(level - 1, B_i, S_i)
            U |= U_i

            K = []
            for u in U_i:
                for v, w in self.graph[u]:
                    if self.relax(u, v, w):
                        new = self.key(v)
                        if B_i <= new < B:
                            D.insert(v, new)
                        elif B_last <= new < B_i:
                            K.append((v, new))
            K.extend((x, self.key(x)) for x in S_i if B_last <= self.key(x) < B_i)
            D.batch_prepend(K)

        B_final = min(B_last, B) if len(U) >= limit else B
        U |= {x for x in W if self.key(x) < B_final}
        return B_final, U


def bmssp(graph, start):
    return BMSSP(graph, start).run()
