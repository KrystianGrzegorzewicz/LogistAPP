import networkx as nx
import graphviz

def compute_cpm(tasks):
    """
    tasks = list of dicts:
    {name, duration, start, end}
    """

    G = nx.DiGraph()

    for t in tasks:
        G.add_node(t["name"], duration=t["duration"])

    # precedencje z eventów
    for t in tasks:
        for p in tasks:
            if p["end"] == t["start"]:
                G.add_edge(p["name"], t["name"])

    # forward
    ES, EF = {}, {}
    for n in nx.topological_sort(G):
        ES[n] = max([EF[p] for p in G.predecessors(n)], default=0)
        EF[n] = ES[n] + G.nodes[n]["duration"]

    # backward
    LS, LF = {}, {}
    end_time = max(EF.values())
    for n in reversed(list(nx.topological_sort(G))):
        LF[n] = min([LS[c] for c in G.successors(n)], default=end_time)
        LS[n] = LF[n] - G.nodes[n]["duration"]

    slack = {n: LS[n] - ES[n] for n in G.nodes}
    critical = {n for n, s in slack.items() if s == 0}

    return {
        "ES": ES,
        "EF": EF,
        "LS": LS,
        "LF": LF,
        "slack": slack,
        "critical": critical
    }
