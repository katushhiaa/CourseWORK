import sys

from PyQt6.QtWidgets import QApplication

from app.security.auth_service import create_user, get_user
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow

main_window = None

def on_login_success(user_doc, login_window):
    main = MainWindow(user_doc, login_window=login_window)
    login_window.close()
    main.show()


def main():
    app = QApplication(sys.argv)

    def open_login():
        login_window = LoginWindow()
        login_window.on_success = lambda user, win=login_window: on_login_success(user, win)
        login_window.show()

    open_login()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
