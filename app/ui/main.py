import sys
from PySide6.QtWidgets import QApplication
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.data.db import ensure_db
from app.ui.main_window import MainWindow

def main():
    setup_logging()
    ensure_db()

    app = QApplication(sys.argv)

    try:
        with open(settings.theme_qss, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception:
        pass

    w = MainWindow()
    w.resize(1200, 720)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()