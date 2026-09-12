from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QWidget, QMessageBox, QAbstractButton,
)
from app.ui.query_window import QueryWindow
from app.ui.add_user_window import AddUserWindow
from app.ui.authors_tab import AuthorsTab
from app.ui.customers_tab import CustomersTab
from app.ui.printers_tab import PrintersTab
from app.ui.publications_window import PublicationsTab
from app.ui.orders_tab import OrdersTab
from app.ui.analytics_tab import AnalyticsTab
from app.ui.saved_analytics_tab import SavedAnalyticsTab
from app.ui.shortcuts_helper import apply_common_shortcuts
from app.security.auth_service import request_access
from app.ui.requests_tab import RequestsTab

class MainWindow(QMainWindow):
    def __init__(self, current_user: dict, login_window=None):
        super().__init__()
        self.current_user = current_user
        self.login_window = login_window
        self.current_user = current_user
        self.setWindowTitle("Видавництво — головне вікно")
        self.resize(1100, 720)

        header = QWidget()
        header.setStyleSheet("""
            background-color: #1f1f1f;
            padding: 8px 14px;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(6, 2, 6, 2)

        title = QLabel("Система управління видавництвом")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0;")
        header_layout.addWidget(title)
        header_layout.addStretch(1)

        btn_logout = QPushButton("Вийти")
        btn_logout.clicked.connect(self.handle_logout)
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: #ddd;
                border-radius: 6px;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        header_layout.addWidget(btn_logout)

        user_panel = QWidget()
        user_panel.setStyleSheet("background-color: #242424; padding: 12px 10px 12px 10px;")
        user_layout = QHBoxLayout(user_panel)
        user_layout.setContentsMargins(4, 0, 4, 0)

        label = QLabel(
            f"Вітаємо, {self.current_user['login']}!   "
            f"Ваша роль: {self.current_user['access_right']}"
        )
        label.setStyleSheet("color: #bbb; font-size: 13px;")
        user_layout.addWidget(label)

        if self.current_user.get("access_right", "").lower() == "admin":
            btn_add_user = QPushButton("➕ Додати користувача")
            btn_add_user.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    color: #ddd;
                    border-radius: 6px;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
            """)
            btn_add_user.clicked.connect(self.open_add_user)
            user_layout.addWidget(btn_add_user)
        user_layout.addStretch(1)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #ccc;
                padding: 6px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:hover {
                background-color: #3a3a3a;
            }
            QTabBar::tab:selected {
                background-color: #575757;
                color: #fff;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 4px;
                top: -1px;
                margin-top: 10px;
            }
        """)

        self.authors_tab = AuthorsTab(self)
        self.tabs.addTab(self.authors_tab, "Автори")

        self.customer_tab = CustomersTab(self)
        self.tabs.addTab(self.customer_tab, "Замовники")

        self.publications_tab = PublicationsTab(self)
        self.tabs.addTab(self.publications_tab, "Видання")

        self.printers_tab = PrintersTab(self)
        self.tabs.addTab(self.printers_tab, "Друкарні")

        self.orders_tab = OrdersTab(self)
        self.tabs.addTab(self.orders_tab, "Замовлення")

        self.analytics_tab = AnalyticsTab(self)
        self.tabs.addTab(self.analytics_tab, "Аналітика")

        self.user_panel_layout = user_layout

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addWidget(user_panel)
        layout.addWidget(self.tabs)
        self.setCentralWidget(central)

        self.statusBar().setStyleSheet("background-color: #1b1b1b; color: #aaa;")
        self.statusBar().showMessage(
            f"Користувач: {self.current_user['login']} ({self.current_user['access_right']})"
        )

        self.apply_permission()

        apply_common_shortcuts(
            self,
            help_text=(
                "Головне вікно системи:\n"
                "F1 — допомога\n"
                "Enter — дія поточної вкладки\n"
                "Esc — скасування / вихід із форми\n"
                "Tab / Shift+Tab — стандартна навігація"
            ),
            on_confirm=self._handle_global_enter,
            on_cancel=self._handle_global_escape
        )

    def _handle_global_enter(self):
        fw = self.focusWidget()
        if isinstance(fw, QAbstractButton):
            fw.click()
            return
        current     = self.tabs.currentWidget()
        if hasattr(current, "on_enter"):
            current.on_enter()

    def _handle_global_escape(self):
        current = self.tabs.currentWidget()
        if hasattr(current, "on_escape"):
            current.on_escape()

    def refresh_current_tab(self):
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, "reload"):
            current_widget.reload()
        else:
            QMessageBox.information(self, "Оновлення", "Для цієї вкладки оновлення не передбачено.")

    def open_add_user(self):
        dialog = AddUserWindow(self)
        dialog.exec()

    def handle_logout(self):
        from app.ui.login_window import LoginWindow
        self.close()
        self.next_login = LoginWindow()
        self.next_login.on_success = lambda user, win=self.next_login: self.reopen_main_window(user, win)
        self.next_login.show()

    def reopen_main_window(self, user, login_window):
        login_window.close()
        new_main = MainWindow(user, login_window=login_window)
        new_main.show()

    def apply_permission(self):
        role = self.current_user.get("access_right", "guest").lower()
        can_edit = role in ("admin", "operator")
        can_cancel_order = role in ("admin", "operator")
        can_see_analytics = role in ("admin", "operator", "authorized")
        can_request_access = role == ("guest")

        for tab in [self.authors_tab, self.customer_tab,
                self.publications_tab, self.printers_tab,
                self.orders_tab]:
            tab.btn_add.setEnabled(can_edit)
            tab.btn_edit.setEnabled(can_edit)
            tab.btn_del.setEnabled(can_edit)

        for tab in [self.orders_tab]:
            tab.btn_cancel_order.setEnabled(can_edit)

        analytics_index = self.tabs.indexOf(self.analytics_tab)
        if not can_see_analytics:
            self.tabs.removeTab(analytics_index)

        if can_request_access:
            self.add_request_button()

        if role == "admin":
            self.requests_tab = RequestsTab(self)
            self.tabs.addTab(self.requests_tab, "Заявки")

        if role in ("admin", "operator"):
            btn_query = QPushButton("Створити власний аналітичний запит")
            btn_query.clicked.connect(self.open_query_window)
            self.user_panel_layout.addWidget(btn_query)

        if role == "authorized":
            btn_save = QPushButton("Зберегти результати аналітики")
            btn_save.setStyleSheet("""
                    QPushButton {
                        background-color: #444;
                        color: #ddd;
                        border-radius: 6px;
                        padding: 6px 10px;
                    }
                    QPushButton:hover { background-color: #5a5a5a; }
                """)
            btn_save.clicked.connect(lambda: self.analytics_tab.save_results())
            self.user_panel_layout.addWidget(btn_save)

            self.saved_tab = SavedAnalyticsTab(self)
            self.tabs.addTab(self.saved_tab, "Мої збережені результати аналітики")

    def add_request_button(self):
        btn_request = QPushButton("Подати заявку на підвищення прав доступу")
        btn_request.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    color: #ddd;
                    border-radius: 6px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
            """)
        btn_request.clicked.connect(lambda: self._send_access_request(request_access))
        user_panel = self.centralWidget().layout().itemAt(1).widget()
        layout = user_panel.layout()
        layout.addWidget(btn_request)

    def open_query_window(self):
        self.query_win = QueryWindow()
        self.query_win.show()

    def _send_access_request(self, request_access_fn):
        try:
            request_access_fn(self.current_user["login"])
            QMessageBox.information(
                self,
                "Заявку відправлено",
                "Ваша заявка на підвищення прав відправлена адміністратору."
            )
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відправити заявку: {e}")
