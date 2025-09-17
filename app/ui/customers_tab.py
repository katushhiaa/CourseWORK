from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFormLayout, QGroupBox, QComboBox
)
from PyQt6.QtCore import Qt
from app.repositories import customers_repo as R

HEADERS = ["ID", "Тип", "Назва / ПІБ", "Контактна особа", "Адреса", "Телефон", "Факс"]

class CustomersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout()

        top = QHBoxLayout()
        self.search_edit =  QLineEdit(placeholderText="Пошук: назва/ПІБ, контакт, телефон")
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Всі", "Приватна особа", "Організація"])
        self.btn_search = QPushButton("Пошук"); self.btn_search.clicked.connect(self.reload)
        self.btn_add = QPushButton("Додати"); self.btn_add.clicked.connect(self.mode_add)
        self.btn_edit = QPushButton("Редагувати"); self.btn_edit.clicked.connect(self.mode_edit)
        self.btn_del = QPushButton("Видалити"); self.btn_del.clicked.connect(self.delete_selected)

        top.addWidget(self.search_edit)
        top.addWidget(self.type_filter)
        top.addWidget(self.btn_search)
        top.addStretch(1)
        top.addWidget(self.btn_add); top.addWidget(self.btn_edit); top.addWidget(self.btn_del)
        root.addLayout(top)

        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        root.addWidget(self.table)

        self.form_box = QGroupBox("Форма")
        f = QFormLayout(self.form_box)
        self.inp_type = QComboBox(); self.inp_type.addItems(["Приватна особа", "Організація"])
        self.inp_name = QLineEdit()
        self.inp_contact = QLineEdit()
        self.inp_addr = QLineEdit()
        self.inp_phone = QLineEdit()
        self.inp_fax = QLineEdit()
        f.addRow("Тип:", self.inp_type)
        f.addRow("Назва / ПІБ:", self.inp_name)
        f.addRow("Контактна особа:", self.inp_contact)
        f.addRow("Адреса:", self.inp_addr)
        f.addRow("Телефон:", self.inp_phone)
        f.addRow("Факс:", self.inp_fax)

        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("Зберегти"); self.btn_save.clicked.connect(self.save_form)
        self.btn_cancel = QPushButton("Скасувати"); self.btn_cancel.clicked.connect(self.cancel_form)
        btn_row.addStretch(1); btn_row.addWidget(self.btn_save); btn_row.addWidget(self.btn_cancel)
        f.addRow(btn_row)

        self.form_box.setVisible(False)
        root.addWidget(self.form_box)

        # технічні прапори
        self._mode: str | None = None  # "add" / "edit
        self._edit_id: str | None = None

        self.reload()

    def reload(self):
        filt = self.search_edit.text().strip()
        tsel = self.type_filter.currentText()
        tmap = {"Всі": None, "Приватна особа": "individual", "Організація": "organization"}
        data = R.list_customers(filt, tmap[tsel])

        self.table.setRowCount(len(data))
        for r, doc in enumerate(data):
            row = [
                str(doc.get("_id", "")),
                "Приватна особа" if doc.get("type") == "individual" else "Організація",
                doc.get("name", ""),
                doc.get("contact_person", ""),
                doc.get("address", ""),
                doc.get("phone", ""),
                doc.get("fax", "")
            ]

            for c, val in enumerate(row):
                it = QTableWidgetItem(val)
                if c == 0:
                    it.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(r, c, it)
            self.table.resizeColumnsToContents()

    def _current_id(self):
        rows = self.table.selectionModel().selectedRows()
        return self.table.item(rows[0].row(), 0).text() if rows else None

    def mode_add(self):
        self._mode = "add"; self._edit_id = None
        self._fill_form("Приватна особа", "", "", "", "", "")
        self.form_box.setTitle("Новий замовник")
        self.form_box.setVisible(True)

    def mode_edit(self):
        _id = self._current_id()
        if not _id:
            QMessageBox.information(self, "Увага", "Оберіть рядок для редагування.")
            return
        r = self.table.currentRow()
        self._mode = "edit";
        self._edit_id = _id
        self._fill_form(
            self.table.item(r, 1).text(),
            self.table.item(r, 2).text(),
            self.table.item(r, 3).text(),
            self.table.item(r, 4).text(),
            self.table.item(r, 5).text(),
            self.table.item(r, 6).text(),
        )
        self.form_box.setTitle("Редагувати замовника")
        self.form_box.setVisible(True)

    def _fill_form(self, t, name, contact, address, phone, fax):
        self.inp_type.setCurrentText(t)
        self.inp_name.setText(name)
        self.inp_contact.setText(contact)
        self.inp_addr.setText(address)
        self.inp_phone.setText(phone)
        self.inp_fax.setText(fax)

    def cancel_form(self):
        self.form_box.setVisible(False)
        self._mode = None;self._edit_id = None

    def save_form(self):
        doc = {
            "type": "individual" if self.inp_type.currentText() == "Приватна особа" else "organization",
            "name": self.inp_name.text().strip(),
            "contact_person": self.inp_contact.text().strip(),
            "address": self.inp_addr.text().strip(),
            "phone": self.inp_phone.text().strip(),
            "fax": self.inp_fax.text().strip()
        }

        if not doc["name"]:
            QMessageBox.warning(self, "Увага", "Поле «Назва / ПІБ» обовʼязкове.")
            return

        try:
            if self._mode == "add":
                R.create_customer(doc)
            elif self._mode == "edit" and self._edit_id:
                R.update_customer(self._edit_id, doc)
            else:
                QMessageBox.warning(self, "Увага", "Невідомий режим форми.")
                return

            self.reload()
            self.cancel_form()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Операція не виконана:\n{e}")

    def delete_selected(self):
        _id = self._current_id()
        if not _id:
            QMessageBox.information(self, "Увага", "Оберіть рядок для видалення.")
            return
        if QMessageBox.question(self, "Підтвердження", "Видалити запис?") == QMessageBox.StandardButton.Yes:
            try:
                R.delete_customer(_id)
                self.reload()
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити:\n{e}")

