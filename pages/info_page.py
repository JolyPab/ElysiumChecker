from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
import styles

DISCORD_INVITE = "https://discord.gg/elysm"   # замени на свою ссылку


class InfoPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        icon = QLabel("ℹ")
        icon.setStyleSheet(
            f"color: {styles.ACCENT_LIGHT}; font-size: 26px; padding-right: 6px;"
        )
        title = QLabel("Информация")
        title.setStyleSheet(
            f"color: {styles.TEXT_PRIMARY}; font-size: 26px; font-weight: 700;"
        )
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Card
        card = QWidget()
        card.setObjectName("card")
        card.setStyleSheet(styles.CARD_STYLE)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(14)

        # Important badge
        badge_row = QHBoxLayout()
        badge_row.setAlignment(Qt.AlignCenter)
        badge = QLabel("  Важно!  ")
        badge.setStyleSheet(
            f"background-color: {styles.BG_MAIN}; color: {styles.TEXT_PRIMARY};"
            f" border: 1px solid {styles.BORDER}; border-radius: 6px;"
            f" font-size: 13px; font-weight: 600; padding: 6px 16px;"
        )
        badge_row.addWidget(badge)
        card_layout.addLayout(badge_row)

        # Button row — Discord + Сигнатуры
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.setAlignment(Qt.AlignCenter)

        discord_btn = QPushButton("Discord сервер")
        sig_btn     = QPushButton("Сигнатуры")

        for btn in (discord_btn, sig_btn):
            btn.setStyleSheet(styles.ACCENT_BUTTON_STYLE)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            btn_row.addWidget(btn)

        discord_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(DISCORD_INVITE))
        )
        sig_btn.clicked.connect(self._open_signatures)

        card_layout.addLayout(btn_row)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(
            f"background-color: {styles.BORDER}; border: none; max-height: 1px;"
        )
        card_layout.addWidget(sep)

        # Description
        paragraphs = [
            "<b>ElysiumChecker</b> — это инструмент для проверки игроков на наличие "
            "запрещённого программного обеспечения (читов) на серверах Elysium в CS2.",

            "Программа полностью безопасна и не содержит вредоносного кода. "
            "Она предоставляет удобные и эффективные инструменты для быстрой "
            "проверки игроков, подозреваемых в использовании читов.",

            "ElysiumChecker сканирует файловую систему по базе сигнатур, проверяет "
            "Steam-аккаунт на баны, а также анализирует процесс игры и запускает "
            "специализированные утилиты для анализа.",

            "Если вы столкнулись с ошибкой — сообщите об этом администрации сервера Elysium.",
        ]

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        text_widget = QWidget()
        text_widget.setStyleSheet("background: transparent;")
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(10)

        for para in paragraphs:
            lbl = QLabel(para)
            lbl.setWordWrap(True)
            lbl.setTextFormat(Qt.RichText)
            lbl.setStyleSheet(
                f"color: {styles.TEXT_PRIMARY}; font-size: 13px;"
            )
            text_layout.addWidget(lbl)

        text_layout.addStretch()
        scroll.setWidget(text_widget)
        card_layout.addWidget(scroll)

        layout.addWidget(card, 1)

    def _open_signatures(self):
        try:
            from utils.signatures_html import open_signatures
            open_signatures()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка", str(e))
