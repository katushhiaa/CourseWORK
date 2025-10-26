from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout
)
from ..security.auth_service import create_user

class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
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
            # автоматично створюємо користувача як «гість»
            create_user(login, pwd, "guest")
            QMessageBox.information(
                self, "Успішно",
                "Реєстрація завершена! Ви увійшли як гість.\n"
                "Тепер ви можете переглядати дані та подати заявку на доступ."
            )
            self.close()
        except ValueError as e:
            QMessageBox.critical(self, "Помилка", str(e))