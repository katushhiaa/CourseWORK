from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox, QFormLayout, QDialog)
from PyQt6.QtCore import Qt
from app.repositories import authors_repo as R

HEADERS = ["ID", "П.І.Б.", "Адреса", "Телефон", "Додаткова інформація"]

class AuthorsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())

        top = QHBoxLayout()
        self.search_edit = QLineEdit(placeholderText="Пошук за П.І.Б.")
        self.btn_search = QPushButton("Пошук"); self.btn_search.clicked.connect(self.reload)
        self.btn_add = QPushButton("Додати"); self.btn_add.clicked.connect(self.add_dialog)
        self.btn_edit = QPushButton("Редагувати"); self.btn_edit.clicked.connect(self.edit_dialog)
        self.btn_del = QPushButton("Видалити"); self.btn_del.clicked.connect(self.delete_selected)
        top.addWidget(self.search_edit);
        top.addWidget(self.btn_search);
        top.addStretch(1)
        top.addWidget(self.btn_add);
        top.addWidget(self.btn_edit);
        top.addWidget(self.btn_del)

        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        self.layout().addLayout(top)
        self.layout().addWidget(self.table)
        self.reload()

    def reload(self):
        data = R.list_authors(self.search_edit.text().strip())
        self.table.setRowCount(len(data))
        for r, doc in enumerate(data):
            row = [str(doc.get("_id", "")),
                   doc.get("full_name", ""),
                   doc.get("address", ""),
                   doc.get("phone", ""),
                   doc.get("extra_info", "")]
            for c, val in enumerate(row):
                item = QTableWidgetItem(val)
                if c == 0:
                    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()

    def current_id(self):
        rows = self.table.selectionModel().selectedRows()
        return self.table.item(rows[0].row(), 0).text() if rows else None

    def add_dialog(self):
        self._add_dlg = AuthorEditDialog(self)
        dlg = AuthorEditDialog(self)
        if dlg.exec():
            R.create_author(dlg.full_name.text(), dlg.address.text(), dlg.phone.text(), dlg.extra_info.text())
            self.reload()

    def edit_dialog(self):
        _id = self.current_id()
        if not _id: QMessageBox.information(self,"Увага","Оберіть рядок."); return
        r = self.table.currentRow()
        dlg = AuthorEditDialog(self,
                               self.table.item(r, 1).text(), self.table.item(r, 2).text(),
                               self.table.item(r, 3).text(), self.table.item(r, 4).text()
                               )
        if dlg.exec():
            R.update_author(_id, dlg.full_name.text(),dlg.address.text(),dlg.phone.text(),dlg.extra_info.text())
            self.reload()

    def delete_selected(self):
        _id = self.current_id()
        if not _id: QMessageBox.information(self, "Увага", "Оберіть рядок."); return
        if (QMessageBox.question(self, "Підтвердження", "Видалити запис?") ==
                QMessageBox.StandardButton.Yes):
            R.delete_author(_id);
            self.reload()

class AuthorEditDialog(QDialog):
    def __init__(self, parent=None, full_name="", address="", phone="", extra_info=""):
        super().__init__(parent)
        self.setWindowTitle("Автор")
        self.setLayout(QVBoxLayout())
        form = QFormLayout()
        self.full_name = QLineEdit(full_name)
        self.address = QLineEdit(address)
        self.phone = QLineEdit(phone)
        self.extra_info = QLineEdit(extra_info)
        form.addRow("П.І.Б.:", self.full_name)
        form.addRow("Адреса:", self.address)
        form.addRow("Телефон:", self.phone)
        form.addRow("Додатково:", self.extra_info)
        self.layout().addLayout(form)
        btns = QHBoxLayout(); ok = QPushButton("Зберегти"); ok.clicked.connect(self.accept)
        cancel = QPushButton("Скасувати"); cancel.clicked.connect(self.reject)
        btns.addStretch(1); btns.addWidget(ok); btns.addWidget(cancel); self.layout().addLayout(btns)