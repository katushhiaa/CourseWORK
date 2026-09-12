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

from app.classes.Author import Author
from app.repositories import authors_repo as R

HEADERS = ["ID", "П.І.Б.", "Адреса", "Телефон", "Додаткова інформація"]

class AuthorsTab(QWidget):
    data_updated = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)

        top = QHBoxLayout()
        self.search_edit = QLineEdit(placeholderText="Пошук за П.І.Б.")
        self.btn_search = QPushButton("Пошук")
        self.btn_search.clicked.connect(self.reload)
        self.btn_add = QPushButton("Додати")
        self.btn_add.clicked.connect(self.mode_add)
        self.btn_edit = QPushButton("Редагувати")
        self.btn_edit.clicked.connect(self.mode_edit)
        self.btn_del = QPushButton("Видалити")
        self.btn_del.clicked.connect(self.delete_selected)

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

        self.form_box = QGroupBox("Форма автора")
        f = QFormLayout(self.form_box)
        self.inp_name = QLineEdit()
        self.inp_addr = QLineEdit()
        self.inp_phone = QLineEdit()
        self.inp_extra = QLineEdit()

        f.addRow("П.І.Б.:", self.inp_name)
        f.addRow("Адреса:", self.inp_addr)
        f.addRow("Телефон:", self.inp_phone)
        f.addRow("Додатково:", self.inp_extra)

        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("Зберегти")
        self.btn_save.clicked.connect(self.save_form)
        self.btn_cancel = QPushButton("Скасувати")
        self.btn_cancel.clicked.connect(self.cancel_form)
        btn_row.addStretch(1)
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_cancel)
        f.addRow(btn_row)

        self.form_box.setVisible(False)
        root.addWidget(self.form_box)

        self._mode: str | None = None
        self._edit_id: str | None = None
        self.reload()

    def _current_id(self):
        rows = self.table.selectionModel().selectedRows()
        return self.table.item(rows[0].row(), 0).text() if rows else None

    def reload(self):
        data: list[Author] = R.list_authors(self.search_edit.text().strip())
        self.table.setRowCount(len(data))
        for r, author in enumerate(data):
            row = [
                str(author._id or ""),
                author.full_name,
                author.address,
                author.phone,
                author.extra_info,
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
        self.inp_extra.clear()
        self.form_box.setTitle("Новий автор")
        self.form_box.setVisible(True)

    def mode_edit(self):
        _id = self._current_id()
        if not _id:
            QMessageBox.information(self, "Увага", "Оберіть рядок для редагування.")
            return
        r = self.table.currentRow()
        self._mode = "edit"
        self._edit_id = _id
        self.inp_name.setText(self.table.item(r, 1).text())
        self.inp_addr.setText(self.table.item(r, 2).text())
        self.inp_phone.setText(self.table.item(r, 3).text())
        self.inp_extra.setText(self.table.item(r, 4).text())
        self.form_box.setTitle("Редагувати автора")
        self.form_box.setVisible(True)

    def cancel_form(self):
        self.form_box.setVisible(False)
        self._mode = None
        self._edit_id = None

    def save_form(self):
        try:
            author = Author(
                full_name=self.inp_name.text(),
                address=self.inp_addr.text(),
                phone=self.inp_phone.text(),
                extra_info=self.inp_extra.text(),
                _id=self._edit_id if self._mode == "edit" else None,
            )
            if self._mode == "add":
                R.create_author(author)
            elif self._mode == "edit" and self._edit_id:
                R.update_author(self._edit_id, author)
            else:
                QMessageBox.warning(self, "Увага", "Невідомий режим форми.")
                return
            self.reload()
            self.cancel_form()
            self.data_updated.emit()
        except ValueError as e:
            QMessageBox.warning(self, "Помилка валідації", str(e))

    def delete_selected(self):
        _id = self._current_id()
        if not _id:
            QMessageBox.information(self, "Увага", "Оберіть рядок.")
            return
        if (
            QMessageBox.question(self, "Підтвердження", "Видалити запис?")
            == QMessageBox.StandardButton.Yes
        ):
            R.delete_author(_id)
            self.reload()
            self.data_updated.emit()

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