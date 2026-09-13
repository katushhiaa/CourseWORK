import traceback
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel
)
from app.db import db
from app.ui.shortcuts_helper import apply_common_shortcuts


class QueryWindow(QWidget):
    ENTITY_RESOLVERS = (
        ("customers", "customer_id", "customer", "name"),
        ("printers", "printer_id", "printer", "name"),
        ("authors", "author_id", "author", "full_name"),
        ("publications", "publication_id", "publication", "title"),
    )
    KEYS_TO_CLEANUP = ("customer_id", "printer_id", "author_id", "publication_id", "_id")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Формуваня нового запиту для обробки та модифікації даних.")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        info_label = QLabel(
            "Введіть Python-запит до бази даних.\n"
            "Приклад:\n"
            "list(db.orders.aggregate([\n"
            "    { '$count': 'total_orders' }\n"
            "]))"
        )
        info_label.setStyleSheet("color: #aaa; font-size: 12px;")
        layout.addWidget(info_label)

        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Введіть код запиту сюди")
        self.query_input.setMaximumHeight(40)
        layout.addWidget(self.query_input)

        btn_run = QPushButton("Виконати запит")
        btn_run.clicked.connect(self.run_query)
        layout.addWidget(btn_run)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setStyleSheet("""
                   QWidget { background-color: #1e1e1e; color: #ddd; }
                   QTextEdit {
                       background-color: #262626;
                       border: 1px solid #444;
                       color: #ddd;
                       font-family: Consolas, monospace;
                       font-size: 13px;
                       border-radius: 6px;
                       padding: 6px;
                   }
                   QPushButton {
                       background-color: #444;
                       color: #ddd;
                       border-radius: 6px;
                       padding: 8px 12px;
                   }
                   QPushButton:hover {
                       background-color: #5a5a5a;
                   }
                   QTableWidget {
                       background-color: #242424;
                       color: #ddd;
                       gridline-color: #555;
                       border: 1px solid #444;
                   }
                   QHeaderView::section {
                       background-color: #2b2b2b;
                       color: #ccc;
                       border: none;
                       padding: 4px;
                   }
               """)

        apply_common_shortcuts(
            self,
            help_text="Вкладка введення власного запиту.\n"
                      "Enter — Ввести запит.\n "
                      "Esc — скасувати.\n"
                      "Tab / Shift+Tab — перехід між полями",
            on_confirm=self.run_query,
            on_cancel=self.clear_input
        )

    def _execute_user_code(self, code: str):
        safe_builtins = {
            "list": list,
            "len": len,
            "dict": dict,
            "sum": sum,
            "min": min,
            "max": max,
            "sorted": sorted,
        }
        safe_env = {"__builtins__": safe_builtins, "db": db}
        return eval(code, safe_env)

    def _enrich_row(self, row: dict) -> None:
        for coll, id_field, target_field, name_field in self.ENTITY_RESOLVERS:
            entity_id = row.get(id_field)
            if not entity_id:
                continue
            entity = db[coll].find_one({"_id": entity_id})
            if entity and name_field in entity:
                row[target_field] = entity[name_field]

        for key in self.KEYS_TO_CLEANUP:
            row.pop(key, None)

    def _render_table(self, result: list) -> None:
        headers = sorted(result[0].keys())
        self.table.setColumnCount(len(headers))
        self.table.setRowCount(len(result))
        self.table.setHorizontalHeaderLabels(headers)

        for r, row in enumerate(result):
            for c, key in enumerate(headers):
                self.table.setItem(r, c, QTableWidgetItem(str(row.get(key, ""))))

        self.table.resizeColumnsToContents()

    def run_query(self):
        code = self.query_input.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "Порожньо", "Введіть код запиту.")
            return

        try:
            result = self._execute_user_code(code)
            if not isinstance(result, list):
                QMessageBox.information(self, "Результат", str(result))
                return

            if not result:
                QMessageBox.information(self, "Результат", "Дані не знайдено.")
                self.table.clear()
                return

            for row in result:
                self._enrich_row(row)

            self._render_table(result)

        except Exception as e:
            err = traceback.format_exc()
            QMessageBox.critical(self, "Помилка виконання", f"{type(e).__name__}: {e}\n\n{err}")

    def clear_input(self):
        self.query_input.clear()
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)