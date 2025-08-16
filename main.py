# File: main.py
# Purpose: App entry point. Sets up DB, applies styles, builds MainWindow with Ribbon & Project Tree.

import sys
from PySide2.QtWidgets import QApplication
from database import Database
from ui.styles import load_app_palette, apply_font_defaults
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    apply_font_defaults(app)
    load_app_palette(app, theme="dark")  # "dark" | "light"

    db = Database(db_path="nikan.db", echo=False)
    db.create_all()

    win = MainWindow(db)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
