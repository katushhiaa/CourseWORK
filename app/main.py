import sys
from PyQt6.QtWidgets import QApplication
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow
from app.security.auth_service import create_user, get_user

main_window = None

def on_login_success(user_doc: dict, login_window: LoginWindow):
    global main_window
    main_window = MainWindow(user_doc)
    main_window.show()
    login_window.close()

def main():
    if not get_user("admin"):
        create_user("admin", "Admin123!", "admin")

    app = QApplication(sys.argv)
    login = LoginWindow(on_success=lambda u: on_login_success(u, login))
    login.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
