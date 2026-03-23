import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QDialog, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import styles

COUNTDOWN_SECONDS = 10


class KeyCheckWorker(QThread):
    log      = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, hwnd: int):
        super().__init__()
        self.hwnd  = hwnd
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        try:
            from utils.game_checker import CHEAT_KEYS, send_key, KEY_DELAY, focus_cs2

            # Countdown
            for i in range(COUNTDOWN_SECONDS, 0, -1):
                if self._stop:
                    self.log.emit("Отменено.")
                    return
                self.log.emit(f"Начало через {i}...")
                time.sleep(1)

            if self._stop:
                self.log.emit("Отменено.")
                return

            self.log.emit("Захватываем фокус CS2...")
            focus_cs2(self.hwnd)
            self.log.emit("Начинаем проверку клавиш. Следите за экраном игры...\n")

            for vk, name in CHEAT_KEYS:
                if self._stop:
                    break
                self.log.emit(f"  Нажимаю: {name}")
                try:
                    send_key(self.hwnd, vk)
                except Exception as e:
                    self.log.emit(f"  [!] Ошибка {name}: {e}")
                time.sleep(KEY_DELAY)

            if not self._stop:
                self.log.emit("\nПроверка завершена.")
                self.log.emit("Если меню чита не открылось — подозрений по клавишам нет.")
            else:
                self.log.emit("\nПроверка остановлена.")
        except Exception as e:
            self.log.emit(f"\n[ОШИБКА] {e}")
        finally:
            self.finished.emit()


# ------------------------------------------------------------------
# Styled dialog helper
# ------------------------------------------------------------------

def _styled_dialog(parent, title: str, text: str, buttons) -> QDialog:
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setFixedWidth(400)
    dlg.setStyleSheet(
        f"QDialog {{ background-color: {styles.BG_MAIN}; }}"
        f"QLabel  {{ color: {styles.TEXT_PRIMARY}; font-size: 13px; }}"
        f"QPushButton {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        f"stop:0 {styles.SECONDARY},stop:1 {styles.ACCENT});"
        f" color: white; border: none; border-radius: 6px;"
        f" padding: 7px 20px; font-size: 13px; font-weight: 600; }}"
        f"QPushButton:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        f"stop:0 #9b3fd5,stop:1 {styles.ACCENT_HOVER}); }}"
        f"QPushButton[text='Нет'] {{ background: #2a1040; }}"
        f"QPushButton[text='Нет']:hover {{ background: #3a1860; }}"
    )

    vbox = QVBoxLayout(dlg)
    vbox.setContentsMargins(20, 20, 20, 16)
    vbox.setSpacing(14)

    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setAlignment(Qt.AlignLeft)
    vbox.addWidget(lbl)

    btn_box = QDialogButtonBox(buttons)
    btn_box.setStyleSheet("QDialogButtonBox { background: transparent; }")
    btn_box.accepted.connect(dlg.accept)
    btn_box.rejected.connect(dlg.reject)
    vbox.addWidget(btn_box, 0, Qt.AlignRight)

    return dlg


# ------------------------------------------------------------------

