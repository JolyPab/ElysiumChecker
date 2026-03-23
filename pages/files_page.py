import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMetaObject, Q_ARG
from PyQt5.QtGui import QColor, QFont
import styles


class ScanWorker(QThread):
    progress = pyqtSignal(int, int, str)   # files, folders, current_path
    item_found = pyqtSignal(dict)
    finished = pyqtSignal(int)             # total results count

    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        from utils.file_scanner import scan_all_drives
        results = scan_all_drives(
            progress_callback=lambda f, d, p: self.progress.emit(f, d, p),
            result_callback=lambda item: self.item_found.emit(item),
            stop_event=self._stop_event,
        )
        self.finished.emit(len(results))


class FilesPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: ScanWorker | None = None
        self._scanning = False
        self._result_count = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        icon = QLabel("📄")
        icon.setStyleSheet(f"color: {styles.ACCENT_LIGHT}; font-size: 24px; padding-right: 6px;")
        title = QLabel("Проверка файлов")
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
        self.status_label = QLabel("Статус: Ожидание")
        self.status_label.setStyleSheet(f"color: {styles.TEXT_PRIMARY}; font-size: 13px;")
        self.counter_label = QLabel("")
        self.counter_label.setStyleSheet(f"color: {styles.TEXT_SECONDARY}; font-size: 12px;")
        status_col.addWidget(self.status_label)
        status_col.addWidget(self.counter_label)

        warning_lbl = QLabel("Работает в тестовом режиме. Могут быть нестабильности")
        warning_lbl.setStyleSheet(f"color: {styles.COLOR_YELLOW}; font-size: 11px;")
        warning_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        ctrl_layout.addLayout(status_col, 1)
        ctrl_layout.addWidget(warning_lbl)

        layout.addWidget(ctrl_card)

        # Buttons row
        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("Начать проверку")
        self.start_btn.setFixedHeight(36)
        self.start_btn.setStyleSheet(styles.ACCENT_BUTTON_STYLE)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self._toggle_scan)

        btn_row.addWidget(self.start_btn)
        btn_row.addStretch()

        self.found_label = QLabel("")
        self.found_label.setStyleSheet(f"color: {styles.TEXT_SECONDARY}; font-size: 12px;")
        btn_row.addWidget(self.found_label)
        layout.addLayout(btn_row)

        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Название", "Путь", "Тип", "Дата изменения"])

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 200)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 70)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 150)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet(
            f"QTableWidget {{ background-color: {styles.BG_CARD}; border: 1px solid {styles.BORDER};"
            f" border-radius: 8px; }}"
        )

        layout.addWidget(self.table, 1)

    # ------------------------------------------------------------------
    def _toggle_scan(self):
        if self._scanning:
            self._stop_scan()
        else:
            self._start_scan()

    def _start_scan(self):
        self._scanning = True
        self._result_count = 0
        self.table.setRowCount(0)
        self.start_btn.setText("Остановить")
        self.status_label.setText("Статус: Идёт сканирование...")
        self.counter_label.setText("")
        self.found_label.setText("")

        self._worker = ScanWorker()
        self._worker.progress.connect(self._on_progress)
        self._worker.item_found.connect(self._on_item_found)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _stop_scan(self):
        if self._worker:
            self._worker.stop()
        self._scanning = False
        self.start_btn.setText("Начать проверку")
        self.status_label.setText("Статус: Остановлено пользователем")

    def _on_progress(self, files: int, folders: int, path: str):
        drive = path[:3] if len(path) >= 3 else path
        self.status_label.setText(f"Статус: Идёт проверка диска {drive}")
        self.counter_label.setText(
            f"Проверено: {files:,} файлов, {folders:,} папок".replace(",", " ")
        )

    def _on_item_found(self, item: dict):
        self._result_count += 1
        self.table.setSortingEnabled(False)
        row = self.table.rowCount()
        self.table.insertRow(row)

        name_item = QTableWidgetItem(item["name"])
        name_item.setForeground(QColor(styles.TEXT_PRIMARY))
        self.table.setItem(row, 0, name_item)

        path_item = QTableWidgetItem(item["path"])
        path_item.setForeground(QColor(styles.TEXT_SECONDARY))
        self.table.setItem(row, 1, path_item)

        type_color = styles.ACCENT_LIGHT if item["type"] == "Папка" else styles.TEXT_SECONDARY
        type_item = QTableWidgetItem(item["type"])
        type_item.setForeground(QColor(type_color))
        self.table.setItem(row, 2, type_item)

        date_item = QTableWidgetItem(item["date"])
        date_item.setForeground(QColor(styles.COLOR_YELLOW))
        self.table.setItem(row, 3, date_item)

        self.table.setSortingEnabled(True)
        self.found_label.setText(f"Найдено: {self._result_count}")

    def _on_finished(self, total: int):
        self._scanning = False
        self.start_btn.setText("Начать проверку")
        self.status_label.setText("Статус: Завершено")
        self.found_label.setText(f"Найдено: {total}")
