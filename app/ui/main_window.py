from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox, QHBoxLayout, QTabWidget
from app.ui.add_user_window import AddUserWindow
from app.ui.authors_tab import AuthorsTab
from app.ui.customers_tab import CustomersTab

class MainWindow(QMainWindow):
    def __init__(self, current_user: dict):
        super().__init__()
        self.current_user = current_user
        self.setWindowTitle("Видавництво — головне вікно")
        self.resize(1000, 700)

        # --- вкладки
        self.tabs = QTabWidget()
        self.authors_tab = AuthorsTab(self)
        self.tabs.addTab(self.authors_tab, "Автори")

        self.customer_tab = CustomersTab(self)
        self.tabs.addTab(self.customer_tab, "Замовники")

        # --- верхня панель (привітання + кнопка додати користувача для admin)
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Привітання
        label = QLabel(f"Вітаємо, {self.current_user['login']}!\n"
                       f"Ваша роль: {self.current_user['access_right']}")
        header_layout.addWidget(label)

        # Кнопка "Додати користувача" (тільки для admin)
        if self.current_user.get("access_right", "").lower() == "admin":
            btn_add_user = QPushButton("➕ Додати користувача")
            btn_add_user.clicked.connect(self.open_add_user)
            header_layout.addWidget(btn_add_user)

        # --- центральний контейнер
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(header)
        layout.addWidget(self.tabs)
        self.setCentralWidget(central)

        self.apply_permission()

    def open_add_user(self):
        self.add_user_win = AddUserWindow(self)
        self.add_user_win.show()

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

