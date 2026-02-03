import sys
from PySide6 import QtWidgets

from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class TerminalWidget(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        # Set a monospaced font
        font = QFont("Courier New", 11)
        self.setFont(font)

        # Style it like a classic terminal
        self.setStyleSheet("background-color: black; color: white;")

        self.prompt = ">>> "
        self.insertPlainText(self.prompt)

    def keyPressEvent(self, event):
        # Prevent user from moving cursor or deleting text above the prompt
        cursor = self.textCursor()

        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Capture the command
            command = self.toPlainText().split("\n")[-1].replace(self.prompt, "")
            print(f"Executing: {command}")  # This is where you'd call QProcess

            self.insertPlainText("\n" + self.prompt)
            self.ensureCursorVisible()
            return  # Don't let the default Enter behavior happen

        if event.key() == Qt.Key.Key_Backspace:
            # Don't delete the prompt!
            if cursor.columnNumber() <= len(self.prompt):
                return

        super().keyPressEvent(event)


def main():
    app = QtWidgets.QApplication([])

    widget = TerminalWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
