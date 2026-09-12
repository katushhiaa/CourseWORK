from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QMessageBox, QFormLayout
)
from app.classes.Entity import Entity
from app.security.auth_service import create_user
from app.db import db
from app.ui.shortcuts_helper import apply_common_shortcuts

class RegistrationWindow(QWidget):
    def __init__(self, login_window = None):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("Реєстрація користувача")
        self.setMinimumWidth(380)
        
        self.login_input = QLineEdit()
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        form = QFormLayout()
        form.addRow("Логін:", self.login_input)
        form.addRow("Пароль:", self.pwd_input)
        form.addRow("Підтвердіть пароль:", self.confirm_input)

        btn_register = QPushButton("Зареєструватися")
        btn_register.clicked.connect(self.handle_register)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addWidget(btn_register)

        apply_common_shortcuts(
            self,
            help_text=(
                "Вікно реєстрації користувача:\n"
                "F1 - допомога\n"
                "Enter - підтвердити реєстрацію\n"
                "Esc - закрити вікно\n"
                "Tab / Shift+Tab - перехід між полями"
            ),
            on_confirm=self.handle_register,
            on_cancel=self.close
        )

    def handle_register(self):
        login = self.login_input.text().strip()
        pwd = self.pwd_input.text()
        confirm = self.confirm_input.text()

        if not login or not pwd or not confirm:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля.")
            return

        if pwd != confirm:
            QMessageBox.warning(self, "Помилка", "Паролі не співпадають.")
            return

        try:
            login = Entity.validate_required(login, "Логін")
            pwd = Entity.validate_password_strength(pwd, "Пароль")
        except ValueError as e:
            QMessageBox.warning(self, "Помилка", str(e))
            return

        try:
            from app.ui.main_window import MainWindow
            create_user(login, pwd, "guest")
            QMessageBox.information(
                self, "Успішно",
                "Реєстрація завершена! Ви увійшли як гість.\n"
                "Тепер ви можете переглядати дані та подати заявку на доступ."
            )

            user_doc = db["keys"].find_one({"login": login})
            self.main = MainWindow(user_doc)
            self.main.show()

            self.close()

            if self.login_window:
                self.login_window.close()

        except ValueError as e:
            QMessageBox.critical(self, "Помилка", str(e))