class GamePage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: KeyCheckWorker | None = None
        self._running = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        icon = QLabel("🎮")
        icon.setStyleSheet(f"color: {styles.ACCENT_LIGHT}; font-size: 24px; padding-right: 6px;")
        title = QLabel("Проверка игры")
        title.setStyleSheet(f"color: {styles.TEXT_PRIMARY}; font-size: 26px; font-weight: 700;")
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Status card
        card = QWidget()
        card.setObjectName("card")
        card.setStyleSheet(styles.CARD_STYLE)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(10)

        self.status_label = QLabel("Статус: Нажмите «Начать проверку»")
        self.status_label.setStyleSheet(f"color: {styles.TEXT_PRIMARY}; font-size: 13px;")
        card_layout.addWidget(self.status_label)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("Начать проверку")
        self.start_btn.setFixedHeight(36)
        self.start_btn.setStyleSheet(styles.ACCENT_BUTTON_STYLE)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(self._toggle)
        btn_row.addWidget(self.start_btn)
        btn_row.addStretch()
        card_layout.addLayout(btn_row)

        info = QLabel(
            "Программа последовательно нажмёт клавиши, типичные для меню чит-клиентов.\n"
            "CS2 должна быть запущена. Наблюдайте за экраном игры."
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {styles.TEXT_SECONDARY}; font-size: 12px;")
        card_layout.addWidget(info)

        layout.addWidget(card)

        log_label = QLabel("Лог проверки:")
        log_label.setStyleSheet(f"color: {styles.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(log_label)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet(
            f"background-color: {styles.BG_CARD}; border: 1px solid {styles.BORDER};"
            f" border-radius: 8px; color: {styles.TEXT_PRIMARY};"
            f" font-family: Consolas; font-size: 12px; padding: 8px;"
        )
        layout.addWidget(self.log_box, 1)

    # ------------------------------------------------------------------
    def _toggle(self):
        if self._running:
            self._stop()
        else:
            self._confirm_and_start()

    def _confirm_and_start(self):
        from utils.game_checker import find_cs2_hwnd, is_cs2_running

        if not is_cs2_running():
            self.status_label.setText("Статус: Процесс игры не запущен! Ошибка: #GS")
            self.status_label.setStyleSheet(f"color: {styles.COLOR_RED}; font-size: 13px;")
            return

        hwnd = find_cs2_hwnd()
        if not hwnd:
            self.status_label.setText("Статус: Окно CS2 не найдено! Ошибка: #WND")
            self.status_label.setStyleSheet(f"color: {styles.COLOR_RED}; font-size: 13px;")
            return

        # Step 1 — confirmation dialog
        confirm = _styled_dialog(
            self,
            "Подтверждение проверки",
            f"После начала проверки через <b>{COUNTDOWN_SECONDS} секунд</b> будет "
            f"эмулировано нажатие всех клавиш.\n\n"
            f"Убедитесь, что вы зашли в CS2 и активировали окно игры!",
            QDialogButtonBox.Yes | QDialogButtonBox.No,
        )
        # rename buttons to Да/Нет
        for btn in confirm.findChildren(QPushButton):
            role = confirm.findChild(QDialogButtonBox).buttonRole(btn)
            if role == QDialogButtonBox.YesRole:
                btn.setText("Да")
            elif role == QDialogButtonBox.NoRole:
                btn.setText("Нет")

        if confirm.exec_() != QDialog.Accepted:
            return

        # Step 2 — preparation info dialog
        prep = _styled_dialog(
            self,
            "Подготовка",
            f"Проверка начнётся через <b>{COUNTDOWN_SECONDS} секунд</b>.\n\n"
            f"Пожалуйста, зайдите в CS2 и активируйте окно игры!",
            QDialogButtonBox.Ok,
        )
        prep.exec_()

        # Step 3 — start worker
        self._run_check(hwnd)

    def _run_check(self, hwnd: int):
        self._running = True
        self.start_btn.setText("Остановить")
        self.status_label.setText("Статус: Обратный отсчёт...")
        self.status_label.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-size: 13px;")
        self.log_box.clear()

        self._worker = KeyCheckWorker(hwnd)
        self._worker.log.connect(self.log_box.append)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _stop(self):
        if self._worker:
            self._worker.stop()
        self._running = False
        self.start_btn.setText("Начать проверку")
        self.status_label.setText("Статус: Остановлено")
        self.status_label.setStyleSheet(f"color: {styles.TEXT_SECONDARY}; font-size: 13px;")

    def _on_finished(self):
        self._running = False
        self.start_btn.setText("Начать проверку")
        self.status_label.setText("Статус: Завершено")
        self.status_label.setStyleSheet(f"color: {styles.COLOR_GREEN}; font-size: 13px;")
