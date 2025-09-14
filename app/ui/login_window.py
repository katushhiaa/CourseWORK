from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from ..security.auth_service import get_user, check_password, forgot_password

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

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color:#666")

        form = QFormLayout()
        form.addRow("Логін:", self.login_input)
        form.addRow("Пароль:", self.pwd_input)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(btn_login)
        root.addWidget(btn_forgot, alignment=Qt.AlignmentFlag.AlignLeft)
        root.addWidget(self.status_lbl)

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
                self, "Forgot password (демо)",
                f"Пароль для '{login}': {plain}\n\n"
            )
        else:
            QMessageBox.information(
                self, "Forgot password",
                "Пароль недоступний у відкритому вигляді. Зверніться до адміністратора."
            )
