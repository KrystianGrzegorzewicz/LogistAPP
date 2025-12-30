import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget,
    QTableWidgetItem, QPushButton, QWidget, QVBoxLayout
)
from cpm import compute_cpm

class MainWindow(QMainWindow):
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
