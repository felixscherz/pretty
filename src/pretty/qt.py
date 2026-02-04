import select
import sys
import os
from threading import Thread
from PySide6 import QtWidgets

import pty
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class TerminalWidget(QPlainTextEdit):
    def __init__(self, controller_fd: int):
        super().__init__()
        # Set a monospaced font
        font = QFont("Courier New", 11)
        self.setFont(font)

        # Style it like a classic terminal
        self.setStyleSheet("background-color: black; color: white;")

        self.controller_fd = controller_fd

        self.read_thread = Thread(target=self._read_subprocess, daemon=True)
        self.read_thread.start()

    def _read_subprocess(self):
        """Called when the process has output to read"""
        while True:
            try:
                r, _, _ = select.select([self.controller_fd], [], [], 0.1)
                if r:
                    data = os.read(self.controller_fd, 1024)
                    text = data.decode("utf-8", errors="replace")
                    self.insertPlainText(text)
                    self.ensureCursorVisible()
            except OSError:
                pass

    def _on_process_finished(self, exit_code, exit_status):
        """Called when the shell process exits"""
        self.insertPlainText(f"\n[Process exited with code {exit_code}]\n")
        self.notifier.setEnabled(False)
        try:
            os.close(self.master_fd)
        except OSError:
            pass

    def keyPressEvent(self, event):
        """Handle key presses and send them to the shell process"""
        text = event.text()

        if text:
            try:
                os.write(self.controller_fd, text.encode("utf-8"))
            except OSError:
                pass
        else:
            key_mapping = {
                Qt.Key.Key_Backspace: b"\x7f",
                Qt.Key.Key_Return: b"\r",
                Qt.Key.Key_Enter: b"\r",
                Qt.Key.Key_Up: b"\x1b[A",
                Qt.Key.Key_Down: b"\x1b[B",
                Qt.Key.Key_Right: b"\x1b[C",
                Qt.Key.Key_Left: b"\x1b[D",
                Qt.Key.Key_Home: b"\x1b[H",
                Qt.Key.Key_End: b"\x1b[F",
                Qt.Key.Key_Delete: b"\x1b[3~",
            }

            if event.key() in key_mapping:
                try:
                    os.write(self.controller_fd, key_mapping[event.key()])
                except OSError:
                    pass

    def closeEvent(self, event):
        """Clean up when the widget is closed"""
        if hasattr(self, "controller_fd"):
            try:
                os.close(self.controller_fd)
            except OSError:
                pass

        super().closeEvent(event)


def main():
    # this opens a pair of file descriptors
    controller, client = pty.openpty()

    # get a new process to run bash
    pid = os.fork()

    if pid == 0:
        # child process

        os.dup2(client, 0)  # stdin
        os.dup2(client, 1)  # stdout
        os.dup2(client, 2)  # stderr
        env = os.environ.copy()
        env["PS1"] = "MY-CUSTOM-PROMPT%  "
        os.execve("/bin/zsh", ["/bin/zsh", "-f"], env)

    app = QtWidgets.QApplication([])

    widget = TerminalWidget(controller)
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
