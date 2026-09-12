from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QTableWidget,
    QTableWidgetItem, QLabel, QPushButton, QDateEdit, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from app.repositories import main_repo as AR
from app.db import db


class AnalyticsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_results = None
        root = QHBoxLayout()

        self.query_list = QListWidget()
        self.query_list.addItems([
            "1. Автори, книги яких найчастіше друкуються за кварталами",
            "2. Поточні замовлення",
            "3. Загальний обсяг роздрукованої продукції в друкованих аркушах за квартали",
            "4. Найбільш завантажені друкарні по місяцях",
            "5. Кількість замовлень за певний період часу",
            "6. Замовлення за різними видами видавничої продукції",
            "7. Замовлення за авторами",
            "8. Скасовані замовлення",
            "9. Замовлення приватних осіб / організацій",
            "10. Прибуток видавництва за місяць"
        ])
        root.addWidget(self.query_list, 2)

        self.results_table = QTableWidget()
        root.addWidget(self.results_table, 6)

        top_bar = QHBoxLayout()
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_from.setDate(QDate.currentDate().addMonths(-3))
        self.date_to = QDateEdit(calendarPopup=True)
        self.date_to.setDate(QDate.currentDate())

        self.btn_save = QPushButton("Зберегти результати аналітики")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_results)

        top_bar.addWidget(QLabel("З:"))
        top_bar.addWidget(self.date_from)
        top_bar.addWidget(QLabel("По:"))
        top_bar.addWidget(self.date_to)
        top_bar.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addLayout(root)
        self.setStyleSheet("""
            QWidget {
                background-color: #1f1f1f;
                color: #ddd;
                font-size: 13px;
            }
            QDateEdit {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 6px;
                color: #ddd;
            }
            QLabel {
                color: #bbb;
            }
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 6px;
                color: #ccc;
                padding: 4px;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #575757;
                color: #fff;
            }
            QTableWidget {
                background-color: #242424;
                color: #ddd;
                gridline-color: #444;
                border: 1px solid #444;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: #ccc;
                padding: 6px;
                border: none;
            }
            QPushButton {
                background-color: #444;
                color: #ddd;
                border-radius: 6px;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)

        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        self.query_list.setSpacing(4)
        self.results_table.setShowGrid(True)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.setLayout(layout)
        self.query_list.itemClicked.connect(self.run_selected_query)

    def run_selected_query(self):
        idx = self.query_list.currentRow()
        if idx < 0:
            QMessageBox.information(self, "Увага", "Оберіть запит із переліку.")
            return

        try:
            results, headers = self.execute_query_by_index(idx)
            if results and headers:
                self.display_results(headers, results)
                self.last_results = {
                    "query_index": idx + 1,
                    "headers": headers,
                    "data": results,
                    "executed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            self.btn_save.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def execute_query_by_index(self, idx: int):
        match idx:
            case 0:
                data = AR.author_top_by_quarter()
                headers = ["Автор", "Рік", "Квартал", "Кількість замовлень"]
                rows = [
                    [d["_id"].get("author"), d["_id"].get("y"), d["_id"].get("q"), d.get("orders_count", 0)]
                    for d in data if d.get("_id")
                ]

            case 1:
                data = AR.current_orders()
                cust_map = {str(c["_id"]): c.get("name", "") for c in AR.CUSTOMERS.find({})}
                headers = ["Номер", "Замовник", "Дата прийому", "Виконано"]
                rows = [
                    [
                        o.get("order_number", ""),
                        cust_map.get(str(o.get("customer_id")), ""),
                        str(o.get("date_received"))[:10] if o.get("date_received") else "",
                        "Так" if o.get("is_completed") else "Ні"
                    ]
                    for o in data if o.get("order_number")
                ]

            case 2:
                data = AR.total_sheet_volume_by_quarter()
                headers = ["Рік", "Квартал", "Загальний обсяг"]
                rows = [
                    [d["_id"].get("y"), d["_id"].get("q"), d.get("total_volume", 0)]
                    for d in data if d.get("total_volume", 0) > 0
                ]

            case 3:
                data = AR.busiest_printers_by_month()
                headers = ["Друкарня", "Рік", "Місяць", "Кількість замовлень"]
                rows = [
                    [d.get("printer", ""), d.get("year"), d.get("month"), d.get("orders_count", 0)]
                    for d in data if d.get("orders_count", 0) > 0
                ]

            case 4:
                start = self.date_from.date().toPyDate()
                end = self.date_to.date().toPyDate()
                data = AR.orders_in_period(start, end)
                headers = ["ID", "Номер", "Дата прийому"]
                rows = [
                    [str(o.get("_id")), o.get("order_number", ""), str(o.get("date_received"))[:10]]
                    for o in data["items"] if o.get("order_number")
                ]
                rows.append(["", "Всього:", data["total"]])

            case 5:
                data = AR.orders_by_product_type()
                headers = ["Тип продукції", "Кількість"]
                rows = [[d.get("_id", ""), d.get("count", 0)] for d in data if d.get("count", 0) > 0]

            case 6:
                sample_author = AR.AUTHORS.find_one()
                if not sample_author:
                    raise ValueError("У базі немає авторів.")

                author_name = sample_author.get("full_name", "Невідомий автор")
                data = AR.orders_by_author(str(sample_author["_id"]))

                if not data["items"]:
                    QMessageBox.information(self, "Результат", f"Для автора {author_name} немає замовлень.")
                    return [], []

                headers = ["Автор", "ID", "Номер замовлення", "Назви публікацій", "Дата прийому", "Виконано"]
                rows = [
                    [
                        author_name,
                        str(o.get("_id")),
                        o.get("order_number", ""),
                        ", ".join(o.get("publications_titles", [])),
                        str(o.get("date_received"))[:10] if o.get("date_received") else "",
                        "Так" if o.get("is_completed") else "Ні"
                    ]
                    for o in data["items"] if o.get("order_number")
                ]
                rows.append(["", "", "Всього:", data["total"], "", ""])

            case 7:
                data = AR.canceled_orders_breakdown()
                headers = ["Статус", "Кількість"]
                rows = [[d.get("_id", ""), d.get("count", 0)] for d in data["breakdown"] if d.get("count", 0) > 0]

            case 8:
                data = AR.orders_by_customer_type()
                headers = ["Тип замовника", "Кількість"]
                rows = [[d.get("type", ""), d.get("count", 0)] for d in data if d.get("count", 0) > 0]

            case 9:
                now = datetime.now()
                data = AR.profit_by_month(now.year, now.month)
                headers = ["Місяць", "Прибуток (грн)", "Кількість замовлень"]
                rows = [[f"{now.month}.{now.year}", data.get("profit", 0.0), len(data.get("orders", []))]]

            case _:
                raise ValueError("Невідомий індекс запиту.")

        rows = [r for r in rows if any(v not in (None, "", [], {}) for v in r)]

        if not rows:
            QMessageBox.information(self, "Результат", "Немає даних для відображення.")
            return [], headers

        return rows, headers

    def display_results(self, headers, data):
        self.results_table.clear()
        self.results_table.setColumnCount(len(headers))
        self.results_table.setRowCount(len(data))
        self.results_table.setHorizontalHeaderLabels(headers)

        for r, row in enumerate(data):
            for c, val in enumerate(row):
                self.results_table.setItem(r, c, QTableWidgetItem(str(val)))

        self.results_table.resizeColumnsToContents()

    def save_results(self):
        if not self.last_results:
            QMessageBox.warning(self, "Немає даних", "Спочатку виконайте аналітику.")
            return

        try:
            db["saved_analytics"].insert_one(self.last_results)
            QMessageBox.information(self, "Збережено", "Результати аналітики успішно збережено.")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти: {e}")

    def on_enter(self):
        if self.query_list.hasFocus() or self.date_from.hasFocus() or self.date_to.hasFocus():
            self.run_selected_query()
            return

        if self.btn_save.isEnabled() and self.results_table.rowCount() > 0:
            self.save_results()
            return

        QMessageBox.information(self, "Увага", "Оберіть запит або виконайте аналітику.")

    def on_escape(self):
        self.query_list.clearSelection()
        self.results_table.clear()
        self.btn_save.setEnabled(False)