from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QFont
import styles


class SteamLocalWorker(QThread):
    result_ready = pyqtSignal(list)
    error        = pyqtSignal(str)
    status       = pyqtSignal(str)

    def run(self):
        try:
            from utils.steam_local import find_steam_path, parse_all_accounts, enrich_accounts

            self.status.emit("Поиск установки Steam...")
            steam_path = find_steam_path()
            if not steam_path:
                self.error.emit("Steam не найден на этом ПК")
                return

            self.status.emit("Сбор аккаунтов (loginusers, userdata, реестр)...")
            accounts = parse_all_accounts(steam_path)
            if not accounts:
                self.error.emit("Аккаунты не найдены")
                return

            self.status.emit(f"Найдено {len(accounts)} аккаунтов. Загрузка профилей...")
            accounts = enrich_accounts(accounts)

            self.result_ready.emit(accounts)
        except Exception as e:
            self.error.emit(str(e))


class SteamPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: SteamLocalWorker | None = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        icon = QLabel("⚙")
        icon.setStyleSheet(f"color: {styles.ACCENT_LIGHT}; font-size: 26px; padding-right: 6px;")
        title = QLabel("Проверка стим")
        title.setStyleSheet(f"color: {styles.TEXT_PRIMARY}; font-size: 26px; font-weight: 700;")
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Control card
        ctrl_card = QWidget()
        ctrl_card.setObjectName("card")
        ctrl_card.setStyleSheet(styles.CARD_STYLE)
        ctrl_card.setFixedHeight(72)
        ctrl_layout = QHBoxLayout(ctrl_card)
        ctrl_layout.setContentsMargins(16, 12, 16, 12)
        ctrl_layout.setSpacing(16)

        status_col = QVBoxLayout()
        status_col.setSpacing(2)
        self.status_label = QLabel("Статус: Готово к проверке")
        self.status_label.setStyleSheet(f"color: {styles.TEXT_PRIMARY}; font-size: 13px;")
        hint = QLabel("Находит все аккаунты Steam, в которые входили на этом ПК")
        hint.setStyleSheet(f"color: {styles.TEXT_SECONDARY}; font-size: 12px;")
        status_col.addWidget(self.status_label)
        status_col.addWidget(hint)

        self.check_btn = QPushButton("Проверить")
        self.check_btn.setFixedSize(120, 44)
        self.check_btn.setStyleSheet(styles.ACCENT_BUTTON_STYLE)
        self.check_btn.setCursor(Qt.PointingHandCursor)
        self.check_btn.clicked.connect(self._start_check)

        ctrl_layout.addLayout(status_col, 1)
        ctrl_layout.addWidget(self.check_btn)
        layout.addWidget(ctrl_card)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Аватар", "SteamID", "Логин", "Никнейм", "Последний вход", "VAC / Game Ban"
        ])

        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Fixed);   self.table.setColumnWidth(0, 52)
        hdr.setSectionResizeMode(1, QHeaderView.Fixed);   self.table.setColumnWidth(1, 155)
        hdr.setSectionResizeMode(2, QHeaderView.Fixed);   self.table.setColumnWidth(2, 130)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        hdr.setSectionResizeMode(4, QHeaderView.Fixed);   self.table.setColumnWidth(4, 140)
        hdr.setSectionResizeMode(5, QHeaderView.Fixed);   self.table.setColumnWidth(5, 200)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(
            f"QTableWidget {{ background-color: {styles.BG_CARD};"
            f" border: 1px solid {styles.BORDER}; border-radius: 8px; }}"
        )
        layout.addWidget(self.table, 1)

    # ------------------------------------------------------------------
    def _start_check(self):
        self.table.setRowCount(0)
        self.check_btn.setEnabled(False)
        self.status_label.setStyleSheet(f"color: {styles.TEXT_PRIMARY}; font-size: 13px;")
        self.status_label.setText("Статус: Сканирование...")

        self._worker = SteamLocalWorker()
        self._worker.status.connect(lambda s: self.status_label.setText(f"Статус: {s}"))
        self._worker.result_ready.connect(self._on_result)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_result(self, accounts: list):
        self.check_btn.setEnabled(True)
        self.status_label.setText(f"Статус: Готово! Проверено {len(accounts)} аккаунтов.")

        self.table.setRowCount(len(accounts))
        for row_idx, acc in enumerate(accounts):
            self.table.setRowHeight(row_idx, 50)

            # Avatar
            avatar_lbl = QLabel()
            avatar_lbl.setAlignment(Qt.AlignCenter)
            if acc.get("avatar"):
                pix = QPixmap()
                pix.loadFromData(acc["avatar"])
                pix = pix.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                avatar_lbl.setPixmap(pix)
            else:
                avatar_lbl.setText("?")
                avatar_lbl.setStyleSheet(f"color: {styles.TEXT_MUTED}; font-size: 18px;")
            self.table.setCellWidget(row_idx, 0, avatar_lbl)

            # SteamID
            item = QTableWidgetItem(acc["steamid"])
            item.setForeground(QColor(styles.TEXT_SECONDARY))
            item.setFont(QFont("Consolas", 11))
            self.table.setItem(row_idx, 1, item)

            # Login name
            item = QTableWidgetItem(acc["account_name"] or "—")
            item.setForeground(QColor(styles.ACCENT_LIGHT))
            self.table.setItem(row_idx, 2, item)

            # Persona name
            item = QTableWidgetItem(acc["persona_name"] or "Неизвестно")
            item.setForeground(QColor(styles.TEXT_PRIMARY))
            self.table.setItem(row_idx, 3, item)

            # Last login (★ = текущий аккаунт)
            last_text = acc["last_login"] + ("  ★" if acc["most_recent"] else "")
            item = QTableWidgetItem(last_text)
            item.setForeground(QColor(styles.COLOR_GREEN if acc["most_recent"] else styles.TEXT_SECONDARY))
            self.table.setItem(row_idx, 4, item)

            # Ban
            item = QTableWidgetItem(acc["ban_text"])
            item.setForeground(QColor(acc["ban_color"]))
            item.setFont(QFont("Segoe UI", 11, QFont.Bold))
            self.table.setItem(row_idx, 5, item)

    def _on_error(self, msg: str):
        self.check_btn.setEnabled(True)
        self.status_label.setStyleSheet(f"color: {styles.COLOR_RED}; font-size: 13px;")
        self.status_label.setText(f"Статус: Ошибка — {msg}")
