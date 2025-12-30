import sys
import csv
import graphviz

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QFileDialog,
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, QUrl

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
    dot = graphviz.Digraph(format="svg")
    dot.attr(rankdir="LR", nodesep="0.5", ranksep="0.5")

    events = set()
    for t in tasks:
        events.add(t["start"])
        events.add(t["end"])
    events = sorted(events)

    EET = result.get("EET", {})
    LET = result.get("LET", {})
    Slack = result.get("Slack", {})

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
        self.setAcceptDrops(True)  # włączenie drag & drop

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Duration", "Start", "End"])
        self.table.itemChanged.connect(self.recompute)

        btn_add = QPushButton("Dodaj wiersz")
        btn_add.clicked.connect(self.add_row)

        btn_csv = QPushButton("Wczytaj CSV")
        btn_csv.clicked.connect(self.load_csv)

        self.svg = QSvgWidget()
        self.svg.setMinimumHeight(400)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(btn_add)
        layout.addWidget(btn_csv)
        layout.addWidget(self.svg)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.load_tasks(INITIAL_TASKS)
        self.recompute()

    # -------------------
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
                tasks.append({
                    "name": self.table.item(r, 0).text(),
                    "duration": int(self.table.item(r, 1).text()),
                    "start": int(self.table.item(r, 2).text()),
                    "end": int(self.table.item(r, 3).text()),
                })
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

    # -------------------
    def load_csv(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Wczytaj CSV", "", "CSV Files (*.csv)"
        )
        if not filename:
            return
        self._load_csv_file(filename)

    def _load_csv_file(self, filename):
        tasks = []
        try:
            with open(filename, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tasks.append({
                        "name": row["Name"],
                        "duration": int(row["Duration"]),
                        "start": int(row["Start"]),
                        "end": int(row["End"]),
                    })
        except Exception as e:
            print("Błąd wczytywania CSV:", e)
            return

        self.table.blockSignals(True)
        self.load_tasks(tasks)
        self.table.blockSignals(False)
        self.recompute()

    # -------------------
    # Drag & drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().endswith(".csv") for url in urls):
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.endswith(".csv"):
                self._load_csv_file(file_path)
        event.acceptProposedAction()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
