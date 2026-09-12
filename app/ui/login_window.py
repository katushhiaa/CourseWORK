from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.security.auth_service import check_password, forgot_password, get_user
from app.ui.shortcuts_helper import apply_common_shortcuts

class LoginWindow(QWidget):
    def __init__(self, on_success=None):
        super().__init__()
        self.on_success = on_success
        self.setWindowTitle("Вхід до системи")
        self.setMinimumWidth(360)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логін")
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("Пароль")
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)

        btn_login = QPushButton("Увійти")
        btn_login.clicked.connect(self.handle_login)

        btn_forgot = QPushButton("Забули пароль?")
        btn_forgot.setFlat(True)
        btn_forgot.clicked.connect(self.handle_forgot)

        btn_register = QPushButton("Зареєструватися")
        btn_register.setFlat(True)
        btn_register.clicked.connect(self.open_register_window)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color:#666")

        form = QFormLayout()
        form.addRow("Логін:", self.login_input)
        form.addRow("Пароль:", self.pwd_input)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(btn_login)
        root.addWidget(btn_forgot, alignment=Qt.AlignmentFlag.AlignLeft)
        root.addWidget(btn_register, alignment=Qt.AlignmentFlag.AlignLeft)
        root.addWidget(self.status_lbl)

        apply_common_shortcuts(
            self,
            help_text=(
                "Вікно входу:\n"
                "F1 — допомога\n"
                "Enter — увійти в систему\n"
                "Esc — закрити вікно\n"
                "Tab / Shift+Tab — перехід між полями"
            ),
            on_confirm=self.handle_login,
            on_cancel=self.close
        )

    def handle_login(self):
        login = self.login_input.text().strip()
        pwd = self.pwd_input.text()
        if not login or not pwd:
            QMessageBox.warning(self, "Увага", "Введіть логін і пароль.")
            return

        user = get_user(login)
        if not user:
            QMessageBox.critical(self, "Помилка", "Користувача не знайдено.")
            return

        if not check_password(pwd, user):
            QMessageBox.critical(self, "Помилка", "Невірний пароль.")
            return

        role = user.get("access_right", "guest")
        self.status_lbl.setText(f"Вхід успішний. Роль: {role}")
        if self.on_success:
            self.on_success(user)

    def handle_forgot(self):
        login = self.login_input.text().strip()
        if not login:
            QMessageBox.information(self, "Підказка", "Введіть логін у поле «Логін».")
            return
        plain = forgot_password(login)
        if plain:
            QMessageBox.information(
                self,
                "Забув пароль",
                f"Пароль для '{login}': {plain}\n\n"
            )
        else:
            QMessageBox.information(
                self,
                "Forgot password",
                "Пароль переглянути неможливо, бо користувача з таким логіном не існує.",
            )

    def open_register_window(self):
        from app.ui.registration_window import RegistrationWindow
        self.register = RegistrationWindow(login_window=self)
        self.register.show()