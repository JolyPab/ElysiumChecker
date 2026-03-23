import os
import ctypes
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt
import styles
from utils.paths import tool_path

PRIMARY_TOOLS = [
    ("ShellBag",             "shellbag_analyzer_cleaner.exe"),
    ("Everything",           "Everything.exe"),
    ("LastActivityView",     "LastActivityView.exe"),
    ("BrowsingHistoryView",  "BrowsingHistoryView.exe"),
    ("USBDriveLog",          "USBDriveLog.exe"),
    ("SystemInformer",       "amd64\\SystemInformer.exe"),
]


class PrimaryCheckPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(14)

        header = QHBoxLayout()
        icon = QLabel("🔍")
        icon.setStyleSheet(f"color: {styles.ACCENT_LIGHT}; font-size: 24px; padding-right: 6px;")
        title = QLabel("Первичная проверка")
        title.setStyleSheet(f"color: {styles.TEXT_PRIMARY}; font-size: 26px; font-weight: 700;")
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        card = QWidget()
        card.setObjectName("card")
        card.setStyleSheet(styles.CARD_STYLE)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 20)
        card_layout.setSpacing(16)

        hint = QLabel("Нажмите на инструмент, чтобы запустить его")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"color: {styles.TEXT_SECONDARY}; font-size: 13px;")
        card_layout.addWidget(hint)

        grid = QGridLayout()
        grid.setSpacing(10)
        for idx, (name, exe) in enumerate(PRIMARY_TOOLS):
            row, col = divmod(idx, 3)
            btn = QPushButton(f"{idx + 1}.  {name}")
            btn.setFixedHeight(52)
            btn.setStyleSheet(styles.TOOL_BUTTON_STYLE)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, e=exe, n=name: self._launch(e, n))
            grid.addWidget(btn, row, col)

        card_layout.addLayout(grid)
        layout.addWidget(card)
        layout.addStretch()

    def _launch(self, exe: str, name: str):
        path = tool_path(exe)
        if not os.path.isfile(path):
            QMessageBox.warning(self, "Утилита не найдена",
                f"Файл не найден:\n{path}\n\nПоместите .exe в папку tools\\")
            return
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", path, None, os.path.dirname(path), 1)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запуска", str(e))
