from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.classes.Printer import Printer
from app.repositories import printers_repo as RP

HEADERS = ["ID", "Назва друкарні", "Адреса", "Телефон"]

class PrintersTab(QWidget):
    data_updated = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)

        top = QHBoxLayout()
        self.search_edit = QLineEdit(placeholderText="Пошук: назва, адреса або телефон")
        self.btn_search = QPushButton("Пошук")
        self.btn_search.clicked.connect(self.reload)
        self.btn_add = QPushButton("Додати")
        self.btn_add.clicked.connect(self.mode_add)
        self.btn_edit = QPushButton("Редагувати")
        self.btn_edit.clicked.connect(self.mode_edit)
        self.btn_del = QPushButton("Видалити")
        self.btn_del.clicked.connect(self.delete_printer)
        top.addWidget(self.search_edit)
        top.addWidget(self.btn_search)
        top.addStretch(1)
        top.addWidget(self.btn_add)
        top.addWidget(self.btn_edit)
        top.addWidget(self.btn_del)
        root.addLayout(top)

        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        root.addWidget(self.table)

        self.form_box = QGroupBox("Форма друкарні")
        f = QFormLayout(self.form_box)
        self.inp_name = QLineEdit()
        self.inp_addr = QLineEdit()
        self.inp_phone = QLineEdit()
        f.addRow("Назва:", self.inp_name)
        f.addRow("Адреса:", self.inp_addr)
        f.addRow("Телефон:", self.inp_phone)

        row = QHBoxLayout()
        self.btn_save = QPushButton("Зберегти")
        self.btn_save.clicked.connect(self.save_form)
        self.btn_cancel = QPushButton("Скасувати")
        self.btn_cancel.clicked.connect(self.cancel_form)
        row.addStretch(1)
        row.addWidget(self.btn_save)
        row.addWidget(self.btn_cancel)
        f.addRow(row)

        self.form_box.setVisible(False)
        root.addWidget(self.form_box)

        self._mode: str | None = None
        self._edit_id: str | None = None

        self.reload()

    def _selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        return self.table.item(rows[0].row(), 0).text() if rows else None

    def reload(self):
        data: list[Printer] = RP.list_printers(self.search_edit.text().strip())
        self.table.setRowCount(len(data))
        for r, printer in enumerate(data):
            row = [
                str(printer._id or ""),
                printer.name,
                printer.address,
                printer.phone,
            ]
            for c, val in enumerate(row):
                it = QTableWidgetItem(val)
                if c == 0:
                    it.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(r, c, it)
        self.table.resizeColumnsToContents()

    def mode_add(self):
        self._mode = "add"
        self._edit_id = None
        self.inp_name.clear()
        self.inp_addr.clear()
        self.inp_phone.clear()
        self.form_box.setTitle("Нова друкарня")
        self.form_box.setVisible(True)

    def mode_edit(self):
        _id = self._selected_id()
        if not _id:
            QMessageBox.information(self, "Увага", "Оберіть рядок для редагування.")
            return
        self._mode = "edit"
        self._edit_id = _id
        printer = RP.get_printer(_id)
        if not printer:
            QMessageBox.warning(self, "Увага", "Не вдалося завантажити документ.")
            return
        self.inp_name.setText(printer.name)
        self.inp_addr.setText(printer.address)
        self.inp_phone.setText(printer.phone)
        self.form_box.setTitle("Редагувати друкарню")
        self.form_box.setVisible(True)

    def cancel_form(self):
        self.form_box.setVisible(False)
        self._mode = None
        self._edit_id = None

    def save_form(self):
        name = self.inp_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Увага", "Поле «Назва» обовʼязкове.")
            return

        try:
            printer = Printer(
                name=self.inp_name.text(),
                address=self.inp_addr.text(),
                phone=self.inp_phone.text(),
                _id=self._edit_id if self._mode == "edit" else None,
            )
            if self._mode == "add":
                RP.create_printer(printer)
            elif self._mode == "edit" and self._edit_id:
                RP.update_printer(self._edit_id, printer)
            else:
                QMessageBox.warning(self, "Увага", "Невідомий режим форми.")
                return
            self.reload()
            self.cancel_form()
            self.data_updated.emit()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Операція не виконана:\n{e}")

    def delete_printer(self):
        _id = self._selected_id()
        if not _id:
            QMessageBox.information(self, "Увага", "Оберіть рядок для видалення.")
            return
        if (
            QMessageBox.question(self, "Підтвердження", "Видалити запис?")
            == QMessageBox.StandardButton.Yes
        ):
            try:
                RP.delete_printer(_id)
                self.reload()
                self.data_updated.emit()
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити:\n{e}")


    def on_enter(self):
        if self.form_box.isVisible():
            self.save_form()
        elif self.search_edit.hasFocus():
            self.reload()
        elif self.table.hasFocus():
            self.mode_edit()
        else:
            self.mode_add()


    def on_escape(self):
        if self.form_box.isVisible():
            self.cancel_form()
        elif self.search_edit.text():
            self.search_edit.clear()
            self.reload()