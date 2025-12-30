import networkx as nx

def compute_cpm(tasks):
    """
    tasks = list of dicts: {name, duration, start, end}
    Zwraca:
    {
        'EET': {...},   # Earliest Event Time
        'LET': {...},   # Latest Event Time
        'Slack': {...}, # Slack dla eventów
        'critical': [...] # nazwy czynności krytycznych
    }
    """

    # 1. Zbiór wszystkich zdarzeń
    events = set()
    for t in tasks:
        events.add(t["start"])
        events.add(t["end"])
    events = sorted(events)

    # 2. Forward (EET)
    EET = {e: 0 for e in events}
    for e in events:
        # znajdź wszystkie czynności kończące się w e
        incoming = [t for t in tasks if t["end"] == e]
        if incoming:
            EET[e] = max(EET[t["start"]] + t["duration"] for t in incoming)

    # 3. Backward (LET)
    LET = {e: float('inf') for e in events}
    LET[max(events)] = EET[max(events)]
    for e in reversed(events):
        outgoing = [t for t in tasks if t["start"] == e]
        if outgoing:
            LET[e] = min(LET[t["end"]] - t["duration"] for t in outgoing)
        if LET[e] == float('inf'):
            LET[e] = EET[e]  # jeśli brak outgoing, LET = EET

    # 4. Slack dla eventów
    Slack = {e: LET[e] - EET[e] for e in events}

    # 5. Ścieżka krytyczna czynności
    critical = []
    for t in tasks:
        if Slack[t["start"]] == 0 and Slack[t["end"]] == 0:
            # sprawdzamy czy EET+duration = EET następnego węzła
            if EET[t["start"]] + t["duration"] == EET[t["end"]]:
                critical.append(t["name"])

    return {
        "EET": EET,
        "LET": LET,
        "Slack": Slack,
        "critical": critical
    }
