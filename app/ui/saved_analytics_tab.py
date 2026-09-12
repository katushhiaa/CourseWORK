from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QTableWidgetItem, QDialog, QLabel, \
    QHeaderView
from app.db import db

class SavedAnalyticsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID запиту", "Дата виконання", "Кількість рядків", "Попередній перегляд"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        btn_refresh = QPushButton("Оновити")
        btn_refresh.clicked.connect(self.load_data)
        layout.addWidget(btn_refresh)

        self.table.cellDoubleClicked.connect(self.open_details)

        self.load_data()

    def load_data(self):
        data = list(db["saved_analytics"].find({}).sort("executed_at", -1))
        self.data = data
        self.table.setRowCount(len(data))

        for r, item in enumerate(data):
            preview = ""
            if item.get("data"):
                first_row = item.get("data")[0]
                if isinstance(first_row, dict):
                    preview = ", ".join(str(v) for v in first_row.values())[:60]
                elif isinstance(first_row, (list, tuple)):
                    preview = ", ".join(str(v) for v in first_row)[:60]
                else:
                    preview = str(first_row)[:60]
            self.table.setItem(r, 0, QTableWidgetItem(str(item.get("query_index"))))
            self.table.setItem(r, 1, QTableWidgetItem(item.get("executed_at", "")))
            self.table.setItem(r, 2, QTableWidgetItem(str(len(item.get("data", [])))))
            self.table.setItem(r, 3, QTableWidgetItem(preview))

        self.table.resizeColumnsToContents()

    def open_details(self, row, _col):
        item = self.data[row]
        data = item.get("data", [])
        headers = item.get("headers", [])

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Результати аналітики #{item.get('query_index')}")
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)

        label = QLabel(f"Дата: {item.get('executed_at', '')} | Рядків: {len(data)}")
        label.setStyleSheet("color: #ccc; font-size: 13px;")
        layout.addWidget(label)

        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setRowCount(len(data))
        table.setHorizontalHeaderLabels(headers)

        for r, row_data in enumerate(data):
            for c, val in enumerate(row_data):
                table.setItem(r, c, QTableWidgetItem(str(val)))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(table)

        btn_close = QPushButton("Закрити")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)

        dialog.exec()

    def on_enter(self):
        row = self.table.currentRow()
        if row >= 0:
            self.open_details(row, 0)
        else:
            self.load_data()

    def on_escape(self):
        self.load_data()