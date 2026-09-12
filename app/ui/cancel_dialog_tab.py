from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton

from app.ui.shortcuts_helper import apply_common_shortcuts

class CancelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Причина скасування")
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Оберіть причину:"))
        self.reason = QComboBox()
        self.reason.addItems(["неоплата", "відміна замовником"])
        layout.addWidget(self.reason)

        btn_ok = QPushButton("Підтвердити")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

        apply_common_shortcuts(
            self,
            help_text="Вікно вибору причини скасування:\nEnter — підтвердити\nEsc — закрити",
            on_confirm=self.accept,
            on_cancel=self.reject
        )

    def selected_reason(self):
        return self.reason.currentText()