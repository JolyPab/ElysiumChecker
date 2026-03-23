import sys
import os
import ctypes

# Fix high-DPI scaling
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
import config
from main_window import MainWindow
from utils.paths import base_dir


def main():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ElysiumChecker")

    config.load()

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    icon_path = os.path.join(base_dir(), "logo.ico")
    if os.path.isfile(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
