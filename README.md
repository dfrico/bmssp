# BMSSP in Python

This is the companion code for the blog post "[From Dijkstra to BMSSP](https://dfrico.com/blog/2025-09-08-bmssp)".

A simplified Python version of BMSSP, the shortest-path algorithm from [Breaking the Sorting Barrier for Directed Single-Source Shortest Paths](https://arxiv.org/abs/2504.17033) (Duan et al., 2025). It uses a plain heap instead of the paper's data structure, so it gives correct distances but not the paper's running time. `bmssp(graph, start)` takes a dict of `node: [(neighbour, weight), ...]` and returns the distance to every node, like the `dijkstra` function in the same file.

It only needs Python 3. `test.py`, `stress.py` and `zero_weights.py` compare BMSSP against Dijkstra on random graphs, and `bench.py` times both. Run any of them with `python3 <file>.py`.

Released under the MIT License, see `LICENSE`.
