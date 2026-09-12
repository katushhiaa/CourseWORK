from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QAbstractItemView
)
from app.security.auth_service import get_all_requests, approve_request, reject_request

class RequestsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Логін", "Бажана роль", "Статус"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("Оновити")
        btn_approve = QPushButton("Підтвердити користувача")
        btn_reject = QPushButton("Відхилити користувача")

        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_approve)
        btn_layout.addWidget(btn_reject)
        layout.addLayout(btn_layout)

        btn_refresh.clicked.connect(self.load_requests)
        btn_approve.clicked.connect(self.approve_selected)
        btn_reject.clicked.connect(self.reject_selected)

        self.load_requests()

    def load_requests(self):
        self.table.clearContents()
        data = get_all_requests()
        self.table.setRowCount(len(data))
        for row, req in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(req["login"]))
            self.table.setItem(row, 1, QTableWidgetItem(req["requested_role"]))
            self.table.setItem(row, 2, QTableWidgetItem(req["status"]))

    def approve_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Увага", "Оберіть заявку.")
            return
        login = self.table.item(row, 0).text()
        approve_request(login)
        QMessageBox.information(self, "OK", f"Користувача '{login}' підтверджено.")
        self.load_requests()

    def reject_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Увага", "Оберіть заявку.")
            return
        login = self.table.item(row, 0).text()
        reject_request(login)
        QMessageBox.information(self, "OK", f"Заявку користувача '{login}' відхилено.")
        self.load_requests()

    def on_enter(self):
        if self.table.hasFocus():
            self.approve_selected()
        else:
            self.load_requests()

    def on_escape(self):
        self.load_requests()

