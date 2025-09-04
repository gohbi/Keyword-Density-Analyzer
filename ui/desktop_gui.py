import sys
import requests
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox
)


API_URL = "http://localhost:8000/analyze"


class AnalyzerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keyword‑Density Analyzer")
        self.resize(600, 400)

        layout = QVBoxLayout()

        self.info_label = QLabel("Select a PDF or DOCX file")
        layout.addWidget(self.info_label)

        self.select_btn = QPushButton("Choose File")
        self.select_btn.clicked.connect(self.pick_file)
        layout.addWidget(self.select_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Word", "Count", "Density %"])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def pick_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open file", "", "Documents (*.pdf *.docx *.doc)"
        )
        if file_path:
            self.upload_and_show(file_path)

    def upload_and_show(self, path):
        try:
            with open(path, "rb") as f:
                files = {"file": (Path(path).name, f, "application/octet-stream")}
                resp = requests.post(API_URL, files=files)

            if resp.status_code != 200:
                raise RuntimeError(resp.text)

            data = resp.json()
            self.info_label.setText(
                f"File: {data['filename']} – {data['total_words']} words"
            )
            self.populate_table(data["top_keywords"])

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def populate_table(self, rows):
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(row["word"]))
            self.table.setItem(i, 1, QTableWidgetItem(str(row["count"])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row["density_pct"])))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AnalyzerWindow()
    win.show()
    sys.exit(app.exec())