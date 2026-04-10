import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QMovie

import styles
import config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ElysiumChecker")
        self.setFixedSize(1050, 650)
        self.setWindowFlags(Qt.Window)

        self.setStyleSheet(styles.MAIN_STYLE)
        self._nav_buttons = {}
        self._current_page = None

        self._build_ui()
        self._navigate("info")

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_sidebar())

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        self.stack = QStackedWidget()
        right.addWidget(self.stack, 1)
        right.addWidget(self._build_statusbar())

        right_widget = QWidget()
        right_widget.setLayout(right)
        layout.addWidget(right_widget, 1)

        self._add_pages()

    # ------------------------------------------------------------------
    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(styles.SIDEBAR_STYLE)

        vbox = QVBoxLayout(sidebar)
        vbox.setContentsMargins(12, 16, 12, 16)
        vbox.setSpacing(4)

        # Logo area
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(8, 0, 8, 12)
        logo_layout.setSpacing(4)

        # Icon + title row
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.setContentsMargins(0, 0, 0, 0)

        # Try logo.gif → logo.png → emoji fallback
        from utils.paths import base_dir
        base = base_dir()
        logo_icon_lbl = QLabel()
        logo_icon_lbl.setFixedSize(36, 36)
        logo_icon_lbl.setAlignment(Qt.AlignCenter)

        gif_path = os.path.join(base, "logo.gif")
        png_path = os.path.join(base, "logo.png")

        if os.path.isfile(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(36, 36))
            logo_icon_lbl.setMovie(movie)
            movie.start()
            self._logo_movie = movie          # keep reference alive
        elif os.path.isfile(png_path):
            pix = QPixmap(png_path).scaled(
                36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            logo_icon_lbl.setPixmap(pix)
        else:
            logo_icon_lbl.setText("🦋")
            logo_icon_lbl.setStyleSheet("font-size: 26px;")

        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        logo_title = QLabel("ElysiumChecker")
        logo_title.setStyleSheet(
            f"color: {styles.ACCENT_LIGHT}; font-size: 15px; font-weight: 700;"
            f" background: transparent;"
        )
        logo_subtitle = QLabel("Проверка на читы CS2")
        logo_subtitle.setStyleSheet(
            f"color: {styles.TEXT_MUTED}; font-size: 10px; background: transparent;"
        )
        text_col.addWidget(logo_title)
        text_col.addWidget(logo_subtitle)

        title_row.addWidget(logo_icon_lbl)
        title_row.addLayout(text_col)
        title_row.addStretch()
        logo_layout.addLayout(title_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {styles.BORDER}; border: none; max-height: 1px;")

        vbox.addWidget(logo_widget)
        vbox.addWidget(sep)
        vbox.addSpacing(8)

        nav_items = [
            ("info",       "  Информация"),
            ("steam",      "  Проверка стим"),
            ("files",      "  Проверка файлов"),
            ("game",       "  Проверка игры"),
            ("primary",    "  Первичная проверка"),
            ("secondary",  "  Вторичная проверка"),
            ("additional", "  Дополнительно"),
        ]

        for key, label in nav_items:
            btn = QPushButton(label)
            btn.setFixedHeight(42)
            btn.setStyleSheet(styles.NAV_BUTTON_STYLE)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._navigate(k))
            vbox.addWidget(btn)
            self._nav_buttons[key] = btn

        vbox.addStretch()

        return sidebar

    # ------------------------------------------------------------------
    def _build_statusbar(self):
        bar = QWidget()
        bar.setObjectName("statusbar")
        bar.setFixedHeight(30)
        bar.setStyleSheet(styles.STATUS_BAR_STYLE)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)

        left = QLabel(f"build_id: {config.get('build_id', '1.0.0')}")
        left.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 11px;")

        right = QLabel(f"ElysiumChecker  /  Elysium CS2")
        right.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 11px;")

        layout.addWidget(left)
        layout.addStretch()
        layout.addWidget(right)

        return bar

    # ------------------------------------------------------------------
    def _add_pages(self):
        from pages.info_page import InfoPage
        from pages.steam_page import SteamPage
        from pages.files_page import FilesPage
        from pages.game_page import GamePage
        from pages.primary_check import PrimaryCheckPage
        from pages.secondary_check import SecondaryCheckPage
        from pages.additional_check import AdditionalCheckPage

        self._pages = {
            "info":       InfoPage(),
            "steam":      SteamPage(),
            "files":      FilesPage(),
            "game":       GamePage(),
            "primary":    PrimaryCheckPage(),
            "secondary":  SecondaryCheckPage(),
            "additional": AdditionalCheckPage(),
        }
        for page in self._pages.values():
            self.stack.addWidget(page)

    # ------------------------------------------------------------------
    def _navigate(self, key: str):
        if self._current_page:
            btn = self._nav_buttons.get(self._current_page)
            if btn:
                btn.setStyleSheet(styles.NAV_BUTTON_STYLE)

        self._current_page = key
        btn = self._nav_buttons.get(key)
        if btn:
            btn.setStyleSheet(styles.NAV_BUTTON_ACTIVE_STYLE)

        page = self._pages.get(key)
        if page:
            self.stack.setCurrentWidget(page)

