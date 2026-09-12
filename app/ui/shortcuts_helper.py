from PyQt6.QtGui import QShortcut
from PyQt6.QtCore import Qt, QObject, QEvent
from PyQt6.QtWidgets import QMessageBox

class ShortcutEventFilter(QObject):
    def __init__(self, parent, on_confirm=None, on_cancel=None):
        super().__init__(parent)
        self.parent = parent
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if self.on_confirm:
                    self.on_confirm()
                    return True
            elif key == Qt.Key.Key_Escape:
                if self.on_cancel:
                    self.on_cancel()
                    return True
        return False

def apply_common_shortcuts(widget, help_text=None, on_confirm=None, on_cancel=None):
    QShortcut(Qt.Key.Key_Escape, widget, activated=on_cancel or widget.close)
    QShortcut(Qt.Key.Key_F1, widget, activated=lambda: QMessageBox.information(
        widget, "Довідка",
        help_text or (
            "F1 — допомога\n"
            "Enter — підтвердження / завершення\n"
            "Esc — скасування / закриття\n"
            "Tab — наступне поле\n"
            "Shift+Tab — попереднє поле"
        )
    ))
    if on_confirm:
        QShortcut(Qt.Key.Key_Return, widget, activated=on_confirm)
        QShortcut(Qt.Key.Key_Enter, widget, activated=on_confirm)

        event_filter = ShortcutEventFilter(widget, on_confirm, on_cancel)
        widget.installEventFilter(event_filter)

    def focusNextPrevChild(self, next: bool):
        return super(widget.__class__, self).focusNextPrevChild(next)

    widget.focusNextPrevChild = focusNextPrevChild.__get__(widget)