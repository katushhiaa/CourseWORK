from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QFormLayout, QGroupBox, QComboBox, QListWidget,
    QListWidgetItem, QDateEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from app.repositories import orders_repo as RO
from app.repositories import customers_repo as RC
from app.repositories import publications_repo as RP
from app.repositories import printers_repo as RPR
from app.classes.Order import Order
from app.ui.cancel_dialog_tab import CancelDialog

HEADERS = [
    "ID", "Номер замовлення", "Замовник", "Вид продукції",
    "Видання", "Друкарня", "Дата прийому", "Дата виконання",
    "Виконано", "Скасування"
]


class OrdersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)

        top = QHBoxLayout()
        self.search_edit = QLineEdit(placeholderText="Пошук за номером або видом продукції")
        self.btn_search = QPushButton("Пошук"); self.btn_search.clicked.connect(self.reload)
        self.btn_add = QPushButton("Додати"); self.btn_add.clicked.connect(self.mode_add)
        self.btn_edit = QPushButton("Редагувати"); self.btn_edit.clicked.connect(self.mode_edit)
        self.btn_del = QPushButton("Видалити"); self.btn_del.clicked.connect(self.delete_selected)
        self.btn_cancel_order = QPushButton("Скасувати замовлення");self.btn_cancel_order.clicked.connect(self.cancel_order_dialog)
        top.addWidget(self.search_edit); top.addWidget(self.btn_search)
        top.addStretch(1)
        top.addWidget(self.btn_add); top.addWidget(self.btn_edit); top.addWidget(self.btn_del); top.addWidget(self.btn_cancel_order)
        root.addLayout(top)

        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        root.addWidget(self.table)

        self._customers = []
        self._customers_map = {}
        self._publications = []
        self._publications_map = {}
        self._printers = []
        self._printers_map = {}

        self.form_box = QGroupBox("Форма замовлення")
        f = QFormLayout(self.form_box)
        self.inp_number = QLineEdit()
        self.cmb_customer = QComboBox()
        for c in self._customers:
            self.cmb_customer.addItem(c.name, str(c._id))
        self.inp_product = QLineEdit()

        self.list_publications = QListWidget()
        self.list_publications.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for p in self._publications:
            it = QListWidgetItem(p.title)
            it.setData(Qt.ItemDataRole.UserRole, str(p._id))
            self.list_publications.addItem(it)

        self.cmb_printer = QComboBox()
        for pr in self._printers:
            self.cmb_printer.addItem(pr.name, str(pr._id))

        self.date_received = QDateEdit()
        self.date_received.setCalendarPopup(True)
        self.date_received.setDate(QDate.currentDate())

        self.date_completed = QDateEdit()
        self.date_completed.setCalendarPopup(True)
        self.date_completed.setDate(QDate.currentDate())

        self.chk_completed = QCheckBox("Замовлення виконано")

        f.addRow("Номер замовлення:", self.inp_number)
        f.addRow("Замовник:", self.cmb_customer)
        f.addRow("Вид продукції:", self.inp_product)
        f.addRow("Видання:", self.list_publications)
        f.addRow("Друкарня:", self.cmb_printer)
        f.addRow("Дата прийому:", self.date_received)
        f.addRow("Дата виконання:", self.date_completed)
        f.addRow(self.chk_completed)

        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("Зберегти"); self.btn_save.clicked.connect(self.save_form)
        self.btn_cancel = QPushButton("Скасувати"); self.btn_cancel.clicked.connect(self.cancel_form)
        btn_row.addStretch(1); btn_row.addWidget(self.btn_save); btn_row.addWidget(self.btn_cancel)
        f.addRow(btn_row)

        self.form_box.setVisible(False)
        root.addWidget(self.form_box)

        self._mode = None
        self._edit_id = None

        self.reload()

    def _selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        return self.table.item(rows[0].row(), 0).text() if rows else None

    def _selected_publications(self):
        return [it.data(Qt.ItemDataRole.UserRole) for it in self.list_publications.selectedItems()]

    def _set_selected_publications(self, ids: list[str]):
        ids_set = set(ids)
        for i in range(self.list_publications.count()):
            it = self.list_publications.item(i)
            it.setSelected(it.data(Qt.ItemDataRole.UserRole) in ids_set)

    def _pub_titles(self, ids: list[str]) -> str:
        return ", ".join(self._publications_map.get(i, i) for i in ids)

    def reload(self):
        self._customers.clear()
        self._customers_map.clear()
        self._publications.clear()
        self._publications_map.clear()
        self._printers.clear()
        self._printers_map.clear()

        self._customers = RC.list_customers()
        self._customers_map = {str(c._id): c.name for c in self._customers}

        self._publications = RP.list_publications()
        self._publications_map = {str(p._id): p.title for p in self._publications}

        self._printers = RPR.list_printers()
        self._printers_map = {str(p._id): p.name for p in self._printers}

        data = RO.list_orders(self.search_edit.text().strip())
        self.table.setRowCount(len(data))

        for r, order in enumerate(data):
            row = [
                str(order._id or ""),
                order.order_number,
                self._customers_map.get(order.customer_id, order.customer_id),
                order.product_type,
                self._pub_titles(order.publication_ids),
                self._printers_map.get(order.printer_id, ""),
                str(order.date_received),
                str(order.date_completed or ""),
                "Так" if order.is_completed else "Ні",
                getattr(order, "cancel_reason", "") or ""
            ]
            for c, val in enumerate(row):
                it = QTableWidgetItem(val)
                if c == 0:
                    it.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(r, c, it)
        self.table.resizeColumnsToContents()

    def mode_add(self):
        self._mode = "add"; self._edit_id = None
        self.cmb_customer.clear()
        for c in RC.list_customers():
            self.cmb_customer.addItem(c.name, str(c._id))

        self.cmb_printer.clear()
        for p in RPR.list_printers():
            self.cmb_printer.addItem(p.name, str(p._id))

        self.list_publications.clear()
        for pub in RP.list_publications():
            it = QListWidgetItem(pub.title)
            it.setData(Qt.ItemDataRole.UserRole, str(pub._id))
            self.list_publications.addItem(it)

        self.inp_number.clear()
        self.inp_product.clear()
        self._set_selected_publications([])
        self.cmb_customer.setCurrentIndex(0)
        self.cmb_printer.setCurrentIndex(0)
        self.date_received.setDate(QDate.currentDate())
        self.date_completed.setDate(QDate.currentDate())
        self.chk_completed.setChecked(False)

        self.form_box.setTitle("Нове замовлення")
        self.form_box.setVisible(True)

    def mode_edit(self):
        _id = self._selected_id()
        if not _id:
            QMessageBox.information(self, "Увага", "Оберіть рядок.")
            return

        order = RO.get_order(_id)
        if not order:
            QMessageBox.warning(self, "Помилка", "Не вдалося завантажити замовлення.")
            return

        self._mode = "edit"; self._edit_id = _id
        self.cmb_customer.clear()
        for c in RC.list_customers():
            self.cmb_customer.addItem(c.name, str(c._id))

        self.cmb_printer.clear()
        for p in RPR.list_printers():
            self.cmb_printer.addItem(p.name, str(p._id))

        self.list_publications.clear()
        for pub in RP.list_publications():
            it = QListWidgetItem(pub.title)
            it.setData(Qt.ItemDataRole.UserRole, str(pub._id))
            it.setSelected(str(pub._id) in order.publication_ids)
            self.list_publications.addItem(it)

        self.inp_number.setText(order.order_number)
        self.inp_product.setText(order.product_type)
        self.chk_completed.setChecked(order.is_completed)

        idx = self.cmb_customer.findData(order.customer_id)
        self.cmb_customer.setCurrentIndex(idx if idx >= 0 else 0)

        idx = self.cmb_printer.findData(order.printer_id)
        self.cmb_printer.setCurrentIndex(idx if idx >= 0 else 0)

        self.date_received.setDate(QDate(order.date_received.year, order.date_received.month, order.date_received.day))
        if order.date_completed:
            self.date_completed.setDate(
                QDate(order.date_completed.year, order.date_completed.month, order.date_completed.day))

        self.form_box.setTitle("Редагувати замовлення")
        self.form_box.setVisible(True)

    def cancel_form(self):
        self.form_box.setVisible(False)
        self._mode = None; self._edit_id = None

    def save_form(self):
        d_received = self.date_received.date().toPyDate()
        d_completed = self.date_completed.date().toPyDate()

        if d_completed < d_received:
            QMessageBox.warning(self, "Помилка\n", "Дата виконання не може бути раніше за дату прийому.")
            return

        try:
            order = Order(
                order_number=self.inp_number.text().strip(),
                customer_id=self.cmb_customer.currentData(),
                product_type=self.inp_product.text().strip(),
                publication_ids=self._selected_publications(),
                printer_id=self.cmb_printer.currentData(),
                date_received=self.date_received.date().toPyDate(),
                date_completed=self.date_completed.date().toPyDate(),
                is_completed=self.chk_completed.isChecked(),
                _id=self._edit_id if self._mode == "edit" else None,
            )
        except ValueError as e:
            QMessageBox.warning(self, "Помилка валідації", str(e))
            return

        try:
            if self._mode == "add":
                RO.create_order(order)
            elif self._mode == "edit" and self._edit_id:
                RO.update_order(self._edit_id, order)
            else:
                QMessageBox.warning(self, "Увага", "Невідомий режим.")
                return
            self.reload()
            self.cancel_form()

            mw = self.window()
            if hasattr(mw, "publications_tab"):
                mw.publications_tab.reload()

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Операція не виконана:\n{e}")

    def delete_selected(self):
        _id = self._selected_id()
        if not _id:
            QMessageBox.information(self, "Увага", "Оберіть рядок.")
            return
        if QMessageBox.question(self, "Підтвердження", "Видалити замовлення?") == QMessageBox.StandardButton.Yes:
            try:
                RO.delete_order(_id)
                self.reload()
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити:\n{e}")

    def cancel_order_dialog(self):
        _id = self._selected_id()
        if not _id:
            QMessageBox.information(self, "Увага", "Оберіть замовлення для скасування.")
            return

        dlg = CancelDialog(self)
        if dlg.exec():
            reason = dlg.selected_reason()
            try:
                RO.cancel_order(_id, reason)
                QMessageBox.information(self, "OK", f"Замовлення скасовано ({reason}).")
                self.reload()
            except Exception as e:
                QMessageBox.critical(self, "Помилка", str(e))

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


