from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)
from app.ui.add_user_window import AddUserWindow
from app.ui.authors_tab import AuthorsTab
from app.ui.customers_tab import CustomersTab
from app.ui.printers_tab import PrintersTab
from app.ui.publications_window import PublicationsTab
from app.ui.orders_tab import OrdersTab
from app.ui.analytics_tab import AnalyticsTab


class MainWindow(QMainWindow):
    def __init__(self, current_user: dict):
        super().__init__()
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

        # === 🟪 Панель користувача (вітання + “Додати користувача”) ===
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

        # === 🟨 Вкладки ===
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

        # --- вкладки
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

        # --- Порожня вкладка для майбутньої аналітики
        self.analytics_tab = AnalyticsTab(self)
        self.tabs.addTab(self.analytics_tab, "Аналітика")

        # === 🟩 Головний контейнер ===
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addWidget(user_panel)
        layout.addWidget(self.tabs)
        self.setCentralWidget(central)

        # === 🟫 Статусбар ===
        self.statusBar().setStyleSheet("background-color: #1b1b1b; color: #aaa;")
        self.statusBar().showMessage(
            f"Користувач: {self.current_user['login']} ({self.current_user['access_right']})"
        )

        # застосувати права доступу
        self.apply_permission()

    def open_add_user(self):
        dialog = AddUserWindow(self)
        dialog.exec()

    def handle_logout(self):
        """Закриває головне вікно та повертає користувача на екран логіну."""
        from app.ui.login_window import LoginWindow
        from app.main import on_login_success
        self.close()
        self.login_window = LoginWindow(on_success=lambda u: on_login_success(u, self.login_window))
        self.login_window.show()

    def reopen_main_window(self, user):
        """Перезапускає головне вікно після повторного входу."""
        self.login_window.close()
        new_main = MainWindow(user)
        new_main.show()

    def apply_permission(self):
        role = self.current_user.get("access_right", "guest").lower()
        can_edit = role in ("admin", "operator")

        # Автори
        self.authors_tab.btn_add.setEnabled(can_edit)
        self.authors_tab.btn_edit.setEnabled(can_edit)
        self.authors_tab.btn_del.setEnabled(can_edit)

        # Замовники
        self.customer_tab.btn_add.setEnabled(can_edit)
        self.customer_tab.btn_edit.setEnabled(can_edit)
        self.customer_tab.btn_del.setEnabled(can_edit)

        # Видання
        self.publications_tab.btn_add.setEnabled(can_edit)
        self.publications_tab.btn_edit.setEnabled(can_edit)
        self.publications_tab.btn_del.setEnabled(can_edit)

        # Друкарні
        self.printers_tab.btn_add.setEnabled(can_edit)
        self.printers_tab.btn_edit.setEnabled(can_edit)
        self.printers_tab.btn_del.setEnabled(can_edit)

        #Замовлення
        self.orders_tab.btn_add.setEnabled(can_edit)
        self.orders_tab.btn_edit.setEnabled(can_edit)
        self.orders_tab.btn_del.setEnabled(can_edit)