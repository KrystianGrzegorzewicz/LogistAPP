import sys
import graphviz

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtSvgWidgets import QSvgWidget

from cpm import compute_cpm

INITIAL_TASKS = [
    {"name": "A", "duration": 3, "start": 1, "end": 2},
    {"name": "B", "duration": 4, "start": 2, "end": 3},
    {"name": "C", "duration": 6, "start": 2, "end": 4},
    {"name": "D", "duration": 7, "start": 3, "end": 5},
    {"name": "E", "duration": 1, "start": 5, "end": 7},
    {"name": "F", "duration": 2, "start": 4, "end": 7},
    {"name": "G", "duration": 3, "start": 4, "end": 6},
    {"name": "H", "duration": 4, "start": 6, "end": 7},
    {"name": "I", "duration": 1, "start": 7, "end": 8},
    {"name": "J", "duration": 2, "start": 8, "end": 9},
]

def build_graph_svg(tasks, result):
    """
    tasks: lista słowników z name, duration, start, end
    result: słownik z wynikami compute_cpm(), zawiera:
        - EET, LET, Slack dla zdarzeń
        - critical = lista nazw czynności krytycznych
    """
    dot = graphviz.Digraph(format="svg")
    dot.attr(rankdir="LR", nodesep="0.5", ranksep="0.5")

    # Wyznaczamy wszystkie zdarzenia
    events = set()
    for t in tasks:
        events.add(t["start"])
        events.add(t["end"])
    events = sorted(events)

    # EET, LET, Slack z result
    EET = result.get("EET", {})
    LET = result.get("LET", {})
    Slack = result.get("Slack", {})

    # Dodaj węzły z tabelką HTML
    for e in events:
        eet = EET.get(e, 0)
        let = LET.get(e, 0)
        slack = Slack.get(e, 0)
        label_html = f"""<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" BGCOLOR="white">
              <TR><TD COLSPAN="2" ALIGN="CENTER"><B>{e}</B></TD></TR>
              <TR><TD ALIGN="LEFT">EET: {eet}</TD><TD ALIGN="RIGHT">LET: {let}</TD></TR>
              <TR><TD COLSPAN="2" ALIGN="CENTER">Slack: {slack}</TD></TR>
            </TABLE>
        >"""
        dot.node(str(e), label=label_html, shape="circle")

    # Dodaj krawędzie dla czynności
    for t in tasks:
        color = "red" if t["name"] in result.get("critical", []) else "black"
        dot.edge(
            str(t["start"]),
            str(t["end"]),
            label=f"{t['name']} ({t['duration']})",
            color=color,
            fontcolor=color,
        )

    return dot.pipe(format="svg")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPM GUI")

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Duration", "Start", "End"]
        )
        self.table.itemChanged.connect(self.recompute)

        btn = QPushButton("Dodaj wiersz")
        btn.clicked.connect(self.add_row)

        self.svg = QSvgWidget()
        self.svg.setMinimumHeight(400)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(btn)
        layout.addWidget(self.svg)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.load_tasks(INITIAL_TASKS)
        self.recompute()

    def load_tasks(self, tasks):
        self.table.blockSignals(True)
        self.table.setRowCount(len(tasks))
        for r, t in enumerate(tasks):
            self.table.setItem(r, 0, QTableWidgetItem(t["name"]))
            self.table.setItem(r, 1, QTableWidgetItem(str(t["duration"])))
            self.table.setItem(r, 2, QTableWidgetItem(str(t["start"])))
            self.table.setItem(r, 3, QTableWidgetItem(str(t["end"])))
        self.table.blockSignals(False)
        
    def add_row(self):
        self.table.insertRow(self.table.rowCount())

    def read_tasks(self):
        tasks = []
        for r in range(self.table.rowCount()):
            try:
                tasks.append(
                    {
                        "name": self.table.item(r, 0).text(),
                        "duration": int(self.table.item(r, 1).text()),
                        "start": int(self.table.item(r, 2).text()),
                        "end": int(self.table.item(r, 3).text()),
                    }
                )
            except Exception:
                pass
        return tasks

    def recompute(self):
        tasks = self.read_tasks()
        if not tasks:
            return

        result = compute_cpm(tasks)

        svg_data = build_graph_svg(tasks, result)
        self.svg.load(svg_data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())