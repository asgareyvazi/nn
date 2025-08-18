# =========================================
# file: nikan_drill_master/main.py
# =========================================
from __future__ import annotations
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from database import init_engine_and_session, create_all_tables

APP_NAME = "Nikan Drill Master"
DB_PATH = Path.home() / ".nikan_drill_master" / "ndm.sqlite3"

def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine, SessionLocal = init_engine_and_session(f"sqlite:///{DB_PATH}")
    create_all_tables(engine)

    win = MainWindow(SessionLocal=SessionLocal, db_url=str(DB_PATH))
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

