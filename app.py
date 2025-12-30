import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget,
    QTableWidgetItem, QPushButton, QWidget, QVBoxLayout
)
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

class MainWindow(QMainWindow):
    def load_tasks(self, tasks):
        self.table.setRowCount(len(tasks))
        for r, t in enumerate(tasks):
            self.table.setItem(r, 0, QTableWidgetItem(t["name"]))
            self.table.setItem(r, 1, QTableWidgetItem(str(t["duration"])))
            self.table.setItem(r, 2, QTableWidgetItem(str(t["start"])))
            self.table.setItem(r, 3, QTableWidgetItem(str(t["end"])))

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPM GUI")

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Duration", "Start", "End"]
        )

        btn = QPushButton("Dodaj wiersz")
        btn.clicked.connect(self.add_row)

        self.table.itemChanged.connect(self.recompute)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(btn)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        
        self.load_tasks(INITIAL_TASKS)
        self.recompute()

    
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
            except:
                pass
        return tasks

    def recompute(self):
        tasks = self.read_tasks()
        if not tasks:
            return
        result = compute_cpm(tasks)
        print("Ścieżka krytyczna:", result["critical"])

app = QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec())
