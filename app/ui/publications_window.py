from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.classes.Author import Author
from app.classes.Publication import Publication
from app.repositories import authors_repo as RA, publications_repo as RP

HEADERS = ["ID", "Код", "Назва", "Автори", "Обсяг (арк.)", "Тираж", "Номер замовлення"]

class PublicationsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)

        top = QHBoxLayout()
        self.search_edit = QLineEdit(placeholderText="Пошук за назвою або кодом")
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

        self._authors_cache: list[Author] = RA.list_authors("")
        self._authors_map = {str(a._id): a.full_name for a in self._authors_cache}

        self.form_box = QGroupBox("Форма видання")
        f = QFormLayout(self.form_box)
        self.inp_code = QLineEdit()
        self.inp_title = QLineEdit()
        self.list_authors = QListWidget()
        self.list_authors.setSelectionMode(self.list_authors.SelectionMode.MultiSelection)
        self._authors_cache: list[Author] = RA.list_authors("")
        self._authors_map = {str(a._id): a.full_name for a in self._authors_cache}
        for a in self._authors_cache:
            it = QListWidgetItem(a.full_name)
            it.setData(Qt.ItemDataRole.UserRole, str(a._id))
            self.list_authors.addItem(it)
        self.inp_volume = QLineEdit()
        self.inp_run = QLineEdit()
        self.inp_order_id = QLineEdit()

        f.addRow("Код видання:", self.inp_code)
        f.addRow("Назва:", self.inp_title)
        f.addRow("Автори:", self.list_authors)
        f.addRow("Обсяг у друк. арк.:", self.inp_volume)
        f.addRow("Тираж:", self.inp_run)
        f.addRow("Номер замовлення:", self.inp_order_id)

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

    def _reload_authors_list(self, selected_ids: list[str] = None):
        self.list_authors.clear()
        self._authors_cache = RA.list_authors("")
        self._authors_map = {str(a._id): a.full_name for a in self._authors_cache}

        for a in self._authors_cache:
            it = QListWidgetItem(a.full_name)
            it.setData(Qt.ItemDataRole.UserRole, str(a._id))
            if selected_ids and str(a._id) in selected_ids:
                it.setSelected(True)
            self.list_authors.addItem(it)

    def _selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        return self.table.item(rows[0].row(), 0).text() if rows else None

    def _authors_names(self, ids: list[str]) -> str:
        return ", ".join(self._authors_map.get(i, i) for i in ids)

    def _set_selected_authors(self, ids: list[str]):
        ids_set = set(ids)
        for i in range(self.list_authors.count()):
            it = self.list_authors.item(i)
            it.setSelected(it.data(Qt.ItemDataRole.UserRole) in ids_set)

    def _get_selected_authors(self) -> list[str]:
        return [str(it.data(Qt.ItemDataRole.UserRole)) for it in self.list_authors.selectedItems()]

    def reload(self):
        self._authors_cache = RA.list_authors("")
        self._authors_map = {str(a._id): a.full_name for a in self._authors_cache}

        data: list[Publication] = RP.list_publications(self.search_edit.text().strip())
        self.table.setRowCount(len(data))
        for r, pub in enumerate(data):
            row = [
                str(pub._id or ""),
                pub.code,
                pub.title,
                self._authors_names(pub.authors),
                str(pub.sheet_volume),
                str(pub.print_run),
                str(pub.order_id or ""),
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
        self._reload_authors_list([])
        self.inp_code.clear()
        self.inp_title.clear()
        self._set_selected_authors([])
        self.inp_volume.clear()
        self.inp_run.clear()
        self.inp_order_id.clear()
        self.form_box.setTitle("Нове видання")
        self.form_box.setVisible(True)

    def mode_edit(self):
        _id = self._selected_id()
        if not _id:
            QMessageBox.information(self, "Увага", "Оберіть рядок для редагування.")
            return
        self._mode = "edit"
        self._edit_id = _id
        pub = RP.get_publication(_id)
        if not pub:
            QMessageBox.warning(self, "Увага", "Не вдалося завантажити документ.")
            return

        self._reload_authors_list(pub.authors)
        self.inp_code.setText(pub.code)
        self.inp_title.setText(pub.title)
        self._set_selected_authors(pub.authors)
        self.inp_volume.setText(str(pub.sheet_volume))
        self.inp_run.setText(str(pub.print_run))
        self.inp_order_id.setText(str(pub.order_id or ""))

        self.form_box.setTitle("Редагувати видання")
        self.form_box.setVisible(True)

    def cancel_form(self):
        self.form_box.setVisible(False)
        self._mode = None
        self._edit_id = None

    def save_form(self):
        code = self.inp_code.text().strip()
        title = self.inp_title.text().strip()
        if not code or not title:
            QMessageBox.warning(self, "Увага", "Поля «Код» і «Назва» обовʼязкові.")
            return
        try:
            volume = float(self.inp_volume.text().strip() or 0)
        except ValueError:
            QMessageBox.warning(self, "Увага", "Обсяг має бути числом.")
            return
        try:
            run = int(float(self.inp_run.text().strip() or 0))
        except ValueError:
            QMessageBox.warning(self, "Увага", "Тираж має бути цілим числом.")
            return

        authors = self._get_selected_authors()
        order_id = self.inp_order_id.text().strip() or None

        try:
            pub = Publication(
                code=code,
                title=title,
                authors=authors,
                sheet_volume=volume,
                print_run=run,
                order_id=order_id,
                _id=self._edit_id if self._mode == "edit" else None,
            )
            if self._mode == "add":
                RP.create_publication(pub)
            elif self._mode == "edit" and self._edit_id:
                RP.update_publication(self._edit_id, pub)
            else:
                QMessageBox.warning(self, "Увага", "Невідомий режим форми.")
                return
            self.reload()
            self.cancel_form()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Операція не виконана:\n{e}")

    def delete_selected(self):
        _id = self._selected_id()
        if not _id:
            QMessageBox.information(self, "Увага", "Оберіть рядок для видалення.")
            return
        if (
            QMessageBox.question(self, "Підтвердження", "Видалити запис?")
            == QMessageBox.StandardButton.Yes
        ):
            try:
                RP.delete_publication(_id)
                self.reload()
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