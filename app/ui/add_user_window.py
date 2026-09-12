import sys

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QDialog,
)

from app.classes.Entity import Entity
from app.security.auth_service import create_user
from app.ui.shortcuts_helper import apply_common_shortcuts


class AddUserWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додавання користувача")
        self.setModal(True)
        self.setMinimumSize(400, 200)
        self.login = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.role = QComboBox()
        self.role.addItems(["admin", "operator", "authorized", "guest"])

        btn_add = QPushButton("Створити")
        btn_add.clicked.connect(self.handle_create)

        form = QFormLayout()
        form.addRow("Логін:", self.login)
        form.addRow("Пароль:", self.password)
        form.addRow("Роль:", self.role)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(btn_add)
        self.setLayout(layout)

        apply_common_shortcuts(
            self,
            help_text="Додавання користувача.\n "
                      "Enter — створити користувача,\n "
                      "Esc — закрити вікно.\n"
                      "Tab / Shift+Tab — перехід між полями",
            on_confirm=self.handle_create,
            on_cancel = self.close
        )

    def handle_create(self):
        login = self.login.text().strip()
        password = self.password.text().strip()
        role = self.role.currentText()

        if not login or not password or not role:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля.")
            return

        try:
            login = Entity.validate_required(login,"Логін")
            password = Entity.validate_password_strength(password,"Пароль")
        except ValueError as e:
            QMessageBox.warning(self, "Помилка", str(e))
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
