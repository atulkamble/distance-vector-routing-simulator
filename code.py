#!/usr/bin/env python3

import math
import sys

infinity = math.inf

def HelperMethod(parsededges, nodes, start):
    distances = {node: infinity for node in nodes}
    preds = {node: None for node in nodes}
    distances[start] = 0

    for u, v, w in parsededges:
        if u == start:
            distances[v] = w
            preds[v] = u

    snapshots = [distances.copy()]

    for _ in range(len(nodes) - 1):
        updated = False
        for u, v, w in parsededges:
            if distances[u] != infinity and distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                preds[v] = u
                updated = True
        snapshots.append(distances.copy())
        if not updated:
            break

    return snapshots, preds, distances

def tables(start, nodes, all_snaps, graph, maxx=None, start_t=0):
    others = [n for n in nodes if n != start]
    cell_w = 6
    maxx = maxx if maxx is not None else len(all_snaps[start]) - 1

    for t in range(maxx + 1):
        print(f"\nDistance Table of router {start} at t={start_t + t}:")
        header = f"{'':<{cell_w}}" + "".join(f"{d:<{cell_w}}" for d in others)
        print(header)

        for via in others:
            row_line = f"{via:<{cell_w}}"
            link_via = graph[start].get(via, infinity)

            for dst in others:
                if dst == via:
                    cost = link_via
                elif t == 0:
                    cost = infinity
                else:
                    index = min(t - 1, len(all_snaps[via]) - 1)
                    neighbour_cost = all_snaps[via][index][dst]
                    cost = (link_via + neighbour_cost 
                            if link_via != infinity and neighbour_cost != infinity
                            else infinity)
                row_line += f"{'INF' if cost == infinity else cost:<6}"
            print(row_line)
    print()

def shortpath(start, preds, distance):
    rows = []
    for dst, cost in distance.items():
        if dst == start or cost == infinity:
            continue

        hop = dst
        seen = set()
        while preds[hop] is not None and preds[hop] != start:
            if hop in seen:
                hop = None
                break
            seen.add(hop)
            hop = preds[hop]

        if hop is None:
            continue

        rows.append((dst, hop, cost))
    return rows

def update_distance(nodes, graph, title, start_t=0):
    all_snaps = {}
    all_preds = {}

    edges = [(a, b, c) for a in graph for b, c in graph[a].items()]

    for r in nodes:
        snaps, preds, _ = HelperMethod(edges, nodes, start=r)
        all_snaps[r] = snaps
        all_preds[r] = preds

    t = max(len(s) for s in all_snaps.values()) - 1
    for r in nodes:
        tables(r, nodes, all_snaps, graph, maxx=t, start_t=start_t)

    for r in nodes:
        print(f"\nRouting Table of router {r}{':' if title.upper() != 'UPDATED' else ''}")
        best_path = all_snaps[r][-1]
        for destination, hop, cost in shortpath(r, all_preds[r], best_path):
            print(f"{destination},{hop},{cost}")
    print()
    return t + 1

def DistanceVector():
    inputdata = []
    try:
        while True:
            line = input()
            inputdata.append(line)
    except EOFError:
        pass

    nodes, edges, update = [], [], []
    sett = "nodes"

    for raw in inputdata:
        text = raw.strip()
        if not text:
            continue

        marker = text.upper()
        if marker == "START":
            sett = "edges"
            continue
        elif marker == "UPDATE":
            sett = "update"
            continue
        elif marker == "END":
            break

        if sett == "nodes":
            nodes.append(text)
        elif sett == "edges":
            edges.append(text)
        elif sett == "update":
            update.append(text)

    parsededges = []
    for line in edges:
        u, v, w_str = line.split()
        w = int(w_str)
        parsededges.append((u, v, w))
        parsededges.append((v, u, w))

    graph = {n: {} for n in nodes}
    for u, v, w in parsededges:
        graph[u][v] = w

    rounds_so_far = 0
    if edges:
        rounds_so_far = update_distance(nodes, graph, "Original", start_t=0)

    parsedupdate = []
    for line in update:
        a, b, c_str = line.split()
        c = int(c_str)
        parsedupdate.append((a, b, c))
        parsedupdate.append((b, a, c))

    for a, b, c in parsedupdate:
        for n in (a, b):
            if n not in nodes:
                nodes.append(n)
                graph[n] = {}
        if c == -1:
            graph[a].pop(b, None)
            graph[b].pop(a, None)
        else:
            graph[a][b] = c
            graph[b][a] = c

    if parsedupdate:
        update_distance(nodes, graph, "Updated", start_t=rounds_so_far)

def main():
    DistanceVector()

if __name__ == "__main__":
    main()
