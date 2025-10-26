import sys

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget, QDialog,
)

from app.security.auth_service import create_user


class AddUserWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додавання користувача")
        self.setModal(True)  # 🔑 робить діалог модальним
        self.setMinimumSize(400, 200)

        # Поля
        self.login = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.role = QComboBox()
        self.role.addItems(["admin", "operator", "authorized", "guest"])

        # Кнопка
        btn_add = QPushButton("Створити")
        btn_add.clicked.connect(self.handle_create)

        # Layout
        form = QFormLayout()
        form.addRow("Логін:", self.login)
        form.addRow("Пароль:", self.password)
        form.addRow("Роль:", self.role)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(btn_add)

        self.setLayout(layout)  # 🔑 головний layout

    def handle_create(self):
        login = self.login.text().strip()
        password = self.password.text().strip()
        role = self.role.currentText()

        if not login or not password or not role:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля.")
            return

        try:
            create_user(login, password, role)
            QMessageBox.information(self, "Успіх", f"Користувача '{login}' створено ({role})")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося створити користувача:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AddUserWindow()
    win.show()
    sys.exit(app.exec())
