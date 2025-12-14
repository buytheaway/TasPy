from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.core.config import AppConfig
from app.core.logging_config import setup_logging
from .main_window import MainWindow


def load_stylesheet(app: QApplication, config: AppConfig) -> None:
    qss_path: Path = config.theme_qss
    if qss_path and qss_path.exists():
        try:
            with qss_path.open("r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception as exc:  # noqa: BLE001
            print("[TasPy] Ошибка при загрузке QSS:", exc)


def main() -> None:
    setup_logging()

    app = QApplication(sys.argv)
    config = AppConfig()

    load_stylesheet(app, config)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
